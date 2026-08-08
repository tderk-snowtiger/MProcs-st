import os
import sys
import json
import platform
import requests
import subprocess
import webbrowser

def get_system():
    return platform.system()

def is_android():
    return os.path.exists('/data/data/com.termux/files/usr/bin/termux-open') or os.path.exists('/system/bin/am')

def is_wsl():
    return os.path.exists('/proc/version') and 'microsoft' in open('/proc/version').read().lower()

def cmd_exists(cmd):
    return subprocess.run(['which', cmd], capture_output=True).returncode == 0

def run_cmd(*args, **kwargs):
    kwargs.setdefault('capture_output', True)
    kwargs.setdefault('text', True)
    return subprocess.run(args, **kwargs)

def _get_display_env():
    import re
    if os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY'):
        return
    if os.path.exists('/run/user/1000/wayland-0') or os.path.exists('/run/user/1000/wayland-0.lock'):
        os.environ['WAYLAND_DISPLAY'] = 'wayland-0'
        return
    result = run_cmd('pgrep', '-a', 'Xwayland')
    if result.returncode == 0 and result.stdout:
        for line in result.stdout.split('\n'):
            if 'Xwayland' in line:
                m = re.search(r':(\\d+)', line)
                if m:
                    os.environ['DISPLAY'] = ':' + m.group(1)
                    return
    if os.path.exists('/tmp/.X11-unix/X0'):
        os.environ['DISPLAY'] = ':0'

def open_url_crossplatform(url, use_w3m=True):
    if use_w3m and cmd_exists('w3m'):
        os.system(f'w3m "{url}"')
        return

    system = get_system()
    if system == 'Darwin':
        os.system(f'open "{url}"')
        return
    if system == 'Windows':
        os.system(f'start "" "{url}"')
        return
    if is_android() and (cmd_exists('termux-open') or cmd_exists('am')):
        if cmd_exists('termux-open'):
            os.system(f'termux-open "{url}"')
        else:
            os.system(f'am start -a android.intent.action.VIEW -d "{url}"')
        return
    if is_wsl():
        if cmd_exists('wslview'):
            os.system(f'wslview "{url}" &')
        else:
            os.system('cmd.exe /c start "" "' + url + '"')
        return
    _get_display_env()
    if cmd_exists('xdg-open'):
        os.system(f'xdg-open "{url}"')
        return
    if cmd_exists('firefox'):
        os.system(f'firefox "{url}"')
        return
    if cmd_exists('chromium') or cmd_exists('chromium-browser'):
        chromium = 'chromium' if cmd_exists('chromium') else 'chromium-browser'
        os.system(f'{chromium} "{url}"')
        return
    print(f"Cannot auto-open browser.")
    print(f"URL: {url}")
    print(f"System: {get_system()}, DISPLAY: {os.environ.get('DISPLAY', 'unset')}")

def download_file_crossplatform(url, filepath, show_progress=True):
    import shutil
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        with requests.get(url, headers=headers, timeout=30, stream=True, verify=False) as resp:
            resp.raise_for_status()
            total = int(resp.headers.get('content-length', 0))
            downloaded = 0
            with open(filepath, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if show_progress and total:
                            pct = (downloaded / total) * 100
                            print(f"\rDownloading: {pct:.1f}%", end='', flush=True)
            if show_progress:
                print()
            return True
    except Exception as e:
        if show_progress:
            print(f"Download error: {e}")
        return False
import time
import re
import secrets
from pathlib import Path
from urllib.parse import quote_plus, unquote_plus
import mimetypes

try:
    from requests_oauthlib import OAuth1
    OAUTH_AVAILABLE = True
except:
    OAUTH_AVAILABLE = False

def install_deps():
    """Install required dependencies with permission."""
    import subprocess

    required = ['requests']
    optional = {}  # All dependencies auto-installed when needed

    missing_req = []
    missing_opt = []

    for dep in required:
        try:
            __import__(dep)
        except ImportError:
            missing_req.append(dep)

    for dep, desc in optional.items():
        try:
            __import__(dep)
        except ImportError:
            missing_opt.append(dep)

    if not missing_req and not missing_opt:
        return

    if missing_req:
        print("\n=== Missing Dependencies ===")
        for dep in missing_req:
            print(f"  - {dep}")
        print()
        print("  1. Install dependencies (recommended)")
        print("  2. Continue without installing")
        resp = input("Choose (1-2): ").strip()
        if resp == "2":
            print("\nMissing dependencies (features limited):")
            for dep in missing_req:
                print(f"  - {dep}")
            print()
            return
        for dep in missing_req:
            print(f"Installing {dep}...")
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', dep],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                print(f"  OK: {dep}")
            else:
                print(f"  FAILED: {dep}")
                print(f"  Run manually: pip install {dep}")

    if missing_opt:
        print("\n=== Optional Dependencies ===")
        for dep in missing_opt:
            print(f"  - {dep}")
        print("\nInstall optional? [y/N]: ", end='', flush=True)
        try:
            resp = input().strip().lower()
        except:
            resp = 'n'
        if resp in ['y', 'yes']:
            for dep in missing_opt:
                print(f"Installing {dep}...")
                subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', dep],
                    capture_output=True
                )

install_deps()

import keys

def get_tumblr_status_message(result):
    """Convert Tumblr API response to human-readable message."""
    meta = result.get('meta', {})
    status = meta.get('status', 0)
    msg = meta.get('msg', '')
    
    if status == 201:
        return "Success! Post published."
    elif status == 200:
        return "Success!"
    elif status == 401:
        return "Error: Invalid or expired credentials. Re-configure your Tumblr API keys."
    elif status == 403:
        return "Error: Permission denied. Check your API permissions."
    elif status == 404:
        return "Error: Blog not found. Check your blog name."
    elif status == 429:
        return "Error: Too many requests. Wait a moment and try again."
    elif status >= 500:
        return "Error: Tumblr server issue. Try again later."
    elif msg:
        return f"Tumblr says: {msg}"
    else:
        return f"Unknown error (status: {status})"




def list_ai_texts():
    """Display list of AI-generated text from gtxt command."""
    if not ai_texts:
        print("No AI texts yet! Generate some with 'gtxt' command first.")
        return
    
    print("\n=== AI TEXT GENERATIONS ===")
    for i, t in enumerate(ai_texts[-20:], 1):  # Show last 20
        text = t.get('text', '')[:60]
        timestamp = t.get('timestamp', '')
        print(f"{i}. {text}...")
        if timestamp:
            print(f"   {timestamp}")
    print()
    return ai_texts[-20:]  # Return last 20 for selection


def export_ai_texts():
    """Export all stored AI texts to a file."""
    if not ai_texts:
        print("No AI texts to export!")
        return

    filepath = input("Export filename (default: ai_texts_export.txt): ").strip()
    if not filepath:
        filepath = "ai_texts_export.txt"

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            for i, entry in enumerate(ai_texts, 1):
                f.write(f"=== AI Text #{i} ===\n")
                f.write(f"Date: {entry.get('timestamp', 'N/A')}\n")
                f.write(f"Source: {entry.get('source', 'N/A')}\n")
                if entry.get('query'):
                    f.write(f"Prompt: {entry['query']}\n")
                if entry.get('filename'):
                    f.write(f"File: {entry['filename']}\n")
                f.write(f"\n{entry.get('text', '')}\n")
                f.write(f"{'='*60}\n\n")
        print(f"Exported {len(ai_texts)} texts to {filepath}")
    except Exception as e:
        print(f"Error exporting: {e}")


def post_image_by_number(num):
    """Post an image from cached results by number to Facebook/Tumblr."""
    if not CACHED_IMAGES:
        print("No images in cache! Search images first with 'img'.")
        return
    
    if num < 1 or num > len(CACHED_IMAGES):
        print(f"Invalid number. Choose 1-{len(CACHED_IMAGES)}")
        return
    
    img = CACHED_IMAGES[num - 1]
    url = img.get('image', '')
    title = img.get('title', f'Image {num}')
    
    if not url:
        print("No image URL found.")
        return
    
    print(f"Posting: {title}")
    print(f"URL: {url}")
    
    # Ask which platform
    print("\nPost to: 1=Facebook, 2=Tumblr, 3=Both")
    platform = input("Choose (1-3): ").strip() or "3"
    
    caption = input("Caption: ").strip()
    tags_input = input("Tags (comma): ").strip()
    tags = [t.strip() for t in tags_input.split(',')] if tags_input else None
    
    if platform in ['1', 'fb', 'facebook', '3', 'both']:
        print("\nPosting to Facebook...")
        fb_post_image_url(url, caption)
    
    if platform in ['2', 'tm', 'tumblr', '3', 'both']:
        print("\nPosting to Tumblr...")
        result = tumblr_post_photo(url, caption, tags)
        print(f"Tumblr: {get_tumblr_status_message(result)}")

def post_link_by_number(num):
    """Post a link from cached results by number to Facebook/Tumblr."""
    if not CACHED_LINKS:
        print("No links in cache! Search web first with 'web'.")
        return
    
    if num < 1 or num > len(CACHED_LINKS):
        print(f"Invalid number. Choose 1-{len(CACHED_LINKS)}")
        return
    
    link = CACHED_LINKS[num - 1]
    url = link.get('url', '')
    title = link.get('title', f'Link {num}')
    
    if not url:
        print("No URL found.")
        return
    
    print(f"Posting: {title}")
    print(f"URL: {url}")
    
    # Ask which platform
    print("\nPost to: 1=Facebook, 2=Tumblr, 3=Both")
    platform = input("Choose (1-3): ").strip() or "3"
    
    msg = input("Message: ").strip()
    
    if platform in ['1', 'fb', 'facebook', '3', 'both']:
        print("\nPosting to Facebook...")
        fb_post_link(url, msg)
    
    if platform in ['2', 'tm', 'tumblr', '3', 'both']:
        print("\nPosting to Tumblr...")
        desc = input("Tumblr description: ").strip() or msg
        tags_input = input("Tags (comma): ").strip()
        tags = [t.strip() for t in tags_input.split(',')] if tags_input else None
        result = tumblr_post_link(title, url, desc, tags)
        print(f"Tumblr: {get_tumblr_status_message(result)}")

def post_video_by_number(num):
    """Post a video from cached results by number to Facebook/Tumblr."""
    if not CACHED_VIDEOS:
        print("No videos in cache! Search YouTube first with 'yt'.")
        return
    
    if num < 1 or num > len(CACHED_VIDEOS):
        print(f"Invalid number. Choose 1-{len(CACHED_VIDEOS)}")
        return
    
    video = CACHED_VIDEOS[num - 1]
    url = video.get('url', '')
    title = video.get('title', f'Video {num}')
    
    if not url:
        print("No video URL found.")
        return
    
    print(f"Posting: {title}")
    print(f"URL: {url}")
    
    # Ask which platform
    print("\nPost to: 1=Facebook, 2=Tumblr, 3=Both")
    platform = input("Choose (1-3): ").strip() or "3"
    
    caption = input("Caption: ").strip()
    tags_input = input("Tags (comma): ").strip()
    tags = [t.strip() for t in tags_input.split(',')] if tags_input else None
    
    if platform in ['1', 'fb', 'facebook', '3', 'both']:
        print("\nPosting to Facebook...")
        fb_post_link(url, caption)
    
    if platform in ['2', 'tm', 'tumblr', '3', 'both']:
        print("\nPosting to Tumblr...")
        result = tumblr_post_video(url, caption, tags)
        print(f"Tumblr: {get_tumblr_status_message(result)}")



