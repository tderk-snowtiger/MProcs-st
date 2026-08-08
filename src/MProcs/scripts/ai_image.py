import os
import sys
import time
import logging
import subprocess
import glob

logging.getLogger("huggingface_hub").setLevel(logging.ERROR)

os.environ.setdefault("HF_TOKEN", "0")
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

MODELS = {
    "LCM Dreamshaper": ("SimianLuo/LCM_Dreamshaper_v7", 4, "4-step fast generation (default)"),
    "Balanced": ("nota-ai/bk-sdm-small", 15, "Lightweight general purpose"),
    "Anime": ("gsdf/Counterfeit-V2.5", 15, "Public anime / illustration style"),
}

SIZE_OPTIONS = [
    ("256x256", 256, 256),
    ("320x320", 320, 320),
    ("384x384", 384, 384),
    ("448x448", 448, 448),
    ("512x512", 512, 512),
    ("512x768", 512, 768),
    ("768x512", 768, 512),
    ("768x768", 768, 768),
    ("1024x1024", 1024, 1024),
]

def is_termux():
    if not os.path.exists('/data/data/com.termux/files/usr/bin/termux-open'):
        return False
    if os.path.exists('/etc/debian_version') or os.path.exists('/etc/lsb-release'):
        return False
    return True

def ensure_deps():
    if is_termux():
        print("\nAI image generation requires PyTorch, which is not available on Termux (Android).")
        print("Use this feature on a desktop Linux system instead.")
        return False

    deps = [
        ("torch", "torch", ["--extra-index-url", "https://download.pytorch.org/whl/cpu"]),
        ("diffusers", "diffusers", []),
        ("transformers", "transformers", []),
        ("PIL", "Pillow", []),
        ("tqdm", "tqdm", []),
        ("huggingface_hub", "huggingface-hub", []),
    ]
    missing = []
    for mod_name, pkg_name, extra_args in deps:
        try:
            __import__(mod_name)
        except ImportError:
            missing.append((mod_name, pkg_name, extra_args))

    if not missing:
        return True

    print("\n=== Missing Dependencies for AI Image Generation ===")
    for _, pkg_name, _ in missing:
        print(f"  - {pkg_name}")
    print()
    print("  1. Install dependencies (recommended)")
    print("  2. Cancel")
    resp = input("Choose (1-2): ").strip()
    if resp != "1":
        print("Cancelled.")
        return False

    for mod_name, pkg_name, extra_args in missing:
        print(f"\nInstalling {pkg_name}...", flush=True)
        cmd = [sys.executable, '-m', 'pip', 'install', pkg_name]
        cmd.extend(extra_args)
        result = subprocess.run(cmd)
        if result.returncode == 0:
            print(f"{pkg_name} installed.", flush=True)
        else:
            print(f"Failed to install {pkg_name}.", flush=True)
            resp = input("Retry with --break-system-packages? (y/N): ").strip().lower()
            if resp == "y":
                cmd = [sys.executable, '-m', 'pip', 'install', '--break-system-packages', pkg_name]
                cmd.extend(extra_args)
                result = subprocess.run(cmd)
                if result.returncode == 0:
                    print(f"{pkg_name} installed.", flush=True)
                else:
                    print(f"Still failed to install {pkg_name}.", flush=True)
                    return False
            else:
                return False

    for mod_name, pkg_name, _ in missing:
        __import__(mod_name)

    return True

CLIP_MAX_TOKENS = 77

def _pre_truncate(text):
    words = text.split()
    if len(words) <= CLIP_MAX_TOKENS - 2:
        return text
    return " ".join(words[:CLIP_MAX_TOKENS - 2])

def clean_cache(model_id):
    from huggingface_hub import constants

    model_cache = os.path.join(constants.default_cache_path, "models--" + model_id.replace("/", "--"))
    for f in glob.glob(os.path.join(model_cache, "blobs", "*.incomplete")):
        os.remove(f)
    for f in glob.glob(os.path.join(constants.default_cache_path, ".locks", "models--" + model_id.replace("/", "--"), "*.lock")):
        os.remove(f)

