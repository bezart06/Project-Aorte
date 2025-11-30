import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import zipfile

# IMPORTANT
GITHUB_REPO = "bezart06/Project-Aorte"

API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases"
CURRENT_VERSION = "ver.0.3.0-hotfix"


def parse_to_comparable(version_str):
    """
    Handles 'ver.X.Y.Z' and 'ver.X.Y.Z-hotfix' style tags.
    A post-release tag ('-hotfix') makes the version higher than one without it.
    Example: ('ver.1.2.3-hotfix') -> ((1, 2, 3), 1)
             ('ver.1.2.3')        -> ((1, 2, 3), 0)
    This ensures ( (1,2,3), 1 ) > ( (1,2,3), 0 ) is true.
    """
    if not isinstance(version_str, str):
        return None

    if version_str.startswith("ver."):
        version_str = version_str[4:]

    # Separate main version from post-release tags (e.g., -hotfix)
    parts = version_str.split('-', 1)
    main_version_str = parts[0]
    post_release_marker = 1 if len(parts) > 1 else 0

    try:
        release_tuple = tuple(map(int, main_version_str.split('.')))
        return release_tuple, post_release_marker
    except (ValueError, TypeError):
        return None


def check_for_updates():
    """
    Fetches all releases, filters out pre-releases, and finds the latest stable version
    that is newer than the current version, including hotfixes.
    """
    try:
        print("Checking for updates...")
        with urllib.request.urlopen(API_URL, timeout=10) as response:
            if response.status != 200:
                print(f"Error: Data could not be retrieved (status: {response.status})")
                return None
            all_releases = json.loads(response.read().decode('utf-8'))

        latest_stable_release = None
        current_v_comparable = parse_to_comparable(CURRENT_VERSION)

        if not current_v_comparable:
            print(f"Error: Current version '{CURRENT_VERSION}' is in an invalid format.")
            return None

        highest_v_comparable = current_v_comparable

        for release in all_releases:
            if release.get("draft", False) or release.get("prerelease", False):
                continue

            tag_name = release.get("tag_name")
            release_v_comparable = parse_to_comparable(tag_name)

            if release_v_comparable and release_v_comparable > highest_v_comparable:
                highest_v_comparable = release_v_comparable
                latest_stable_release = tag_name

        if latest_stable_release:
            print(f"New version found: {latest_stable_release}")
            return latest_stable_release
        else:
            print("You are on the latest version.")
            return None

    except (urllib.error.URLError, json.JSONDecodeError, KeyError) as e:
        print(f"Error when checking for updates: {e}")
        return None


def download_and_apply_update(version):
    try:
        release_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/tags/{version}"

        with urllib.request.urlopen(release_url, timeout=10) as response:
            if response.status != 200:
                print(f"Error: Could not find release {version} (status: {response.status})")
                return False
            release_data = json.loads(response.read().decode('utf-8'))

        zip_url = release_data.get("zipball_url")
        if not zip_url:
            print(f"Could not find source code zip for version {version}.")
            return False

        print(f"Downloading source from {zip_url}...")
        update_zip_path = os.path.join(os.getcwd(), f"update_{version}.zip")

        req = urllib.request.Request(zip_url, headers={'User-Agent': 'Project-Aorte-Updater'})
        with urllib.request.urlopen(req) as r, open(update_zip_path, 'wb') as f:
            f.write(r.read())

        print("Download verified. Preparing to update...")

        app_root_dir = os.getcwd()
        extract_dir = os.path.join(app_root_dir, "update_temp")

        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
        os.makedirs(extract_dir, exist_ok=True)

        with zipfile.ZipFile(update_zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        time.sleep(1)
        extracted_folder_name = os.listdir(extract_dir)[0]
        update_source_path = os.path.join(extract_dir, extracted_folder_name)

        main_script = sys.argv[0]
        restart_cmd = f"\"{sys.executable}\" \"{os.path.join(app_root_dir, main_script)}\""

        if sys.platform == "win32":
            script_path = os.path.join(app_root_dir, "update.bat")
            with open(script_path, "w") as f:
                f.write("@echo off\n")
                f.write("echo Waiting for application to close...\n")
                f.write("timeout /t 2 /nobreak > NUL\n")
                f.write(f"echo Copying new files...\n")
                f.write(f"xcopy /E /Y \"{update_source_path}\" \"{app_root_dir}\" > NUL\n")
                f.write("echo Update complete! Starting new version...\n")
                f.write(f"start \"Project Aorte\" {restart_cmd}\n")
                f.write(f"rd /s /q \"{extract_dir}\"\n")
                f.write(f"del \"{update_zip_path}\"\n")
                f.write("(goto) 2>nul & del \"%~f0\"\n")
            subprocess.Popen(script_path, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            script_path = os.path.join(app_root_dir, "update.sh")
            with open(script_path, "w") as f:
                f.write("#!/bin/bash\n")
                f.write("echo \"Waiting for application to close...\"\n")
                f.write("sleep 2\n")
                f.write(f"echo \"Copying new files...\"\n")
                f.write(f"cp -R \"{update_source_path}/.\" \"{app_root_dir}/\"\n")
                f.write("echo \"Update complete! Starting new version...\"\n")
                f.write(f"{restart_cmd}\n")
                f.write(f"rm -rf \"{extract_dir}\"\n")
                f.write(f"rm -f \"{update_zip_path}\"\n")
                f.write("rm -- \"$0\"\n")
            os.chmod(script_path, 0o755)
            subprocess.Popen([script_path])

        print("Update script created. The application will now close.")
        sys.exit(0)

    except Exception as e:
        print(f"An error occurred during the update process: {e}")
        if 'extract_dir' in locals() and os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
        if 'update_zip_path' in locals() and os.path.exists(update_zip_path):
            os.remove(update_zip_path)
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        check_for_updates()