def post_text_interactive():
    """Post text with optional photo from URL, local file, or cached list."""
    print("\n=== Post Text ===")
    
    # Get the message
    print("\nMessage source:")
    print("  1. Type new message")
    print("  2. From AI text list (gtxt generations)")
    msg_source = input("Choose (1-2): ").strip() or "1"
    
    message = ""
    attached_image = None
    local_file = None
    
    if msg_source == "2":
        # Show AI text list and let user choose
        list_ai_texts()
        if ai_texts:
            idx = input("Choose AI text number (or Enter to type new): ").strip()
            if idx.isdigit() and 1 <= int(idx) <= len(ai_texts[-20:]):
                message = ai_texts[-20:][int(idx)-1].get('text', '')
                print(f"Using: {message[:80]}...")
                # Ask to also attach an image from cached
                if CACHED_IMAGES:
                    print(f"\nAttach image from cached? (y/n)")
                    if input("> ").strip().lower() == 'y':
                        print(f"Available images: 1-{len(CACHED_IMAGES)}")
                        img_idx = input("Image number: ").strip()
                        if img_idx.isdigit() and 1 <= int(img_idx) <= len(CACHED_IMAGES):
                            attached_image = CACHED_IMAGES[int(img_idx)-1].get('image', '')
            else:
                message = input("Enter your message: ").strip()
        else:
            print("No AI texts available! Generate some with 'gtxt' first.")
            return
    else:
        message = input("Enter your message: ").strip()
    
    if not message:
        print("No message entered!")
        return
    
    if attached_image is None:
        print("\nAttach image?")
        print("  1. None (text only)")
        print("  2. From URL")
        print("  3. From local file")
        print("  4. From cached list (searched images)")
        img_choice = input("Choose (1-4): ").strip() or "1"
        
        attached_image = None
        local_file = None
    
        if img_choice == "2":
            attached_image = input("Image URL: ").strip()
            print(f"Attached: {attached_image}")
    
        elif img_choice == "3":
            local_file = input("File path: ").strip()
            if not os.path.exists(local_file):
                print(f"File not found: {local_file}")
                return
            print(f"Attached: {local_file}")
    
        elif img_choice == "4":
            if not CACHED_IMAGES:
                print("No cached images! Search images first with 'img'")
            else:
                print(f"\nAvailable images (1-{len(CACHED_IMAGES)}):")
                for i, img in enumerate(CACHED_IMAGES[:10], 1):
                    print(f"  {i}. {img.get('title', 'Untitled')}")
                idx = input("Choose image number: ").strip()
                if idx.isdigit() and 1 <= int(idx) <= len(CACHED_IMAGES):
                    attached_image = CACHED_IMAGES[int(idx)-1].get('image', '')
                    print(f"Attached: {attached_image}")
    
    # Ask which platform
    print("\nPost to: 1=Facebook, 2=Tumblr, 3=Both")
    platform = input("Choose (1-3): ").strip() or "3"
    
    tags_input = ""
    if platform in ['2', 'tm', 'tumblr', '3', 'both']:
        tags_input = input("Tags (comma, for Tumblr): ").strip()
        tags = [t.strip() for t in tags_input.split(',')] if tags_input else None
    else:
        tags = None
    
    # Post to Facebook
    if platform in ['1', 'fb', 'facebook']:
        print("\nPosting to Facebook...")
        if local_file:
            fb_post_image_file(local_file, message)
        elif attached_image:
            fb_post_image_url(attached_image, message)
        else:
            fb_post_text(message)
    
    # Post to Tumblr
    if platform in ['2', 'tm', 'tumblr', '3', 'both']:
        print("\nPosting to Tumblr...")
        if local_file:
            result = tumblr_post_photo('', message, tags, local_file=local_file)
        elif attached_image:
            result = tumblr_post_photo(attached_image, message, tags)
        else:
            result = tumblr_post_text(message, message, tags)
        print(f"Tumblr: {get_tumblr_status_message(result)}")


def check_dependency(dep_name, install_cmd, package_name=None):
    """Check if a dependency is available, prompt to install if not."""
    package_name = package_name or dep_name
    
    if dep_name == 'requests_oauthlib':
        try:
            from requests_oauthlib import OAuth1
            return True
        except ImportError:
            pass
    elif dep_name == 'w3m':
        result = subprocess.run(['which', 'w3m'], capture_output=True)
        if result.returncode == 0:
            return True
    elif dep_name == 'tycat':
        result = subprocess.run(['which', 'tycat'], capture_output=True)
        if result.returncode == 0:
            return True
    elif dep_name == 'curl':
        result = subprocess.run(['which', 'curl'], capture_output=True)
        if result.returncode == 0:
            return True
    
    print(f"\n[Dependency Required] {package_name} is needed for this feature.")
    print(f"Install with: {install_cmd}")
    
    resp = input("Install now? (y/n): ").strip().lower()
    if resp == 'y':
        os.system(install_cmd)
        return check_dependency(dep_name, install_cmd, package_name)
    return False

CACHED_LINKS = []
CACHED_IMAGES = []
CACHED_VIDEOS = []
CACHED_POSTS = []
CACHED_TUMBLR_POSTS = []

def get_config_dir():
    """Get platform-appropriate config directory."""
    if platform.system() == 'Windows':
        base = os.environ.get('APPDATA', os.path.expanduser('~'))
        return os.path.join(base, 'scmpy')
    elif platform.system() == 'Darwin':
        return os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'scmpy')
    else:
        # Linux, WSL, Termux, etc.
        xdg = os.environ.get('XDG_CONFIG_HOME')
        if xdg:
            return os.path.join(xdg, 'scmpy')
        return os.path.expanduser('~/.config/scmpy')

def get_data_dir():
    """Get platform-appropriate data directory for downloads/outputs."""
    if platform.system() == 'Windows':
        return os.path.join(os.environ.get('USERPROFILE', os.path.expanduser('~')), 'Documents', 'scmpy')
    elif platform.system() == 'Darwin':
        return os.path.join(os.path.expanduser('~'), 'Documents', 'scmpy')
    else:
        # Use current directory or ~/scmpy for Linux/Termux
        return os.path.expanduser('~/scmpy')

# Ensure directories exist
CONFIG_DIR = get_config_dir()
DATA_DIR = get_data_dir()
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

HISTORY_FILE = os.path.join(CONFIG_DIR, 'history.json')
BACKUP_FILE = os.path.join(CONFIG_DIR, 'backup.json')
TEXT_FILE = os.path.join(DATA_DIR, 'scmpy_texts.txt')

search_history = []
post_history = []
scheduled_posts = []
ai_texts = []

def get_pollinations_key():
    return keys.get_or_prompt_key(
        'pollinations_api_key',
        'Enter Pollinations API Key (get from pollinations.ai):'
    )

def get_fb_config():
    return {
        'app_id': keys.get_or_prompt_key('fb_app_id', 'Enter Facebook App ID:'),
        'app_secret': keys.get_or_prompt_key('fb_app_secret', 'Enter Facebook App Secret:'),
        'access_token': keys.get_or_prompt_key('fb_page_access_token', 'Enter Facebook Page Access Token:')
    }

def get_tumblr_config():
    return {
        'api_key': keys.get_or_prompt_key('tumblr_api_key', 'Enter Tumblr API Key:'),
        'api_secret': keys.get_or_prompt_key('tumblr_api_secret', 'Enter Tumblr API Secret:'),
        'token': keys.get_or_prompt_key('tumblr_token', 'Enter Tumblr Access Token:'),
        'token_secret': keys.get_or_prompt_key('tumblr_token_secret', 'Enter Tumblr Token Secret:'),
        'blog': keys.get_or_prompt_key('tumblr_blog', 'Enter Tumblr Blog Name:')
    }

def open_in_browser(url):
    open_url_crossplatform(url, use_w3m=False)

def strip_html(text):
    if not text:
        return ''
    return re.sub(r'<[^>]+>', '', text)

def load_history():
    global search_history, post_history, scheduled_posts, ai_texts
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                data = json.load(f)
                search_history = data.get('searches', [])
                post_history = data.get('posts', [])
                scheduled_posts = data.get('scheduled', [])
                ai_texts = data.get('ai_texts', [])
        except:
            pass

def save_history():
    try:
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        with open(HISTORY_FILE, 'w') as f:
            json.dump({
                'searches': search_history[-50:],
                'posts': post_history[-50:],
                'scheduled': scheduled_posts,
                'ai_texts': ai_texts[-100:]
            }, f)
    except:
        pass

def get_text_file():
    return os.path.join(os.getcwd(), "scmpy_texts.txt")

def save_text_to_file(text, label=""):
    text_file = get_text_file()
    try:
        with open(text_file, 'a', encoding='utf-8') as f:
            ct = time.strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"\n--- {ct} ---\n")
            if label:
                f.write(f"[{label}]\n")
            f.write(text + "\n")
    except:
        pass

def wipe_data():
    """Clear all stored data (history, cache, AI texts, backup)."""
    print("\n=== Wipe All Data ===")
    print("This will delete all search history, post history, AI texts,")
    print("cached data, and backups.")
    resp = input("Are you sure? Type 'yes' to confirm: ").strip().lower()
    if resp != 'yes':
        print("Cancelled.")
        return

    global search_history, post_history, scheduled_posts, ai_texts
    global CACHED_LINKS, CACHED_IMAGES, CACHED_VIDEOS, CACHED_POSTS, CACHED_TUMBLR_POSTS

    search_history = []
    post_history = []
    scheduled_posts = []
    ai_texts = []
    CACHED_LINKS = []
    CACHED_IMAGES = []
    CACHED_VIDEOS = []
    CACHED_POSTS = []
    CACHED_TUMBLR_POSTS = []

    for f in [HISTORY_FILE, BACKUP_FILE, TEXT_FILE]:
        if os.path.exists(f):
            os.remove(f)
    print("All data wiped.")


def wipe_keys():
    """Delete stored API keys."""
    print("\n=== Wipe API Keys ===")
    print("This will delete all stored API keys (Facebook, Tumblr, Pollinations).")
    resp = input("Are you sure? Type 'yes' to confirm: ").strip().lower()
    if resp != 'yes':
        print("Cancelled.")
        return

    keys_file = os.path.join(CONFIG_DIR, "keys.json")
    if os.path.exists(keys_file):
        os.remove(keys_file)
        print("API keys wiped.")
    else:
        print("No API keys found.")


