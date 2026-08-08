import json
import os
import sys
import subprocess
import urllib.request
import urllib.error

MPROCS_VERSION = "MProcs-10.0"
PACKAGE_NAME = "MProcs"
PYPI_URL = f"https://pypi.org/pypi/{PACKAGE_NAME}/json"

try:
    import importlib.metadata
    PACKAGE_VERSION = importlib.metadata.version(PACKAGE_NAME)
except Exception:
    PACKAGE_VERSION = "8.8"

_latest_version = None
_update_available = False


def check_for_update(timeout=5):
    global _latest_version, _update_available
    try:
        req = urllib.request.Request(PYPI_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
            _latest_version = data['info']['version']
            _update_available = _latest_version != PACKAGE_VERSION
            return _latest_version, _update_available
    except Exception:
        return None, False


def print_version_status():
    latest, available = check_for_update()
    label = f"{MPROCS_VERSION} (v{PACKAGE_VERSION})"
    if latest is None:
        print(f"{label}: (offline)")
    elif available:
        print(f"{label}: Update available — {latest}")
    else:
        print(f"{label}: Up-to-date")


def perform_update():
    print("Updating MProcs...")
    result = subprocess.run(
        [sys.executable, '-m', 'pip', 'install', '--upgrade', PACKAGE_NAME],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(result.stdout)
        print("Update successful! Restart to apply.")
        return
    print(f"Update failed:\n{result.stderr[:500]}")
    retry = input("\nRetry with --break-system-packages? (y/n): ").strip().lower()
    if retry == 'y':
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--upgrade', '--break-system-packages', PACKAGE_NAME],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(result.stdout)
            if result.stderr:
                print(result.stderr[:500])
            print("Update successful! Restart to apply.")
        else:
            print(f"Update still failed:\n{result.stderr[:500]}")
    else:
        print("Update cancelled.")


def restart_app():
    print("Restarting...")
    os.execl(sys.executable, sys.executable, *sys.argv)
