import hashlib
import os
import subprocess
import sys
import zipfile

import requests

# IMPORTANT
GITHUB_REPO = "bezart06/Project-Aorte"

API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
CURRENT_VERSION = "v0.2.0-beta"


def get_file_hash(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def check_for_updates():
    try:
        print("Checking for updates...")
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        latest_version = response.json()["tag_name"]

        if latest_version != CURRENT_VERSION:
            print(f"New version found: {latest_version}")
            return latest_version
        else:
            print("You are on the latest version.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error checking for updates: {e}")
        return None


def download_and_apply_update(version):
    platform = "windows" if sys.platform == "win32" else "unix"
    asset_name = f"aorte_{platform}.zip"

    try:
        release_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/tags/{version}"
        response = requests.get(release_url, timeout=10)
        response.raise_for_status()
        assets = response.json()["assets"]

        asset_url = None
        checksum_url = None
        for asset in assets:
            if asset['name'] == asset_name:
                asset_url = asset['browser_download_url']
            if asset['name'] == f"{asset_name}.sha256":
                checksum_url = asset['browser_download_url']

        if not asset_url or not checksum_url:
            print(f"Could not find release assets for {version} on platform {platform}.")
            return False

        print(f"Downloading {asset_name}...")
        update_zip_path = os.path.join(os.getcwd(), asset_name)
        with requests.get(asset_url, stream=True) as r:
            r.raise_for_status()
            with open(update_zip_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        print("Downloading checksum...")
        checksum_response = requests.get(checksum_url)
        checksum_response.raise_for_status()
        expected_hash = checksum_response.text.strip()

        print("Verifying download integrity...")
        downloaded_hash = get_file_hash(update_zip_path)
        if downloaded_hash != expected_hash:
            print("Error: Checksum mismatch. The downloaded file may be corrupt.")
            os.remove(update_zip_path)
            return False

        print("Download verified.")

        executable_path = sys.executable

        extract_dir = os.path.join(os.getcwd(), "update_temp")
        os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(update_zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        new_executable_name = os.path.basename(executable_path)
        new_executable_path = os.path.join(extract_dir, new_executable_name)

        if not os.path.exists(new_executable_path):
            print(f"Error: Extracted executable not found at {new_executable_path}")
            return False

        if platform == "windows":
            script_path = os.path.join(os.getcwd(), "update.bat")
            with open(script_path, "w") as f:
                f.write("@echo off\n")
                f.write("echo Waiting for application to close...\n")
                f.write("timeout /t 2 /nobreak > NUL\n")
                f.write(f"move /Y \"{new_executable_path}\" \"{executable_path}\"\n")
                f.write("echo Update complete! Starting new version...\n")
                f.write(f"start \"\" \"{executable_path}\"\n")
                f.write(f"rd /s /q \"{extract_dir}\"\n")
                f.write(f"del \"{update_zip_path}\"\n")
                f.write("(goto) 2>nul & del \"%~f0\"\n")
            subprocess.Popen(script_path, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # Unix
            script_path = os.path.join(os.getcwd(), "update.sh")
            with open(script_path, "w") as f:
                f.write("#!/bin/bash\n")
                f.write("echo \"Waiting for application to close...\"\n")
                f.write("sleep 2\n")
                f.write(f"mv -f \"{new_executable_path}\" \"{executable_path}\"\n")
                f.write("echo \"Update complete! Starting new version...\"\n")
                f.write(f"chmod +x \"{executable_path}\"\n")
                f.write(f"\"{executable_path}\" &\n")
                f.write(f"rm -rf \"{extract_dir}\"\n")
                f.write(f"rm -f \"{update_zip_path}\"\n")
                f.write(f"rm -- \"$0\"\n")
            os.chmod(script_path, 0o755)
            subprocess.Popen([script_path], shell=True)

        print("Update script created. The application will now close.")
        sys.exit(0)

    except Exception as e:
        print(f"An error occurred during the update process: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        check_for_updates()