def run(default_prompt=""):
    if not ensure_deps():
        return

    import torch
    from tqdm import tqdm
    from diffusers import DiffusionPipeline

    save_dir = os.path.join(os.getcwd(), "ai_images")
    os.makedirs(save_dir, exist_ok=True)

    print()
    print("=== AI Image Generation ===")
    print()

    if default_prompt:
        truncated_prompt = _pre_truncate(default_prompt)
        prompt = input(f"Image prompt [Default= {truncated_prompt}]: ").strip()
        if not prompt:
            prompt = truncated_prompt
    else:
        prompt = input("Image prompt: ").strip()
    if not prompt:
        print("No prompt entered.")
        return

    print()
    print("Models:")
    model_keys = list(MODELS.keys())
    for i, name in enumerate(model_keys, 1):
        _, _, desc = MODELS[name]
        default_mark = " (default)" if i == 1 else ""
        print(f"  {i}. {name}{default_mark}")
    model_choice = input(f"Model (1-{len(model_keys)}, Enter=1): ").strip()
    if not model_choice:
        model_idx = 0
    else:
        try:
            model_idx = int(model_choice) - 1
            model_idx = max(0, min(model_idx, len(model_keys) - 1))
        except ValueError:
            model_idx = 0
    model_name = model_keys[model_idx]
    model_id, default_steps, _ = MODELS[model_name]

    steps_input = input(f"Steps (Enter={default_steps}): ").strip()
    steps = int(steps_input) if steps_input else default_steps

    guidance_input = input(f"Guidance (Enter=7.5): ").strip()
    guidance = float(guidance_input) if guidance_input else 7.5

    print()
    print("Image sizes:")
    for i, (label, w, h) in enumerate(SIZE_OPTIONS, 1):
        default_mark = " (default)" if i == 5 else ""
        print(f"  {i}. {label}{default_mark}")
    size_choice = input(f"Size (1-{len(SIZE_OPTIONS)}, Enter=5): ").strip()
    if not size_choice:
        size_idx = 4
    else:
        try:
            size_idx = int(size_choice) - 1
            size_idx = max(0, min(size_idx, len(SIZE_OPTIONS) - 1))
        except ValueError:
            size_idx = 4
    _, width, height = SIZE_OPTIONS[size_idx]

    seed_input = input(f"Seed (Enter=-1 for random): ").strip()
    seed = int(seed_input) if seed_input else -1

    print()
    print(f"Model: {model_name} ({model_id})")
    print(f"Steps: {steps}")
    print(f"Guidance: {guidance}")
    print(f"Size: {width}x{height}")
    print(f"Seed: {'random' if seed == -1 else seed}")
    print(f"Output folder: {save_dir}/")
    print()

    confirm = input("Generate? (Y/n): ").strip().lower()
    if confirm == "n":
        print("Cancelled.")
        return

    print(f"\nLoading model {model_name}...", flush=True)
    start = time.time()

    clean_cache(model_id)

    pipe = DiffusionPipeline.from_pretrained(
        model_id, safety_checker=None, requires_safety_checker=False
    )
    pipe.to("cpu")
    pipe.enable_attention_slicing()

    print(f"Model loaded in {time.time()-start:.1f}s", flush=True)

    gen = torch.Generator("cpu").manual_seed(seed) if seed != -1 else None

    bar = tqdm(total=steps, desc="Generating", unit="step")

    def cb(_, step, ___, cb_kwargs):
        bar.update(1)
        return cb_kwargs

    tokens = pipe.tokenizer(prompt, truncation=True, max_length=77, return_tensors="pt")
    truncated = pipe.tokenizer.decode(tokens.input_ids[0], skip_special_tokens=True)
    if truncated != prompt:
        print(f"Prompt truncated to {len(tokens.input_ids[0])} CLIP tokens.")
        prompt = truncated

    gen_start = time.time()
    image = pipe(
        prompt,
        num_inference_steps=steps,
        guidance_scale=guidance,
        width=width,
        height=height,
        generator=gen,
        callback_on_step_end=cb,
    ).images[0]
    bar.close()
    gen_time = time.time() - gen_start

    timestamp = int(time.time())
    filename = f"ai_image_{timestamp}.png"
    filepath = os.path.join(save_dir, filename)
    image.save(filepath)

    print()
    print(f"Prompt: {prompt}")
    print(f"Generated in {gen_time:.1f}s")
    print(f"Saved: {filepath}")
    print(f"file://{filepath}")


if __name__ == "__main__":
    run()
