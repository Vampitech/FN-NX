import os
import json
import requests
from datetime import datetime, timezone

API_KEY = os.environ["FICHIER_API_KEY"]
FOLDER_ID = "W1fFILam"

def get_folder_files():
    url = "https://api.1fichier.com/v1/folder/ls.cgi"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"folder_id": FOLDER_ID}

    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()
    data = r.json()
    return data.get("items", [])

def get_download_url(file_id):
    url = "https://api.1fichier.com/v1/download/get_token.cgi"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"url": f"https://1fichier.com/?{file_id}"}

    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()
    data = r.json()
    return data.get("url", f"https://1fichier.com/?{file_id}")

def main():
    print("Fetching files from 1fichier folder...")
    files = get_folder_files()

    if not files:
        print("No files found in folder.")
        return

    result = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    }

    for f in files:
        name = f.get("filename", "")
        file_id = f.get("code", "")
        size = f.get("size", 0)
        size_mb = round(size / (1024 * 1024), 1) if size else 0

        print(f"Found: {name}")

        # Detectar versión desde el nombre: [vXXXXXXXX]
        version = ""
        if "[v" in name and "]" in name:
            start = name.index("[v") + 1
            end = name.index("]", start)
            version = name[start:end]

        download_url = f"https://1fichier.com/?{file_id}"

        if "[Base]" in name or "[base]" in name:
            result["url_base"] = download_url
            result["filename_base"] = name
            result["version_base"] = version
            result["size_base"] = f"{size_mb} MB"
        elif "[Update]" in name or "[update]" in name:
            result["url_update"] = download_url
            result["filename_update"] = name
            result["version_update"] = version
            result["size_update"] = f"{size_mb} MB"

    if "url_base" not in result and "url_update" not in result:
        print("Warning: Could not identify base or update files.")
        print("Files found:", [f.get("filename") for f in files])
        return

    with open("links.json", "w", encoding="utf-8") as fp:
        json.dump(result, fp, indent=2, ensure_ascii=False)

    print("links.json updated successfully:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
