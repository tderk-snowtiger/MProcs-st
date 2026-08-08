import os
import json

CONFIG_DIR = os.path.expanduser("~/.config/scmpy")
CONFIG_FILE = os.path.join(CONFIG_DIR, "keys.json")

def ensure_config_dir():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR, exist_ok=True)

def load_keys():
    ensure_config_dir()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_keys(keys):
    ensure_config_dir()
    with open(CONFIG_FILE, 'w') as f:
        json.dump(keys, f, indent=2)

def get_key(key_name):
    keys = load_keys()
    return keys.get(key_name, "")

def set_key(key_name, value):
    keys = load_keys()
    keys[key_name] = value
    save_keys(keys)

def get_all_keys():
    return load_keys()

def configure_keys():
    ensure_config_dir()
    print("\n=== SCMPY API Key Configuration ===")
    print(f"Keys will be saved to: {CONFIG_FILE}")
    print()
    
    keys = load_keys()
    
    print("Enter your API keys (press Enter to skip):")
    print()
    
    print("1. Pollinations API Key (for AI text/images):")
    keys['pollinations_api_key'] = input("   > ").strip() or keys.get('pollinations_api_key', '')
    
    print()
    print("2. Facebook App ID:")
    keys['fb_app_id'] = input("   > ").strip() or keys.get('fb_app_id', '')
    
    print()
    print("3. Facebook App Secret:")
    keys['fb_app_secret'] = input("   > ").strip() or keys.get('fb_app_secret', '')
    
    print()
    print("4. Facebook Page Access Token:")
    keys['fb_page_access_token'] = input("   > ").strip() or keys.get('fb_page_access_token', '')
    
    print()
    print("5. Tumblr API Key:")
    keys['tumblr_api_key'] = input("   > ").strip() or keys.get('tumblr_api_key', '')
    
    print()
    print("6. Tumblr API Secret:")
    keys['tumblr_api_secret'] = input("   > ").strip() or keys.get('tumblr_api_secret', '')
    
    print()
    print("7. Tumblr Access Token:")
    keys['tumblr_token'] = input("   > ").strip() or keys.get('tumblr_token', '')
    
    print()
    print("8. Tumblr Token Secret:")
    keys['tumblr_token_secret'] = input("   > ").strip() or keys.get('tumblr_token_secret', '')
    
    print()
    print("9. Tumblr Blog Name:")
    keys['tumblr_blog'] = input("   > ").strip() or keys.get('tumblr_blog', '')
    
    save_keys(keys)
    print()
    print("Keys saved successfully!")
    print()

def get_or_prompt_key(key_name, prompt, default=""):
    keys = load_keys()
    value = keys.get(key_name, default)
    if not value:
        print(prompt)
        value = input("> ").strip()
        keys[key_name] = value
        save_keys(keys)
    return value