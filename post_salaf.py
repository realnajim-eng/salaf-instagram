import os
import json
import time
import subprocess
import requests
from generate_image import generate

ACCESS_TOKEN = os.environ["INSTAGRAM_ACCESS_TOKEN"]
USER_ID      = os.environ["INSTAGRAM_USER_ID"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
REPO         = "realnajim-eng/salaf-instagram"
IMAGE_FILENAME = "temp_post.jpg"

# ── 1. Charger la citation du jour ──────────────────────────────────────────
if os.path.exists("daily_quote.json"):
    with open("daily_quote.json", "r", encoding="utf-8") as f:
        quote_data = json.load(f)
    print("Citation chargée depuis daily_quote.json (Claude API)")
else:
    with open("captions.json", "r", encoding="utf-8") as f:
        captions = json.load(f)
    with open("tracker.json", "r", encoding="utf-8") as f:
        tracker = json.load(f)
    index = (tracker.get("last_index", -1) + 1) % len(captions)
    quote_data = captions[index]
    tracker["last_index"] = index
    with open("tracker.json", "w", encoding="utf-8") as f:
        json.dump(tracker, f, ensure_ascii=False, indent=2)
    print(f"Citation chargée depuis captions.json (index {index})")

name    = quote_data["name"]
quote   = quote_data["quote"]
source  = quote_data["source"]
caption = quote_data.get("caption", f"« {quote} »\n\n— {name}\n📖 {source}\n\n#salaf #sunnah #islam #ilm")

print(f"   Nom    : {name}")
print(f"   Source : {source}")

# ── 2. Générer l'image ──────────────────────────────────────────────────────
image_path = generate(name=name, quote=quote, source=source, output_path=IMAGE_FILENAME)

# ── 3. Pousser l'image sur GitHub pour obtenir une URL publique ─────────────
print("Upload de l'image sur GitHub...")
import base64
with open(image_path, "rb") as f:
    b64_content = base64.b64encode(f.read()).decode("utf-8")

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}

# Vérifier si le fichier existe déjà (pour récupérer son SHA)
check = requests.get(
    f"https://api.github.com/repos/{REPO}/contents/{IMAGE_FILENAME}",
    headers=headers,
)
sha = check.json().get("sha") if check.status_code == 200 else None

payload = {
    "message": "temp: image du jour",
    "content": b64_content,
}
if sha:
    payload["sha"] = sha

upload_resp = requests.put(
    f"https://api.github.com/repos/{REPO}/contents/{IMAGE_FILENAME}",
    headers=headers,
    json=payload,
)
if upload_resp.status_code not in (200, 201):
    raise Exception(f"Erreur upload GitHub : {upload_resp.json()}")

# URL raw publique (CDN GitHub)
image_url = f"https://raw.githubusercontent.com/{REPO}/main/{IMAGE_FILENAME}?t={int(time.time())}"
print(f"URL publique : {image_url}")

# Attendre que GitHub propage l'image
time.sleep(5)

# ── 4. Créer le container media Instagram ───────────────────────────────────
print("Création du container Instagram...")
create_resp = requests.post(
    f"https://graph.instagram.com/v21.0/{USER_ID}/media",
    data={
        "image_url": image_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN,
    },
)
create_data = create_resp.json()
print("Create media response:", create_data)

if "id" not in create_data:
    raise Exception(f"Erreur création media : {create_data}")

creation_id = create_data["id"]

# ── 5. Attendre que le media soit prêt ──────────────────────────────────────
print("Attente de 10 secondes...")
time.sleep(10)

# ── 6. Publier ──────────────────────────────────────────────────────────────
print("Publication...")
publish_resp = requests.post(
    f"https://graph.instagram.com/v21.0/{USER_ID}/media_publish",
    data={
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN,
    },
)
publish_data = publish_resp.json()
print("Publish response:", publish_data)

if "id" not in publish_data:
    raise Exception(f"Erreur publication : {publish_data}")

print(f"Publication réussie ! Post ID : {publish_data['id']}")

# ── 7. Nettoyage ─────────────────────────────────────────────────────────────
if os.path.exists("daily_quote.json"):
    os.remove("daily_quote.json")
if os.path.exists(IMAGE_FILENAME):
    os.remove(IMAGE_FILENAME)
