import os
import json
import time
import base64
import requests
from generate_image import generate

ACCESS_TOKEN = os.environ["INSTAGRAM_ACCESS_TOKEN"]
USER_ID      = os.environ["INSTAGRAM_USER_ID"]
IMGBB_KEY    = os.environ["IMGBB_API_KEY"]

# ── 1. Charger la citation du jour ──────────────────────────────────────────
if os.path.exists("daily_quote.json"):
    with open("daily_quote.json", "r", encoding="utf-8") as f:
        quote_data = json.load(f)
    print("📝 Citation chargée depuis daily_quote.json (Claude API)")
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
    print(f"📝 Citation chargée depuis captions.json (index {index})")

name    = quote_data["name"]
quote   = quote_data["quote"]
source  = quote_data["source"]
caption = quote_data.get("caption", f"قَالَ {name} رَحِمَهُ اللَّهُ :\n\n«{quote}»\n\n📖 {source}\n\n#salaf #sunnah #islam #ilm")

print(f"   Nom    : {name}")
print(f"   Source : {source}")

# ── 2. Générer l'image avec le texte superposé ──────────────────────────────
image_path = generate(name=name, quote=quote, source=source)

# ── 3. Héberger l'image sur imgbb pour obtenir une URL publique ─────────────
print("⬆️  Upload de l'image sur imgbb…")
with open(image_path, "rb") as img_file:
    b64 = base64.b64encode(img_file.read()).decode("utf-8")

imgbb_resp = requests.post(
    "https://api.imgbb.com/1/upload",
    data={"key": IMGBB_KEY, "image": b64, "expiration": 600},
)
imgbb_data = imgbb_resp.json()

if not imgbb_data.get("success"):
    raise Exception(f"Erreur imgbb : {imgbb_data}")

image_url = imgbb_data["data"]["url"]
print(f"🔗 URL publique : {image_url}")

# ── 4. Créer le container media Instagram ───────────────────────────────────
print("📤 Création du container Instagram…")
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
print("⏳ Attente de 10 secondes…")
time.sleep(10)

# ── 6. Publier ──────────────────────────────────────────────────────────────
print("🚀 Publication…")
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

print(f"✅ Publication réussie ! Post ID : {publish_data['id']}")
print(f"   Caption : {caption[:80]}…")

# ── 7. Nettoyage ─────────────────────────────────────────────────────────────
if os.path.exists("daily_quote.json"):
    os.remove("daily_quote.json")
if os.path.exists("output.jpg"):
    os.remove("output.jpg")