def backup_all_data():
    global ai_texts
    try:
        ai_texts = [h for h in search_history if h.get('source') == 'pollinations-text']
        backup_data = {
            'backup_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'search_history': search_history[-100:],
            'ai_texts': ai_texts,
            'post_history': post_history[-100:],
            'scheduled': scheduled_posts,
            'cached_links': CACHED_LINKS[:50] if CACHED_LINKS else [],
            'cached_images': CACHED_IMAGES[:50] if CACHED_IMAGES else [],
            'cached_videos': CACHED_VIDEOS[:50] if CACHED_VIDEOS else [],
        }
        os.makedirs(os.path.dirname(BACKUP_FILE), exist_ok=True)
        with open(BACKUP_FILE, 'w') as f:
            json.dump(backup_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Backup error: {e}")
        return False

def restore_from_backup():
    global search_history, post_history, scheduled_posts
    global CACHED_LINKS, CACHED_IMAGES, CACHED_VIDEOS
    try:
        if not os.path.exists(BACKUP_FILE):
            print("No backup file found!")
            return False
        with open(BACKUP_FILE, 'r') as f:
            data = json.load(f)
        search_history = data.get('search_history', [])
        post_history = data.get('post_history', [])
        scheduled_posts = data.get('scheduled', [])
        CACHED_LINKS = data.get('cached_links', [])
        CACHED_IMAGES = data.get('cached_images', [])
        CACHED_VIDEOS = data.get('cached_videos', [])
        save_history()
        print(f"Restored from backup dated {data.get('backup_date', 'unknown')}")
        return True
    except Exception as e:
        print(f"Restore error: {e}")
        return False

def search_web(query, num_results=10):
    global CACHED_LINKS
    print(f"\nSearching web for: {query}\n")
    
    url = f"https://ddg-api.herokuapp.com/search?q={quote_plus(query)}&num={num_results}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get('results', []) if isinstance(data, dict) else data
            if results:
                CACHED_LINKS = results[:num_results]
                display_links()
                return CACHED_LINKS
    except:
        pass
    
    try:
        ddg_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        resp = requests.get(ddg_url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        if resp.status_code == 200:
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, 'html.parser')
                results = []
                for result in soup.select('.result')[:num_results]:
                    title_elem = result.select_one('.result__a')
                    link_elem = result.select_one('.result__a')
                    snippet_elem = result.select_one('.result__snippet')
                    if title_elem:
                        href = title_elem.get('href', '')
                        if 'uddg=' in href:
                            from urllib.parse import unquote
                            try:
                                import re
                                real_url = re.search(r'uddg=(.*?)(?:&|$)', href)
                                if real_url:
                                    href = unquote(real_url.group(1))
                            except:
                                pass
                        results.append({
                            'title': title_elem.get_text().strip(),
                            'url': href,
                            'snippet': snippet_elem.get_text().strip() if snippet_elem else ''
                        })
                CACHED_LINKS = results
                display_links()
                return CACHED_LINKS
            except ImportError:
                pass
    except Exception as e:
        print(f"Search error: {e}")
    
    print("No results found.")
    return []

def display_links():
    print(f"=== SEARCH RESULTS ({len(CACHED_LINKS)} links) ===\n")
    for i, r in enumerate(CACHED_LINKS):
        title = r.get('title', 'No title')
        link = r.get('url', '')
        print(f"{i+1}. {title}")
        print(f"   {link[:80]}..." if len(link) > 80 else f"   {link}")
        print()

def search_images(query, num_results=10, source='flickr'):
    global CACHED_IMAGES
    print(f"\nSearching images for: {query}\n")
    
    if source == 'all':
        sources_order = ['flickr', 'picsum', 'wikimedia', 'pollinations', 'loremflickr']
    else:
        sources_order = [source]  # Just use the source user chose
    
    for src in sources_order:
        try:
            if src == 'flickr':
                url = f"https://api.flickr.com/services/feeds/photos_public.gne?tags={quote_plus(query)}&format=json&nojsoncallback=1&per_page={num_results}"
                resp = requests.get(url, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get('items', [])
                    if items:
                        results = []
                        for i, item in enumerate(items[:num_results]):
                            img_url = item.get('media', {}).get('m', '')
                            if img_url:
                                img_url = img_url.replace('_m.jpg', '_b.jpg').replace('_s.jpg', '_b.jpg')
                                title = item.get('title', f'{query} {i+1}')
                                results.append({
                                    'title': title,
                                    'image': img_url,
                                    'thumbnail': img_url.replace('_b.jpg', '_m.jpg')
                                })
                        if results:
                            CACHED_IMAGES = results[:num_results]
                            display_images()
                            return CACHED_IMAGES
            elif src == 'picsum':
                results = []
                for i in range(num_results):
                    seed = hash(f"{query}random{i}") % 10000
                    results.append({
                        'title': f'{query} {i+1}',
                        'image': f'https://picsum.photos/seed/{seed}/800/600',
                        'thumbnail': f'https://picsum.photos/seed/{seed}/200/150'
                    })
                CACHED_IMAGES = results
                print("Using Picsum")
                display_images()
                return CACHED_IMAGES
            elif src == 'wikimedia':
                url = "https://commons.wikimedia.org/w/api.php"
                headers = {'User-Agent': 'SCMPY/2.1 (Social Media CLI; mailto:kredt@localhost)'}
                params = {'action': 'query', 'list': 'search', 'srsearch': query, 'srnamespace': 6, 'srlimit': num_results, 'format': 'json'}
                try:
                    resp = requests.get(url, params=params, headers=headers, timeout=15)
                    if resp.status_code == 200:
                        data = resp.json()
                        results_data = data.get('query', {}).get('search', [])
                        if results_data:
                            results = []
                            for item in results_data[:num_results]:
                                title = item.get('title', '').replace('File:', '')
                                img_params = {'action': 'query', 'titles': f"File:{title}", 'prop': 'imageinfo', 'iiprop': 'url', 'iiurlwidth': 800, 'format': 'json'}
                                try:
                                    img_resp = requests.get(url, params=img_params, headers=headers, timeout=10)
                                    if img_resp.status_code == 200:
                                        img_data = img_resp.json()
                                        pages = img_data.get('query', {}).get('pages', {})
                                        for pid, pdata in pages.items():
                                            img_url = pdata.get('imageinfo', [{}])[0].get('thumburl', '')
                                            if img_url:
                                                results.append({'title': title, 'image': img_url, 'thumbnail': img_url.replace('/800px-', '/200px-')})
                                                break
                                except:
                                    pass
                            if results:
                                CACHED_IMAGES = results
                                print("Using Wikimedia Commons")
                                display_images()
                                return CACHED_IMAGES
                except:
                    pass

            elif src == 'pollinations':
                for i in range(num_results):
                    seed = hash(f"{query}{i}") % 1000000
                    img_url = f"https://image.pollinations.ai/prompt/{quote_plus(query)}?width=1024&height=1024&nologo=true&seed={seed}"
                    CACHED_IMAGES.append({
                        'title': f'{query} (AI) #{i+1}',
                        'image': img_url,
                        'thumbnail': img_url
                    })
                print(f"AI-generated images for '{query}'")
                display_images()
                return CACHED_IMAGES
            elif src == 'imgflip':
                # Use imgflip meme database
                url = f"https://api.imgflip.com/get_memes"
                resp = requests.get(url, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    memes = data.get('data', {}).get('memes', [])
                    if memes:
                        results = []
                        for i, meme in enumerate(memes[:num_results]):
                            results.append({
                                'title': meme.get('name', f'Meme {i+1}'),
                                'image': meme.get('url', ''),
                                'thumbnail': meme.get('box_count', '')
                            })
                        CACHED_IMAGES = results
                        print("Using Imgflip memes")
                        display_images()
                        return CACHED_IMAGES
            elif src == 'loremflickr':
                results = []
                for i in range(num_results):
                    seed = hash(f"{query}{i}") % 1000
                    results.append({
                        'title': f'{query} {i+1}',
                        'image': f'https://loremflickr.com/800/600/{quote_plus(query)}?lock={seed}',
                        'thumbnail': f'https://loremflickr.com/200/150/{quote_plus(query)}?lock={seed}'
                    })
                CACHED_IMAGES = results
                print("Using LoremFlickr")
                display_images()
                return CACHED_IMAGES
        except Exception as e:
            print(f"Error with {src}: {e}")
            continue
    
    print("No images found.")
    return []

def display_images():
    print(f"=== IMAGE RESULTS ({len(CACHED_IMAGES)} images) ===\n")
    for i, r in enumerate(CACHED_IMAGES):
        print(f"{i+1}. {r.get('title', 'No title')}")
        print(f"   {r.get('image', '')}")
        print()

def generate_text(prompt, model='openai', temperature=0.7):
    api_key = get_pollinations_key()
    print(f"\nGenerating text for: {prompt}\n")
    try:
        url = f"https://text.pollinations.ai/{quote_plus(prompt)}"
        params = {"model": model, "temperature": temperature}
        headers = {}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        resp = requests.get(url, params=params, headers=headers, timeout=60)
        if resp.status_code == 200:
            save_text_to_file(resp.text, "AI Text")
            ai_entry = {
                'query': prompt,
                'source': 'pollinations-text',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'text': resp.text[:500]
            }
            search_history.append(ai_entry)
            ai_texts.append(ai_entry)
            save_history()
            return resp.text
        else:
            print(f"Error: {resp.status_code}")
            return None
    except Exception as e:
        print(f"Error generating text: {e}")
        return None

def generate_ai_images(prompt, num=1, width=1024, height=1024, model='flux'):
    global CACHED_IMAGES, ai_texts
    api_key = get_pollinations_key()
    print(f"\nGenerating AI images for: {prompt}\n")
    results = []
    headers = {}
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    for i in range(num):
        seed = hash(f"{prompt}{i}") % 1000000
        img_url = f"https://image.pollinations.ai/prompt/{quote_plus(prompt)}?width={width}&height={height}&nologo=true&seed={seed}&model={model}"
        results.append({
            'title': f'{prompt} #{i+1}',
            'image': img_url,
            'thumbnail': img_url,
            'headers': headers
        })
    CACHED_IMAGES = results
    print(f"Generated {num} AI image(s)")
    display_images()
    return CACHED_IMAGES

def search_youtube(query, num_results=10):
    global CACHED_VIDEOS
    print(f"\nSearching YouTube for: {query}\n")
    
    # Try primary API
    url = f"https://ddg-api.herokuapp.com/youtube?q={quote_plus(query)}&num={num_results}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            results = data if isinstance(data, list) else data.get('results', [])
            if results:
                CACHED_VIDEOS = results[:num_results]
                display_videos()
                return CACHED_VIDEOS
    except:
        pass
    
    # Fallback: scrape YouTube HTML directly (like cli.py)
    try:
        yt_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
        resp = requests.get(yt_url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        if resp.status_code == 200:
            # Extract video IDs from JSON data in the page
            pattern = r'"videoId":"([a-zA-Z0-9_-]{11})"'
            video_ids = re.findall(pattern, resp.text)
            
            if not video_ids:
                print("No YouTube videos found.")
                return []
            
            # Get unique video IDs
            video_ids = list(dict.fromkeys(video_ids))[:num_results]
            
            # Try to get titles - simplified pattern
            try:
                title_pattern = r'"text":"([^"]{5,100}?)"'
                titles = re.findall(title_pattern, resp.text)
                # Filter to likely video titles
                video_titles = [t for t in titles if len(t) > 5][:num_results*2]
            except:
                video_titles = []
            
            results = []
            for i, vid in enumerate(video_ids):
                title = video_titles[i] if i < len(video_titles) else f"Video {i+1}"
                results.append({
                    'title': title,
                    'vid': vid,
                    'url': f'https://youtube.com/watch?v={vid}'
                })
            
            CACHED_VIDEOS = results
            display_videos()
            return CACHED_VIDEOS
    except Exception as e:
        print(f"YouTube search error: {e}")
    
    print("YouTube search unavailable.")
    return []

def display_videos():
    print(f"=== YOUTUBE RESULTS ({len(CACHED_VIDEOS)} videos) ===\n")
    for i, v in enumerate(CACHED_VIDEOS):
        title = v.get('title', 'No title')
        video_id = v.get('vid', v.get('videoId', ''))
        url_link = v.get('url', f'https://youtube.com/watch?v={video_id}')
        print(f"{i+1}. {title}")
        print(f"   {url_link}")
        print()
    if CACHED_VIDEOS:
        num = input(f"Open video # (1-{len(CACHED_VIDEOS)}) or Enter to skip: ").strip()
        if num.isdigit():
            idx = int(num) - 1
            if 0 <= idx < len(CACHED_VIDEOS):
                video_id = CACHED_VIDEOS[idx].get('vid', CACHED_VIDEOS[idx].get('videoId', ''))
                url = CACHED_VIDEOS[idx].get('url', f'https://youtube.com/watch?v={video_id}')
                print(f"Opening: {url}")
                open_in_browser(url)

def download_file(url, filepath, show_progress=True):
    if show_progress:
        print(f"Downloading to {filepath}...")
    return download_file_crossplatform(url, filepath, show_progress)

def unique_filename(folder, base, ext):
    counter = 1
    filename = f"{base}.{ext}"
    filepath = os.path.join(folder, filename)
    while os.path.exists(filepath):
        counter += 1
        filename = f"{base}_{counter}.{ext}"
        filepath = os.path.join(folder, filename)
    return filepath
def download_by_number(items, number, folder, is_image=False, prefix=""):
    if not items:
        print("No items to download!")
        return
    
    if number < 1 or number > len(items):
        print(f"Invalid number. Choose 1-{len(items)}")
        return
    
    item = items[number - 1]
    url = item.get('image', item.get('url', '')) if is_image else item.get('url', '')
    
    if not url:
        print("No URL found")
        return
    
    os.makedirs(folder, exist_ok=True)
    base = f"{prefix}_{number}" if prefix else f"download_{number}"
    from urllib.parse import urlparse
    parsed = urlparse(url)
    path = parsed.path
    if '.' in path and len(path.split('.')[-1]) >= 3:
        ext = path.split('.')[-1][:4].lower()
    else:
        ext = 'png'
    filepath = unique_filename(folder, base, ext)
    print(f"Downloading to {filepath}...")
    download_file(url, filepath)

def download_all_images(items, folder, prefix="img"):
    if not items:
        print("No images to download!")
        return
    os.makedirs(folder, exist_ok=True)
    print(f"Downloading {len(items)} images to {folder}...")
    for i, item in enumerate(items):
        url = item.get('image', '')
        if not url:
            continue
        from urllib.parse import urlparse
        parsed = urlparse(url)
        path = parsed.path
        if '.' in path and len(path.split('.')[-1]) >= 3:
            ext = path.split('.')[-1][:4].lower()
        else:
            ext = 'png'
        base = f"{prefix}_{i+1}"
        filepath = unique_filename(folder, base, ext)
        filename = os.path.basename(filepath)
        print(f"[{i+1}/{len(items)}] {filename}...", end=' ', flush=True)
        if download_file(url, filepath):
            print("OK")
        else:
            print("FAILED")
    print(f"Done! {len(items)} images downloaded.")

def fb_api_call(endpoint, method='GET', data=None, params=None):
    config = get_fb_config()
    token = config['access_token']
    url = f"https://graph.facebook.com/v18.0/{endpoint}"
    params = params or {}
    params['access_token'] = token
    
    if method == 'GET':
        response = requests.get(url, params=params)
    elif method == 'POST':
        response = requests.post(url, data=data, params=params)
    elif method == 'DELETE':
        response = requests.delete(url, params=params)
    
    if response.status_code >= 400:
        return {'error': {'message': f'HTTP error {response.status_code}', 'type': 'OAuthException', 'code': response.status_code}}
    try:
        return response.json()
    except:
        return {'error': {'message': 'Invalid JSON response', 'type': 'OAuthException', 'code': response.status_code}}

def fb_list_posts(limit=20):
    global CACHED_POSTS
    all_posts = []
    fetched = 0
    after = None
    
    while True:
        params = {'limit': min(limit - fetched, 100) if limit != 'all' else 100}
        if after:
            params['after'] = after
        
        data = fb_api_call('me/feed', params=params)
        new_posts = data.get('data', [])
        
        if not new_posts:
            break
            
        all_posts.extend(new_posts)
        fetched += len(new_posts)
        
        if limit != 'all' and fetched >= limit:
            break
            
        paging = data.get('paging', {})
        cursors = paging.get('cursors', {})
        after = cursors.get('after')
        
        if not after:
            break
    
    posts = all_posts[:limit] if limit != 'all' else all_posts
    CACHED_POSTS = posts
    
    for i, post in enumerate(posts):
        created = post.get('created_time', 'Unknown')
        message = post.get('message', '(No text)')[:60]
        print(f"{i+1}. [{created[:10]}] {message}...")
    
    return posts

def _confirm_post(platform):
    resp = input(f"Post to {platform}? (y/n): ").strip().lower()
    if resp != 'y':
        print("Cancelled.")
        return False
    return True

def fb_post_text(message):
    print(f"\nPosting: {message[:50]}...")
    if not _confirm_post("Facebook"):
        return
    data = fb_api_call('me/feed', method='POST', data={'message': message})
    if 'id' in data:
        print(f"Posted! Post ID: {data['id']}\n")
    else:
        print(f"Error: {data}\n")

def fb_post_link(url, message=''):
    print(f"\nPosting link: {url}")
    if not _confirm_post("Facebook"):
        return
    data = fb_api_call('me/feed', method='POST', data={'message': message, 'link': url})
    if 'id' in data:
        print(f"Posted! Post ID: {data['id']}\n")
    else:
        print(f"Error: {data}\n")

def fb_post_image_url(url, message='', _confirm=True):
    # Handle file:// URLs by converting to local file upload
    if url.startswith('file://'):
        local_file = url[7:]  # Remove 'file://' prefix
        if os.path.exists(local_file):
            return fb_post_image_file(local_file, message, _confirm=_confirm)
        else:
            print(f"Error: File not found: {local_file}")
            return
    
    print(f"\nPosting image from: {url}")
    if _confirm and not _confirm_post("Facebook"):
        return
    data = fb_api_call('me/photos', method='POST', data={'url': url, 'message': message})
    if 'id' in data:
        print(f"Image posted! Post ID: {data['id']}\n")
    else:
        print(f"Error: {data}\n")

def fb_post_image_file(filepath, message='', _confirm=True):
    print(f"\nPosting image from file: {filepath}")
    if _confirm and not _confirm_post("Facebook"):
        return
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}")
        return
    with open(filepath, 'rb') as f:
        files = {'source': f}
        config = get_fb_config()
        token = config['access_token']
        url = "https://graph.facebook.com/v18.0/me/photos"
        response = requests.post(url, files=files, data={'message': message}, params={'access_token': token})
    
    if response.status_code >= 400:
        data = {'error': {'message': f'HTTP error {response.status_code}', 'type': 'OAuthException', 'code': response.status_code}}
    else:
        try:
            data = response.json()
        except:
            data = {'error': {'message': 'Invalid JSON response', 'type': 'OAuthException', 'code': response.status_code}}
    
    if 'id' in data:
        print(f"Image posted! Post ID: {data['id']}\n")
    else:
        print(f"Error: {data}\n")

def get_tumblr_auth():
    global OAUTH_AVAILABLE
    if not OAUTH_AVAILABLE:
        if not check_dependency('requests_oauthlib', 'pip install requests-oauthlib', 'requests-oauthlib'):
            print("requests-oauthlib required for Tumblr. Install via: pip install requests-oauthlib")
            return None
        try:
            from requests_oauthlib import OAuth1 as _OAuth1
            global OAuth1
            OAuth1 = _OAuth1
            OAUTH_AVAILABLE = True
        except Exception as e:
            print(f"Failed to import OAuth1: {e}")
            return None
    if not OAUTH_AVAILABLE:
        return None
    config = get_tumblr_config()
    return OAuth1(config['api_key'], config['api_secret'], config['token'], config['token_secret'])

def tumblr_post_text(title, body, tags=None):
    print(f"\nPosting text to Tumblr: {title[:50]}...")
    if not _confirm_post("Tumblr"):
        return {'meta': {'status': 0, 'msg': 'Cancelled'}}
    auth = get_tumblr_auth()
    config = get_tumblr_config()
    tags_str = ','.join(tags) if tags else ''
    
    payload = {
        'type': 'text',
        'title': title,
        'body': body,
        'state': 'published'
    }
    if tags_str:
        payload['tags'] = tags_str
    
    url = f'https://api.tumblr.com/v2/blog/{config["blog"]}.tumblr.com/post'
    resp = requests.post(url, auth=auth, data=payload)
    if resp.status_code >= 400:
        return {'meta': {'status': resp.status_code, 'msg': f"HTTP error {resp.status_code}: {resp.text[:200]}"}}
    try:
        return resp.json()
    except:
        return {'meta': {'status': resp.status_code, 'msg': 'Invalid JSON response'}}

def tumblr_post_photo(image_url, caption, tags=None, link=None, local_file=None, _confirm=True):
    print(f"\nPosting photo to Tumblr...")
    if _confirm and not _confirm_post("Tumblr"):
        return {'meta': {'status': 0, 'msg': 'Cancelled'}}
    auth = get_tumblr_auth()
    config = get_tumblr_config()
    tags_str = ','.join(tags) if tags else ''
    
    if local_file and os.path.exists(local_file):
        with open(local_file, 'rb') as f:
            image_data = f.read()
        
        filename = os.path.basename(local_file)
        mime_type = mimetypes.guess_type(filename)[0] or 'image/jpeg'
        boundary = '---0123456789boundary'
        
        body = f'--{boundary}\r\n'
        body += 'Content-Disposition: form-data; name="type"\r\n\r\n'
        body += 'photo\r\n'
        body += f'--{boundary}\r\n'
        body += 'Content-Disposition: form-data; name="caption"\r\n\r\n'
        body += f'{caption}\r\n'
        body += f'--{boundary}\r\n'
        body += 'Content-Disposition: form-data; name="state"\r\n\r\n'
        body += 'published\r\n'
        if tags_str:
            body += f'--{boundary}\r\n'
            body += 'Content-Disposition: form-data; name="tags"\r\n\r\n'
            body += f'{tags_str}\r\n'
        if link:
            body += f'--{boundary}\r\n'
            body += 'Content-Disposition: form-data; name="click-through-url"\r\n\r\n'
            body += f'{link}\r\n'
        body += f'--{boundary}\r\n'
        body += f'Content-Disposition: form-data; name="data"; filename="{filename}"\r\n'
        body += f'Content-Type: {mime_type}\r\n\r\n'
        
        body_bytes = body.encode('utf-8') + image_data + b'\r\n'
        body_bytes += f'--{boundary}--\r\n'.encode('utf-8')
        
        headers = {
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'Content-Length': str(len(body_bytes))
        }
        
        url = f'https://api.tumblr.com/v2/blog/{config["blog"]}.tumblr.com/post'
        resp = requests.post(url, auth=auth, data=body_bytes, headers=headers)
        if resp.status_code >= 400:
            return {'meta': {'status': resp.status_code, 'msg': f'HTTP error {resp.status_code}: {resp.text[:200]}'}}
        try:
            return resp.json()
        except:
            return {'meta': {'status': resp.status_code, 'msg': 'Invalid JSON response'}}
    
    payload = {
        'type': 'photo',
        'caption': caption,
        'state': 'published'
    }
    if tags_str:
        payload['tags'] = tags_str
    if link:
        payload['click-through-url'] = link
    if image_url:
        # Handle file:// URLs by converting to local file path
        if image_url.startswith('file://'):
            local_file = image_url[7:]  # Remove 'file://' prefix
            if os.path.exists(local_file):
                # Use local file upload path (skip confirm, already asked)
                return tumblr_post_photo('', caption, tags, link=link, local_file=local_file, _confirm=False)
            else:
                return {'meta': {'status': 404, 'msg': f'File not found: {local_file}'}}
        
        # Tumblr requires file upload, not URL - download then upload
        print(f"Downloading image from {image_url}...")
        import tempfile
        import shutil
        try:
            resp = requests.get(image_url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code == 200:
                # Save to temp file
                ext = image_url.split('.')[-1].lower()[:4]
                if ext not in ['jpg', 'png', 'gif', 'jpeg']:
                    ext = 'jpg'
                temp_file = tempfile.NamedTemporaryFile(suffix=f'.{ext}', delete=False)
                temp_file.write(resp.content)
                temp_file.close()
                print(f"Uploaded temp file: {temp_file.name}")
                # Upload as file
                with open(temp_file.name, 'rb') as f:
                    files = {'data': f}
                    data = {'type': 'photo', 'caption': caption, 'state': 'published'}
                    if tags_str:
                        data['tags'] = tags_str
                    if link:
                        data['click-through-url'] = link
                    url = f'https://api.tumblr.com/v2/blog/{config["blog"]}.tumblr.com/post'
                    resp = requests.post(url, auth=auth, files=files, data=data)
                # Clean up
                try:
                    os.remove(temp_file.name)
                except:
                    pass
                if resp.status_code >= 400:
                    return {'meta': {'status': resp.status_code, 'msg': f'HTTP error {resp.status_code}: {resp.text[:200]}'}}
                try:
                    return resp.json()
                except:
                    return {'meta': {'status': resp.status_code, 'msg': 'Invalid JSON response'}}
            else:
                print(f"Failed to download image: {resp.status_code}")
        except Exception as e:
            print(f"Error downloading image: {e}")
    
    url = f'https://api.tumblr.com/v2/blog/{config["blog"]}.tumblr.com/post'
    resp = requests.post(url, auth=auth, data=payload)
    if resp.status_code >= 400:
        return {'meta': {'status': resp.status_code, 'msg': f'HTTP error {resp.status_code}: {resp.text[:200]}'}}
    try:
        return resp.json()
    except:
        return {'meta': {'status': resp.status_code, 'msg': 'Invalid JSON response'}}

def tumblr_post_link(title, url, description, tags=None):
    print(f"\nPosting link to Tumblr: {title[:50]}...")
    if not _confirm_post("Tumblr"):
        return {'meta': {'status': 0, 'msg': 'Cancelled'}}
    auth = get_tumblr_auth()
    config = get_tumblr_config()
    tags_str = ','.join(tags) if tags else ''
    
    payload = {
        'type': 'link',
        'title': title,
        'url': url,
        'description': description,
        'state': 'published'
    }
    if tags_str:
        payload['tags'] = tags_str
    
    url = f'https://api.tumblr.com/v2/blog/{config["blog"]}.tumblr.com/post'
    resp = requests.post(url, auth=auth, data=payload)
    if resp.status_code >= 400:
        return {'meta': {'status': resp.status_code, 'msg': f"HTTP error {resp.status_code}: {resp.text[:200]}"}}
    try:
        return resp.json()
    except:
        return {'meta': {'status': resp.status_code, 'msg': 'Invalid JSON response'}}

def tumblr_post_video(video_url, caption, tags=None):
    print(f"\nPosting video to Tumblr: {caption[:50]}...")
    if not _confirm_post("Tumblr"):
        return {'meta': {'status': 0, 'msg': 'Cancelled'}}
    auth = get_tumblr_auth()
    config = get_tumblr_config()
    tags_str = ','.join(tags) if tags else ''
    
    video_id = None
    if 'youtube.com/watch' in video_url:
        match = re.search(r'[?&]v=([a-zA-Z0-9_-]+)', video_url)
        if match:
            video_id = match.group(1)
    elif 'youtu.be/' in video_url:
        match = re.search(r'youtu\.be/([a-zA-Z0-9_-]+)', video_url)
        if match:
            video_id = match.group(1)
    
    embed = None
    if video_id:
        embed = f'<iframe width="500" height="281" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>'
    
    payload = {
        'type': 'video',
        'caption': caption,
        'state': 'published'
    }
    if embed:
        payload['embed'] = embed
    if tags_str:
        payload['tags'] = tags_str
    
    url = f'https://api.tumblr.com/v2/blog/{config["blog"]}.tumblr.com/post'
    resp = requests.post(url, auth=auth, data=payload)
    if resp.status_code >= 400:
        return {'meta': {'status': resp.status_code, 'msg': f"HTTP error {resp.status_code}: {resp.text[:200]}"}}
    try:
        return resp.json()
    except:
        return {'meta': {'status': resp.status_code, 'msg': 'Invalid JSON response'}}

def tumblr_get_posts(limit=20):
    auth = get_tumblr_auth()
    config = get_tumblr_config()
    url = f'https://api.tumblr.com/v2/blog/{config["blog"]}.tumblr.com/posts'
    resp = requests.get(url, auth=auth, params={'limit': limit})
    if resp.status_code >= 400:
        return {'meta': {'status': resp.status_code, 'msg': f'HTTP error {resp.status_code}'}, 'response': {'posts': []}}
    try:
        return resp.json()
    except:
        return {'meta': {'status': resp.status_code, 'msg': 'Invalid JSON response'}, 'response': {'posts': []}}

# CLI Wrapper functions
def web_search(query):
    results = search_web(query)
    display_links()

def image_search(query):
    results = search_images(query)
    display_images()

def youtube_search(query):
    results = search_youtube(query)
    display_videos()

def ai_text(prompt):
    result = generate_text(prompt)
    save_text_to_file(result, "AI")
    print(result)

def ai_image(prompt):
    urls = generate_ai_images(prompt)
    for i, url in enumerate(urls):
        print(f"{i+1}. {url}")

def list_images(path='.', add_to_cache=True, allow_upload=True):
    import os
    folder = path if path != '.' else os.getcwd()
    if not os.path.isdir(folder):
        print(f"Folder not found: {folder}")
        return
    images = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'))]
    if images:
        print(f"Images in {folder}:")
        for i, f in enumerate(images):
            print(f"  {i+1}. {f}")
        view_opt = input(f"\nView image # (1-{len(images)}), 'c' to cache, 'p' to post, or Enter to skip: ").strip()
        if view_opt.isdigit():
            i = int(view_opt) - 1
            if 0 <= i < len(images):
                filepath = os.path.abspath(os.path.join(folder, images[i]))
                view_with_w3m(f"file://{filepath}", images[i])
                CACHED_IMAGES.append({
                    'title': images[i],
                    'image': f"file://{filepath}",
                    'thumbnail': f"file://{filepath}"
                })
        elif view_opt.lower() == 'c':
            idx = input(f"Add to cache # (1-{len(images)}): ").strip()
            if idx.isdigit():
                i = int(idx) - 1
                if 0 <= i < len(images):
                    filepath = os.path.join(folder, images[i])
                    CACHED_IMAGES.append({
                        'title': images[i],
                        'image': f"file://{os.path.abspath(filepath)}",
                        'thumbnail': f"file://{os.path.abspath(filepath)}"
                    })
                    print(f"Added to cache: {images[i]}")
        elif view_opt.lower() == 'p' and allow_upload:
            img_idx = input(f"Image # (1-{len(images)}): ").strip()
            if img_idx.isdigit():
                i = int(img_idx) - 1
                if 0 <= i < len(images):
                    msg = input("Message: ").strip()
                    where = input("Post to: 1=FB, 2=Tumblr, 3=Both: ").strip() or "3"
                    fp = os.path.abspath(os.path.join(folder, images[i]))
                    if where in ('1', '3'):
                        fb_post_image_file(fp, msg)
                    if where in ('2', '3'):
                        tumblr_post_photo('', msg, tags_list=None, local_file=fp)
    else:
        print("No images found.")

def view_image(filename):
    import os
    if os.path.exists(filename):
        view_with_w3m(filename, filename)
    else:
        print(f"File not found: {filename}")

def list_videos(path='.'):
    import os
    folder = path if path != '.' else os.getcwd()
    if not os.path.isdir(folder):
        print(f"Folder not found: {folder}")
        return
    videos = [f for f in os.listdir(folder) if f.lower().endswith(('.mp4', '.mkv', '.avi', '.webm', '.mov'))]
    if videos:
        print(f"Videos in {folder}:")
        for i, f in enumerate(videos):
            print(f"  {i+1}. {f}")
        idx = input(f"\nOpen video # (1-{len(videos)}) or Enter to skip: ").strip()
        if idx.isdigit():
            i = int(idx) - 1
            if 0 <= i < len(videos):
                filepath = os.path.abspath(os.path.join(folder, videos[i]))
                print(f"Opening {videos[i]}...")
                open_in_browser(f"file://{filepath}")
                CACHED_VIDEOS.append({
                    'title': videos[i],
                    'url': f"file://{filepath}"
                })
    else:
        print("No videos found.")

def list_text_files(path='.', add_to_cache=True, allow_post=True):
    import os
    folder = path if path != '.' else os.getcwd()
    if not os.path.isdir(folder):
        print(f"Folder not found: {folder}")
        return
    texts = [f for f in os.listdir(folder) if f.lower().endswith(('.txt', '.md', '.html', '.json', '.xml'))]
    if texts:
        print(f"Text files in {folder}:")
        for i, f in enumerate(texts):
            print(f"  {i+1}. {f}")
        if add_to_cache:
            idx = input(f"\nAdd to text cache # (1-{len(texts)}) or Enter to skip: ").strip()
            if idx.isdigit():
                i = int(idx) - 1
                if 0 <= i < len(texts):
                    filepath = os.path.join(folder, texts[i])
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        ai_texts.append({
                            'text': content,
                            'source': 'file',
                            'filename': texts[i],
                            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                        })
                        print(f"Added to text cache: {texts[i]}")
                    except Exception as e:
                        print(f"Error reading file: {e}")
            if allow_post:
                opt = input("Post this text? (y/n): ").strip().lower()
                if opt == 'y':
                    num = input("Which # to post: ").strip()
                    if num.isdigit():
                        i = int(num) - 1
                        if 0 <= i < len(texts):
                            filepath = os.path.join(folder, texts[i])
                            caption = input("Caption: ").strip()
                            where = input("Post to: 1=FB, 2=Tumblr, 3=Both: ").strip() or "3"
                            content = convert_text_for_upload(filepath)
                            if where in ('1', '3'):
                                fb_post_text(content if content else caption)
                            if where in ('2', '3'):
                                tumblr_post_text(texts[i], content or caption)
    else:
        print("No text files found.")

def convert_text_for_upload(filepath):
    import os, re
    ext = filepath.rsplit('.', 1)[-1].lower()
    ansi_escape = re.compile(r'\x1b\[[0-9;]*[A-Za-z]')
    def strip_ansi(text):
        return ansi_escape.sub('', text)
    if ext in ('html', 'htm'):
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            return strip_ansi(soup.get_text(separator='\n', strip=True))
        except:
            return None
    elif ext == 'json':
        try:
            import json
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return json.dumps(data, indent=2)
        except:
            return None
    elif ext == 'xml':
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(filepath)
            return strip_ansi(ET.tostring(tree.getroot(), encoding='unicode'))
        except:
            return None
    else:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return strip_ansi(f.read())

def open_url(url):
    open_in_browser(url)

def download_url(url, filepath):
    download_file(url, filepath)

def fb_post_image_interactive():
    print("Image source: 1=URL, 2=File")
    src = input("Choose (1-2): ").strip() or "1"
    msg = input("Message: ").strip()
    if src == "1":
        url = input("Image URL: ").strip()
        if url:
            fb_post_image_url(url, msg)
    else:
        filepath = input("File path: ").strip()
        if filepath:
            fb_post_image_file(filepath, msg)

def tumblr_post_interactive():
    title = input("Title: ").strip() or "Post"
    body = input("Body: ").strip()
    tags = input("Tags (comma): ").strip()
    tags_list = [t.strip() for t in tags.split(',')] if tags else None
    result = tumblr_post_text(title, body, tags_list)
    print(f"Tumblr: {get_tumblr_status_message(result)}")

def tumblr_post_image_interactive():
    print("Image source:")
    print("  1. Image URL")
    print("  2. Local file")
    src = input("Choose (1-2): ").strip() or "1"
    caption = input("Caption: ").strip()
    tags = input("Tags: ").strip()
    tags_list = [t.strip() for t in tags.split(',')] if tags else None
    
    if src == "1":
        url = input("Image URL: ").strip()
        if url:
            result = tumblr_post_photo(url, caption, tags_list)
            print(f"Tumblr: {get_tumblr_status_message(result)}")
    else:
        filepath = input("File path: ").strip()
        if filepath:
            result = tumblr_post_photo('', caption, tags_list, local_file=filepath)
            print(f"Tumblr: {get_tumblr_status_message(result)}")

def tumblr_post_link_interactive():
    title = input("Title: ").strip()
    url = input("URL: ").strip()
    desc = input("Description: ").strip()
    tags = input("Tags: ").strip()
    tags_list = [t.strip() for t in tags.split(',')] if tags else None
    if title and url:
        result = tumblr_post_link(title, url, desc, tags_list)
        print(f"Tumblr: {get_tumblr_status_message(result)}")

def tumblr_post_video_interactive():
    url = input("YouTube URL: ").strip()
    caption = input("Caption: ").strip()
    tags = input("Tags: ").strip()
    tags_list = [t.strip() for t in tags.split(',')] if tags else None
    if url:
        result = tumblr_post_video(url, caption, tags_list)
        print(f"Tumblr: {get_tumblr_status_message(result)}")

def post_interactive():
    print("Post to both Facebook & Tumblr")
    print("Type: 1=Text, 2=Link, 3=Image, 4=Video")
    ptype = input("Choose: ").strip()
    
    msg = input("Message/Caption: ").strip()
    
    if ptype == '1':
        fb_post_text(msg)
        title = input("Tumblr title: ").strip() or "Post"
        body = input("Tumblr body (or Enter for same): ").strip() or msg
        tags = input("Tags (comma): ").strip()
        tags_list = [t.strip() for t in tags.split(',')] if tags else None
        result = tumblr_post_text(title, body, tags_list)
        print(f"Tumblr: {get_tumblr_status_message(result)}")
    
    elif ptype == '2':
        url = input("URL: ").strip()
        if url:
            fb_post_link(url, msg)
            title = input("Tumblr title: ").strip() or "Link"
            desc = input("Tumblr description: ").strip() or msg
            tags = input("Tags (comma): ").strip()
            tags_list = [t.strip() for t in tags.split(',')] if tags else None
            result = tumblr_post_link(title, url, desc, tags_list)
            print(f"Tumblr: {get_tumblr_status_message(result)}")
    
    elif ptype == '3':
        print("Image source: 1=URL, 2=File")
        imgsrc = input("Choose: ").strip() or "1"
        tags = input("Tags (comma): ").strip()
        tags_list = [t.strip() for t in tags.split(',')] if tags else None
        
        if imgsrc == "1":
            img_url = input("Image URL: ").strip()
            if img_url:
                fb_post_image_url(img_url, msg)
                result = tumblr_post_photo(img_url, msg, tags_list)
                print(f"Tumblr: {get_tumblr_status_message(result)}")
        else:
            filepath = input("File path: ").strip()
            if filepath and os.path.exists(filepath):
                fb_post_image_file(filepath, msg)
                result = tumblr_post_photo('', msg, tags_list, local_file=filepath)
                print(f"Tumblr: {get_tumblr_status_message(result)}")
    
    elif ptype == '4':
        url = input("YouTube URL: ").strip()
        tags = input("Tags (comma): ").strip()
        tags_list = [t.strip() for t in tags.split(',')] if tags else None
        if url:
            fb_post_link(url, msg)
            result = tumblr_post_video(url, msg, tags_list)
            print(f"Tumblr: {get_tumblr_status_message(result)}")

def show_history():
    history = load_history()
    if history:
        print("=== Search History ===")
        for h in history[-10:]:
            print(f"  [{h.get('source', '?')}] {h.get('query', '')}")
    else:
        print("No history.")

def scmpy_help():
    print("""
=== SCMPY COMMANDS ===
Type 'scm' or 'scmpy' to enter this mode.

SEARCH:
  web     - Search web links
  img     - Search images
  yt      - Search YouTube
  gtxt    - Generate AI text
  gimg    - Generate AI images
  history - View search history

VIEW:
  list    - List cached images
  open    - Open link in browser
  view    - Open image in browser
  lv      - List YouTube results (with option to open)

LOCAL FILES:
  li      - List images from folder (add to cache/post)
  ltxt    - List text files (add to cache/post)
  lvv    - List local videos

POSTING (Facebook):
  fbpost  - Post text
  fblink  - Post link
  fbimg   - Post image
  fblist  - List posts

POSTING (Tumblr):
  tmpost  - Post text
  tmimg   - Post image (URL/file)
  tmlink  - Post link
  tmvid   - Post video
  tmlist  - List posts

POSTING (Both):
  post    - Post to FB + Tumblr

DOWNLOAD:
  dl      - Download image by number
  dla     - Download all images
  dlurl   - Download by URL

CACHE POSTING:
  pimg    - Post image (from 'img')
  plink   - Post link (from 'web')
  pvid    - Post video (from 'yt')

TEXT/AI:
  ptext   - Post with AI image
  ailist  - List AI text generations
  aiexport - Export AI texts to file
  smuck   - AI article + AI image + post to Tumblr/Facebook/Both

OTHER:
  backup  - Backup data
  restore - Restore from backup
  wipeda  - Wipe all data (history, cache, texts)
  wipekey - Wipe stored API keys
  install - Install dependencies (pip/pipx)
  config  - Configure API keys
  h       - Show this help
  x/q     - Exit SCMPY
""")

def smuck():
    print("\n=== Smuck: AI Article + Image + Post ===")
    art_topic = input("Article prompt: ").strip()
    if not art_topic:
        print("Cancelled.")
        return

    print("\n--- Generating AI Article ---")
    article = generate_text(art_topic)
    if not article:
        print("Article generation failed.")
        return

    print(f"\nArticle generated ({len(article)} chars):\n{article}")

    img_prompt = input("\nImage prompt (Enter to reuse article prompt): ").strip()
    if not img_prompt:
        img_prompt = art_topic

    print("\n--- Generating AI Image ---")
    generate_ai_images(img_prompt, num=1)
    if not CACHED_IMAGES:
        print("Image generation failed.")
        return

    image_url = CACHED_IMAGES[0].get('image', '')

    print("\n--- Post To ---")
    print("1. Tumblr")
    print("2. Facebook")
    print("3. Both")
    where = input("Choose (1-3): ").strip()

    tags = input("Tags for Tumblr (comma separated): ").strip()
    tags_list = [t.strip() for t in tags.split(',')] if tags else None

    if where in ('1', '3'):
        result = tumblr_post_photo(image_url, article, tags_list)
        print(f"Tumblr: {get_tumblr_status_message(result)}")

    if where in ('2', '3'):
        message = article[:5000] if len(article) > 5000 else article
        fb_post_image_url(image_url, message)


def scmpy_main():
    dep_imports = {
        'requests': 'requests',
        'requests-oauthlib': 'requests_oauthlib',
        'beautifulsoup4': 'bs4',
        'lxml': 'lxml',
        'Pillow': 'PIL'
    }
    missing = []
    for pkg, imp in dep_imports.items():
        try:
            __import__(imp)
        except ImportError:
            missing.append(pkg)
    if missing:
        print("\n=== Missing Dependencies ===")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\nInstall now? [Y/n]: ", end='', flush=True)
        try:
            resp = input().strip().lower()
        except:
            resp = 'y'
        if resp in ['', 'y', 'yes']:
            import subprocess
            for pkg in missing:
                print(f"Installing {pkg}...")
                subprocess.run([sys.executable, '-m', 'pip', 'install', pkg], capture_output=True)
        else:
            print("Some features may not work.")
    load_history()
    show_help = True
    
    print("""
=== SCMPY v2.1 - Social Media CLI ===


Type 'h' for help, 'x' to exit
""")
    
    while True:
        if show_help:
                print("\nSCMPY $ ", end='')
        else:
            print("\nSCMPY $ ", end='')
        
        choice = input().strip().lower()
        
        if choice in ['exit', 'quit', '0', 'x', 'q', 'bye', 'stop']:
            print("Goodbye!")
            break
        
        elif choice in ['help', 'commands', '?', 'h']:
            scmpy_help()
            show_help = False
            continue
        
        elif choice in ['web', 'w', 'search', 's']:
            query = input("Search query: ").strip()
            if query:
                num = input("How many results? (default 10): ").strip() or "10"
                search_web(query, int(num))
                search_history.append({
                    'query': query,
                    'source': 'web',
                    'num': num,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                })
                save_history()
        
        elif choice in ['img', 'i', 'image', 'images']:
            query = input("Image search query: ").strip()
            if query:
                print("\nImage sources:")
                print("  1. Flickr (real relevant images)")
                print("  2. Picsum (random fallback)")
                print("  3. Wikimedia Commons")
                print("  4. Pollinations (AI-generated)")
                print("  5. LoremFlickr (random relevant)")
                print("  6. All (try each until one works)")
                src = input("Choose source (1-6, default 1): ").strip() or "1"
                source_map = {'1': 'flickr', '2': 'picsum', '3': 'wikimedia', '4': 'pollinations', '5': 'loremflickr', '6': 'all'}
                source = source_map.get(src, 'flickr')
                
                num = input("How many results? (default 10): ").strip() or "10"
                
                if source == 'all':
                    search_images(query, int(num))
                else:
                    search_images(query, int(num), source)
                
                search_history.append({
                    'query': query,
                    'source': f'images-{source}',
                    'num': num,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                })
                save_history()
        
        elif choice in ['yt', 'youtube', 'y', 'video', 'videos']:
            query = input("YouTube search query: ").strip()
            if query:
                num = input("How many results? (default 10): ").strip() or "10"
                search_youtube(query, int(num))
                search_history.append({
                    'query': query,
                    'source': 'youtube',
                    'num': num,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                })
                save_history()
        
        elif choice in ['gtxt', 'text', 'ai', 'gpt', 'gen']:
            prompt = input("AI text prompt: ").strip()
            if prompt:
                result = generate_text(prompt)
                if result:
                    print(f"\n--- Generated Text ---")
                    print(result[:500] + "..." if len(result) > 500 else result)
        
        elif choice in ['gimg', 'gai', 'aigen', 'imagegen']:
            prompt = input("AI image prompt: ").strip()
            if prompt:
                num = input("How many images? (default 1): ").strip() or "1"
                generate_ai_images(prompt, int(num))
        
        elif choice in ['smuck', 'smk']:
            smuck()
        
        elif choice in ['list', 'ls', 'l', 'tyls', 'images']:
            if CACHED_IMAGES:
                print("\nImage options:")
                print("  1. tyls - List all images")
                print("  2. tycat - View image in browser")
                print("  3. tycat - View image in terminal (tycat/w3m)")
                opt = input("Choose (1-3): ").strip()
                if opt == '1':
                    display_images()
                elif opt == '2':
                    tycat(CACHED_IMAGES)
                elif opt == '3':
                    tycat(CACHED_IMAGES, use_terminal=True)
            else:
                print("No images searched yet!")
        
        elif choice in ['view', 'v', 'openimg', 'show']:
            if CACHED_IMAGES:
                num = input(f"Image number (1-{len(CACHED_IMAGES)}): ").strip()
                try:
                    idx = int(num) - 1
                    if 0 <= idx < len(CACHED_IMAGES):
                        url = CACHED_IMAGES[idx].get('image', '')
                        print(f"Opening: {url}")
                        open_in_browser(url)
                except:
                    print("Invalid")
            else:
                print("No images to view!")
        
        elif choice in ['li', 'limg', 'localimg']:
            path = input("Folder (default .): ").strip() or "."
            list_images(path, add_to_cache=True, allow_upload=True)
        
        elif choice in ['ltxt', 'txtfiles', 'localtxt']:
            path = input("Folder (default .): ").strip() or "."
            list_text_files(path, add_to_cache=True, allow_post=True)
        
        elif choice in ['lvv', 'lvid', 'localvid']:
            path = input("Folder (default .): ").strip() or "."
            list_videos(path)
        
        elif choice in ['videos', 'vid', 'youtubes', 'lv']:
            if CACHED_VIDEOS:
                display_videos()
            else:
                print("No videos searched yet! Run 'yt' first.")
        
        elif choice in ['open', 'o', 'url', 'link']:
            if CACHED_LINKS:
                num = input(f"Link number (1-{len(CACHED_LINKS)}): ").strip()
                try:
                    idx = int(num) - 1
                    if 0 <= idx < len(CACHED_LINKS):
                        url = CACHED_LINKS[idx].get('url', '')
                        if not url:
                            # Try 'link' key
                            url = CACHED_LINKS[idx].get('link', '')
                        print(f"Opening: {url}")
                        if url:
                            open_in_browser(url)
                        else:
                            print("No URL found in this result")
                except Exception as e:
                    print(f"Error: {e}")
            else:
                print("No links searched yet! Run 'web' first.")
        
        elif choice in ['dl', 'download', 'd']:
            if CACHED_IMAGES:
                num = input(f"Image number (1-{len(CACHED_IMAGES)}): ").strip()
                folder = input("Folder (default ./downloads): ").strip() or "./downloads"
                prefix = input("Filename prefix (default download): ").strip()
                try:
                    download_by_number(CACHED_IMAGES, int(num), folder, is_image=True, prefix=prefix)
                except:
                    print("Invalid")
            else:
                print("No images to download!")
        
        elif choice in ['dla', 'dlall', 'downloadall', 'dal']:
            if CACHED_IMAGES:
                folder = input("Folder (default ./downloads): ").strip() or "./downloads"
                prefix = input("Filename prefix (default img): ").strip() or "img"
                download_all_images(CACHED_IMAGES, folder, prefix)
            else:
                print("No images to download!")
        
        elif choice in ['dlurl', 'dlu', 'get']:
            url = input("URL to download: ").strip()
            folder = input("Folder (default ./downloads): ").strip() or "./downloads"
            download_by_link_simple(url, folder)
        
        elif choice in ['pimg', 'postimg', 'pi']:
            if not CACHED_IMAGES:
                print("No images! Search first with 'img'")
            else:
                print(f"Images available: 1-{len(CACHED_IMAGES)}")
                num = input("Image number: ").strip()
                try:
                    post_image_by_number(int(num))
                except ValueError:
                    print("Invalid number")
        
        elif choice in ['plink', 'postlink', 'posturl', 'pl']:
            if not CACHED_LINKS:
                print("No links! Search first with 'web'")
            else:
                print(f"Links available: 1-{len(CACHED_LINKS)}")
                num = input("Link number: ").strip()
                try:
                    post_link_by_number(int(num))
                except ValueError:
                    print("Invalid number")
        
        elif choice in ['pvid', 'postvid', 'postvideo', 'pv']:
            if not CACHED_VIDEOS:
                print("No videos! Search first with 'yt'")
            else:
                print(f"Videos available: 1-{len(CACHED_VIDEOS)}")
                num = input("Video number: ").strip()
                try:
                    post_video_by_number(int(num))
                except ValueError:
                    print("Invalid number")
        
        elif choice in ['ptext', 'posttext', 'pt', 'textpost']:
            post_text_interactive()
        
        elif choice in ['ailist', 'ai', 'aitext', 'texts']:
            list_ai_texts()
        
        elif choice in ['aiexport', 'exportai', 'aiex', 'exporttexts']:
            export_ai_texts()
        
        elif choice in ['fbpost', 'fb', 'fpost', 'fbt']:
            message = input("Message: ").strip()
            if message:
                fb_post_text(message)
        
        elif choice in ['fblink', 'fbl', 'flink', 'fblink']:
            url = input("URL: ").strip()
            msg = input("Message: ").strip()
            if url:
                fb_post_link(url, msg)
        
        elif choice in ['fbimg', 'fbi', 'fimage', 'fbpimage']:
            print("Image source:")
            print("  1. Image URL")
            print("  2. Local file")
            src = input("Choose (1-2): ").strip() or "1"
            msg = input("Message: ").strip()
            if src == "1":
                url = input("Image URL: ").strip()
                if url:
                    fb_post_image_url(url, msg)
            else:
                filepath = input("File path: ").strip()
                if filepath:
                    fb_post_image_file(filepath, msg)
        
        elif choice in ['fblist', 'fbls', 'fbposts', 'fbls']:
            num = input("How many posts? (default 10): ").strip() or "10"
            fb_list_posts(int(num))
        
        elif choice in ['tmpost', 'tm', 'tpost', 'tmp']:
            title = input("Title: ").strip()
            body = input("Body: ").strip()
            tags = input("Tags (comma separated): ").strip()
            tags_list = [t.strip() for t in tags.split(',')] if tags else None
            if title and body:
                result = tumblr_post_text(title, body, tags_list)
                print(f"Tumblr: {get_tumblr_status_message(result)}")
        
        elif choice in ['tmimg', 'tmi', 'timg', 'tmimage']:
            print("Image source:")
            print("  1. Image URL")
            print("  2. Local file")
            src = input("Choose (1-2): ").strip() or "1"
            caption = input("Caption: ").strip()
            tags = input("Tags: ").strip()
            tags_list = [t.strip() for t in tags.split(',')] if tags else None
            
            if src == "1":
                url = input("Image URL: ").strip()
                if url:
                    result = tumblr_post_photo(url, caption, tags_list)
                    print(f"Tumblr: {get_tumblr_status_message(result)}")
            else:
                filepath = input("File path: ").strip()
                if filepath:
                    result = tumblr_post_photo('', caption, tags_list, local_file=filepath)
                    print(f"Tumblr: {get_tumblr_status_message(result)}")
        
        elif choice in ['tmlink', 'tml', 'tlink', 'tml']:
            title = input("Title: ").strip()
            url = input("URL: ").strip()
            desc = input("Description: ").strip()
            tags = input("Tags: ").strip()
            tags_list = [t.strip() for t in tags.split(',')] if tags else None
            if title and url:
                result = tumblr_post_link(title, url, desc, tags_list)
                print(f"Tumblr: {get_tumblr_status_message(result)}")
        
        elif choice in ['tmvid', 'tmv', 'tvid', 'tmvideo']:
            url = input("YouTube URL: ").strip()
            caption = input("Caption: ").strip()
            tags = input("Tags: ").strip()
            tags_list = [t.strip() for t in tags.split(',')] if tags else None
            if url:
                result = tumblr_post_video(url, caption, tags_list)
                print(f"Tumblr: {get_tumblr_status_message(result)}")
        
        elif choice in ['tmlist', 'tmls', 'tmposts', 'tmls']:
            result = tumblr_get_posts(10)
            posts = result.get('response', {}).get('posts', [])
            for i, p in enumerate(posts):
                print(f"{i+1}. [{p.get('type', 'post')}] {p.get('post_url', '')[:60]}...")
        
        elif choice in ['post', 'p', 'both', 'share']:
            print("Post to both Facebook & Tumblr")
            print("Type: 1=Text, 2=Link, 3=Image, 4=Video")
            ptype = input("Choose: ").strip()
            
            msg = input("Message/Caption: ").strip()
            
            if ptype == '1':
                fb_post_text(msg)
                title = input("Tumblr title: ").strip() or "Post"
                body = input("Tumblr body (or Enter for same): ").strip() or msg
                tags = input("Tags (comma): ").strip()
                tags_list = [t.strip() for t in tags.split(',')] if tags else None
                result = tumblr_post_text(title, body, tags_list)
                print(f"Tumblr: {get_tumblr_status_message(result)}")
            
            elif ptype == '2':
                url = input("URL: ").strip()
                if url:
                    fb_post_link(url, msg)
                    title = input("Tumblr title: ").strip() or "Link"
                    desc = input("Tumblr description: ").strip() or msg
                    tags = input("Tags (comma): ").strip()
                    tags_list = [t.strip() for t in tags.split(',')] if tags else None
                    result = tumblr_post_link(title, url, desc, tags_list)
                    print(f"Tumblr: {get_tumblr_status_message(result)}")
            
            elif ptype == '3':
                print("Image source: 1=URL, 2=File")
                imgsrc = input("Choose: ").strip() or "1"
                tags = input("Tags (comma): ").strip()
                tags_list = [t.strip() for t in tags.split(',')] if tags else None
                
                if imgsrc == "1":
                    img_url = input("Image URL: ").strip()
                    if img_url:
                        fb_post_image_url(img_url, msg)
                        result = tumblr_post_photo(img_url, msg, tags_list)
                        print(f"Tumblr: {get_tumblr_status_message(result)}")
                else:
                    filepath = input("File path: ").strip()
                    if filepath and os.path.exists(filepath):
                        fb_post_image_file(filepath, msg)
                        result = tumblr_post_photo('', msg, tags_list, local_file=filepath)
                        print(f"Tumblr: {get_tumblr_status_message(result)}")
            
            elif ptype == '4':
                url = input("YouTube URL: ").strip()
                tags = input("Tags (comma): ").strip()
                tags_list = [t.strip() for t in tags.split(',')] if tags else None
                if url:
                    fb_post_link(url, msg)
                    result = tumblr_post_video(url, msg, tags_list)
                    print(f"Tumblr: {get_tumblr_status_message(result)}")
        
        elif choice in ['history', 'hist', 'hx', 'sh']:
            print("\n=== Search History ===")
            for h in search_history[-10:]:
                print(f"  [{h.get('source', '?')}] {h.get('query', '')}")
        
        elif choice in ['install', 'inst', 'install-deps', 'deps']:
            install_dependencies()
        
        elif choice in ['backup', 'bak', 'save', 'export']:
            backup_all_data()
        
        elif choice in ['restore', 'res', 'load', 'import']:
            restore_from_backup()
        
        elif choice in ['wipeda', 'wipedata', 'wipe-data', 'clear-data']:
            wipe_data()
        
        elif choice in ['wipekey', 'wipekeys', 'wipe-keys', 'clear-keys']:
            wipe_keys()
        
        elif choice in ['config', 'cfg', 'keys', 'settings']:
            keys.configure_keys()
        
        elif choice == 'scmpy' or choice == 'scm':
            print("Already in SCMPY mode!")
        
        elif choice:
            print(f"Unknown command: {choice}")
            print("Type 'help' for available commands")

def download_by_link_simple(url, folder):
    os.makedirs(folder, exist_ok=True)
    name = url.split('/')[-1].split('?')[0] or "download"
    ext = name.split('.')[-1][:4] if '.' in name else 'jpg'
    if len(ext) < 2:
        ext = 'jpg'
    filename = f"download.{ext}"
    filepath = os.path.join(folder, filename)
    download_file(url, filepath)

def view_with_w3m(url, title):
    env = os.environ.copy()
    env['TERM'] = 'xterm-256color'
    
    if not check_dependency('curl', 'apt install curl', 'curl'):
        print("curl required for terminal image viewing")
        return
    
    in_terminology = env.get('TERM_PROGRAM') == 'terminology' or env.get('TERMINOLOGY')
    
    tycat_available = subprocess.run(['which', 'tycat'], capture_output=True).returncode == 0
    
    if tycat_available and in_terminology:
        try:
            suffix = url.split('.')[-1].lower()[:4]
            if suffix not in ['jpg', 'png', 'gif', 'bmp']:
                suffix = 'jpg'
            tmp_path = f'/tmp/view_img_{os.getpid()}.{suffix}'
            
            run_cmd('curl', '-sL', '-o', tmp_path, url, timeout=30)
            
            if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0:
                subprocess.run(['tycat', tmp_path], timeout=30, env=env)
                try:
                    os.remove(tmp_path)
                except:
                    pass
                return
        except Exception as e:
            pass
    
    if not cmd_exists('w3m'):
        print("w3m required for terminal image viewing. Install via: apt install w3m")
        return
    
    try:
        html = f"""<!DOCTYPE html>
<html>
<head><title>{title}</title></head>
<body style="background:black; text-align:center; padding:20px;">
<img src="{url}" style="max-width:100%; max-height:90vh;">
<div style="color:white;">Press q to quit</div>
</body>
</html>"""
        with open('/tmp/view_img.html', 'w') as f:
            f.write(html)
        subprocess.run(['w3m', '-T', 'text/html', '/tmp/view_img.html'],
                       env=env, timeout=30)
    except subprocess.TimeoutExpired:
        print("w3m timed out")
    except FileNotFoundError:
        print("w3m not found. Install with: apt install w3m")
    except Exception as e:
        print(f"Error: {e}")

def tycat(items, index=None, use_terminal=False):
    if not items:
        print("No images to display!")
        return
    
    if index is None:
        print(f"Enter image number (1-{len(items)}): ", end='')
        try:
            index = int(input().strip()) - 1
        except:
            return
    
    if index < 0 or index >= len(items):
        print("Invalid number!")
        return
    
    item = items[index]
    title = item.get('title', f'Image {index+1}')
    url = item.get('image', item.get('url', ''))
    
    if use_terminal:
        view_with_w3m(url, title)
    else:
        print(f"\n=== IMAGE {index+1} ===")
        print(f"Title: {title}")
        print(f"URL: {url}")
        if url:
            print(f"\nOpening: {url}")
            open_in_browser(url)

if __name__ == "__main__":
    try:
        scmpy_main()
    except Exception as e:
        print(f"SCMPY error: {e}")

def install_dependencies():
    scmpy_deps = ['requests', 'requests-oauthlib', 'beautifulsoup4', 'lxml', 'Pillow']
    
    while True:
        print()
        print('=== Install Dependencies ===')
        print(f'Python deps: {scmpy_deps}')
        print('System deps: w3m, w3m-img (optional)')
        print()
        print('1. pip (user install all)')
        print('2. pipx (inject into morn)')
        print('3. pipx (inject into mprocs)')
        print('4. pipx (inject into mdcci)')
        print('5. pipx (inject into m0nkrpg)')
        print('6. pipx (inject into ALL)')
        print('7. Install system deps (w3m)')
        print('8. Back to main menu')
        
        choice = input('Choose: ').strip()
        
        def do_inject(pkg):
            for dep in scmpy_deps:
                r = __import__('subprocess').run(['pipx', 'inject', pkg, dep], capture_output=True, text=True)
                print(f'  [+] {dep} -> {pkg}' if r.returncode == 0 else f'  [X] {dep} -> {pkg}')
        
        if choice == '1':
            print()
            for dep in scmpy_deps:
                r = __import__('subprocess').run([__import__('sys').executable, '-m', 'pip', 'install', '--user', dep], capture_output=True, text=True)
                print(f'  [+] {dep}' if r.returncode == 0 else f'  [X] {dep}')
        elif choice == '2':
            print()
            do_inject('morn')
        elif choice == '3':
            print()
            do_inject('mprocs')
        elif choice == '4':
            print()
            do_inject('mdcci')
        elif choice == '5':
            print()
            do_inject('m0nkrpg')
        elif choice == '6':
            print()
            for pkg in ['morn', 'mprocs', 'mdcci', 'm0nkrpg']:
                do_inject(pkg)
        elif choice == '7':
            print()
            if __import__('os').path.exists('/usr/bin/apt'):
                __import__('subprocess').run(['sudo', 'apt', 'install', '-y', 'w3m', 'w3m-img'], text=True)
                print('  [+] w3m installed')
            elif __import__('os').path.exists('/usr/bin/dnf'):
                __import__('subprocess').run(['sudo', 'dnf', 'install', '-y', 'w3m', 'w3m-img'], text=True)
                print('  [+] w3m installed')
            elif __import__('os').path.exists('/usr/bin/pacman'):
                __import__('subprocess').run(['sudo', 'pacman', '-S', '--noconfirm', 'w3m'], text=True)
                print('  [+] w3m installed')
            else:
                print('  [X] Unknown package manager')
        elif choice == '8':
            print('Returning to main menu...')
            break
        else:
            print('Invalid choice.')




def check_dependencies(quiet=False):
    required = {
        'requests': 'requests',
        'requests-oauthlib': 'requests_oauthlib',
        'beautifulsoup4': 'bs4',
        'lxml': 'lxml',
        'Pillow': 'PIL'
    }
    missing = []
    for pkg, mod in required.items():
        try:
            __import__(mod)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print()
        print('=== Missing Dependencies for SCMPY ===')
        print(f'Missing: {missing}')
        print('Install with: pip install ' + ' '.join(missing))
        print('Or: pipx inject morn ' + ' '.join(missing))
        if not quiet:
            print('Type install in scmpy menu to install.')
        return False
    return True

