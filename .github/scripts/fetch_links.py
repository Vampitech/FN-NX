import os
import json
import requests
from datetime import datetime, timezone

API_KEY = os.environ["FICHIER_API_KEY"]
FOLDER_SLUG = "W1fFILam"

def post(label, url, payload, headers):
    print(f"\n--- {label} ---")
    r = requests.post(url, headers=headers, json=payload, timeout=15)
    print(f"  Status: {r.status_code}")
    try:
        print(f"  Response: {json.dumps(r.json(), indent=2)[:800]}")
    except Exception:
        print(f"  Response (raw): {r.text[:400]}")
    return r

def main():
    key_preview = API_KEY[:6] + "..." + API_KEY[-4:] if len(API_KEY) > 10 else "(muy corta?)"
    print(f"API key preview: {key_preview}  (len={len(API_KEY)})")

    # Formato 1: Bearer con comillas (como muestra la doc de 1fichier literalmente)
    h1 = {"Content-Type": "application/json", "Authorization": f'Bearer "{API_KEY}"'}
    # Formato 2: Bearer sin comillas (estándar)
    h2 = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    # Formato 3: solo la key como valor
    h3 = {"Content-Type": "application/json", "Authorization": API_KEY}

    payload = {}  # root, empty hash como indica la doc

    r1 = post("Bearer con comillas", "https://api.1fichier.com/v1/folder/ls.cgi", payload, h1)
    if r1.status_code == 200:
        print("\n✓ Formato 1 funciona (Bearer con comillas)")
        return

    r2 = post("Bearer sin comillas", "https://api.1fichier.com/v1/folder/ls.cgi", payload, h2)
    if r2.status_code == 200:
        print("\n✓ Formato 2 funciona (Bearer sin comillas)")
        return

    r3 = post("Solo la key", "https://api.1fichier.com/v1/folder/ls.cgi", payload, h3)
    if r3.status_code == 200:
        print("\n✓ Formato 3 funciona (key directa)")
        return

    print("\n✗ Ningún formato funcionó.")
    print("Verifica que la API key sea correcta y tenga permisos de lectura de carpetas.")

if __name__ == "__main__":
    main()
