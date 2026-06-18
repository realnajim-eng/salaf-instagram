import os
import json
import requests

ACCESS_TOKEN = os.environ["INSTAGRAM_ACCESS_TOKEN"]
USER_ID = os.environ["INSTAGRAM_USER_ID"]

with open("captions.json", "r", encoding="utf-8") as f:
    captions = json.load(f)

with open("tracker.json", "r", encoding="utf-8") as f:
    tracker = json.load(f)

index = tracker.get("last_index", -1) + 1
if index >= len(captions):
    index = 0

caption = captions[index]

# Image islamique publique sur picsum (JPEG valide, approuve par Instagram)
# On utilise une image de nature/calme qui correspond a l'ambiance spirituelle
IMAGE_URL = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1080&h=1080&fit=crop&auto=format"

# Etape 1: Creer le container media
create_url = f"https://graph.instagram.com/v21.0/{USER_ID}/media"
create_resp = requests.post(create_url, data={
    "image_url": IMAGE_URL,
    "caption": caption,
    "access_token": ACCESS_TOKEN
})
create_data = create_resp.json()
print("Create media response:", create_data)

if "id" not in create_data:
    raise Exception(f"Erreur creation media: {create_data}")

creation_id = create_data["id"]

# Etape 2: Publier le media
publish_url = f"https://graph.instagram.com/v21.0/{USER_ID}/media_publish"
publish_resp = requests.post(publish_url, data={
    "creation_id": creation_id,
    "access_token": ACCESS_TOKEN
})
publish_data = publish_resp.json()
print("Publish response:", publish_data)

if "id" not in publish_data:
    raise Exception(f"Erreur publication: {publish_data}")

print(f"Publication reussie ! Post ID: {publish_data['id']}")
print(f"Caption publiee: {caption[:80]}...")

# Mettre a jour le tracker
tracker["last_index"] = index
with open("tracker.json", "w", encoding="utf-8") as f:
    json.dump(tracker, f, ensure_ascii=False, indent=2)

print("Tracker mis a jour.")
