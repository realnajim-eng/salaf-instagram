import os
import json
import time
import requests
from generate_image import generate

ACCESS_TOKEN   = os.environ["INSTAGRAM_ACCESS_TOKEN"]
USER_ID        = os.environ["INSTAGRAM_USER_ID"]
GITHUB_TOKEN   = os.environ["GITHUB_TOKEN"]
REPO           = "realnajim-eng/salaf-instagram"
RELEASE_TAG    = "daily-images"
IMAGE_FILENAME = "temp_post.jpg"

GH_HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}

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

# ── 3. Héberger l'image via GitHub Releases (aucun commit, URL publique) ────
print("Upload de l'image sur GitHub Releases...")

# S'assurer que la release "daily-images" existe
rel_resp = requests.get(
    f"https://api.github.com/repos/{REPO}/releases/tags/{RELEASE_TAG}",
    headers=GH_HEADERS,
)
if rel_resp.status_code == 404:
    rel_resp = requests.post(
        f"https://api.github.com/repos/{REPO}/releases",
        headers=GH_HEADERS,
        json={"tag_name": RELEASE_TAG, "name": "Daily images", "body": "Auto-generated images"},
    )
release_id = rel_resp.json()["id"]

# Supprimer l'asset existant s'il y en a un (même nom)
assets_resp = requests.get(
    f"https://api.github.com/repos/{REPO}/releases/{release_id}/assets",
    headers=GH_HEADERS,
)
for asset in assets_resp.json():
    if asset["name"] == IMAGE_FILENAME:
        requests.delete(
            f"https://api.github.com/repos/{REPO}/releases/assets/{asset['id']}",
            headers=GH_HEADERS,
        )

# Uploader l'image comme asset de la release
with open(image_path, "rb") as f:
    upload_resp = requests.post(
        f"https://uploads.github.com/repos/{REPO}/releases/{release_id}/assets?name={IMAGE_FILENAME}",
        headers={**GH_HEADERS, "Content-Type": "image/jpeg"},
        data=f,
    )

if upload_resp.status_code not in (200, 201):
    raise Exception(f"Erreur upload GitHub Release : {upload_resp.json()}")

image_url = upload_resp.json()["browser_download_url"]
print(f"URL publique : {image_url}")

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
