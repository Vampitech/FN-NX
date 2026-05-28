import os
import json
import requests
from datetime import datetime, timezone

API_KEY   = os.environ["FICHIER_API_KEY"]
FOLDER_ID = 20447254

HEADERS = {
    "Content-Type":  "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

def list_folder():
    r = requests.post(
        "https://api.1fichier.com/v1/folder/ls.cgi",
        headers=HEADERS,
        json={"folder_id": FOLDER_ID, "files": 1},
        timeout=15
    )
    r.raise_for_status()
    data = r.json()
    if data.get("status") == "KO":
        raise RuntimeError(f"1fichier error: {data.get('message')}")
    return data.get("items", [])

def main():
    print("Fetching files from 1fichier folder FN...")
    files = list_folder()

    if not files:
        print("No files found in folder.")
        return

    print(f"Found {len(files)} file(s):")
    for f in files:
        print(f"  {f.get('filename')}  —  {f.get('url')}")

    result = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    }

    for f in files:
        name = f.get("filename", "")
        url  = f.get("url", "")
        size = f.get("size", 0)
        size_gb = round(size / (1024 ** 3), 2) if size else 0

        # Extraer versión desde el nombre: [vXXXXXXXX]
        version = ""
        if "[v" in name and "]" in name:
            start = name.index("[v") + 1
            end   = name.index("]", start)
            version = name[start:end]

        if "[Base]" in name:
            result["url_base"]      = url
            result["filename_base"] = name
            result["version_base"]  = version
            result["size_base"]     = f"{size_gb} GB"
        elif "[Update]" in name:
            result["url_update"]      = url
            result["filename_update"] = name
            result["version_update"]  = version
            result["size_update"]     = f"{size_gb} GB"

    if "url_base" not in result:
        print("WARNING: base file not found — check filename contains '[Base]'")
    if "url_update" not in result:
        print("WARNING: update file not found — check filename contains '[Update]'")

    with open("links.json", "w", encoding="utf-8") as fp:
        json.dump(result, fp, indent=2, ensure_ascii=False)

    print("\nlinks.json updated:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
