import os
import json
import requests
from datetime import datetime, timezone

API_KEY = os.environ["FICHIER_API_KEY"]
FOLDER_SLUG = "W1fFILam"  # el slug de la URL pública

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def post(url, payload):
    r = requests.post(url, headers=HEADERS, json=payload, timeout=15)
    print(f"  Status: {r.status_code}")
    try:
        print(f"  Response: {json.dumps(r.json(), indent=2)[:1200]}")
    except Exception:
        print(f"  Response (raw): {r.text[:600]}")
    return r

def find_folder_id(sub_folders, slug):
    """Busca recursivamente la carpeta cuyo 'shared' contiene el slug."""
    for f in sub_folders:
        shared = f.get("shared", "") or ""
        if slug in shared:
            return f["id"], f["name"]
        # si tiene sub-carpetas anidadas
        if f.get("sub_folders"):
            result = find_folder_id(f["sub_folders"], slug)
            if result:
                return result
    return None, None

def main():
    print("=== Step 1: list root folder (id=0) to find numeric folder_id ===\n")
    r = post("https://api.1fichier.com/v1/folder/ls.cgi", {})

    if r.status_code != 200:
        print("Root listing failed. Trying with empty hash as docs suggest...")
        r = post("https://api.1fichier.com/v1/folder/ls.cgi", {"folder_id": 0})

    if r.status_code != 200:
        print("Cannot list root folder. Check API key permissions.")
        return

    data = r.json()
    sub_folders = data.get("sub_folders", [])
    print(f"\nFound {len(sub_folders)} sub-folder(s) in root.")

    # Intentar encontrar el folder por el slug en la URL compartida
    folder_id, folder_name = find_folder_id(sub_folders, FOLDER_SLUG)

    if folder_id:
        print(f"\n✓ Found folder: '{folder_name}' → numeric id = {folder_id}")
    else:
        print("\nCould not auto-detect folder. Listing all sub-folders:")
        for f in sub_folders:
            print(f"  id={f['id']}  name={f['name']}  shared={f.get('shared','')}")
        print("\nIdentify your folder above and hardcode FOLDER_ID in the final script.")
        return

    print(f"\n=== Step 2: list folder {folder_id} with files=1 ===\n")
    r2 = post("https://api.1fichier.com/v1/folder/ls.cgi", {
        "folder_id": folder_id,
        "files": 1
    })

if __name__ == "__main__":
    main()
