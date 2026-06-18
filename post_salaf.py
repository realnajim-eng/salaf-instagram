import os
import json
import time
import requests

ACCESS_TOKEN = os.environ["INSTAGRAM_ACCESS_TOKEN"]
USER_ID = os.environ["INSTAGRAM_USER_ID"]

with open("tracker.json", "r", encoding="utf-8") as f:
    tracker = json.load(f)

# Priorité : légende générée par Claude API (fetch_caption.py)
if os.path.exists("daily_caption.txt"):
    with open("daily_caption.txt", "r", encoding="utf-8") as f:
        caption = f.read().strip()
    print("Légende chargée depuis Claude API")
else:
    with open("captions.json", "r", encoding="utf-8") as f:
        captions = json.load(f)
    index = tracker.get("last_index", -1) + 1
    if index >= len(captions):
        index = 0
    caption = captions[index]
    print(f"Légende chargée depuis captions.json (index {index})")

IMAGE_URL = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1080&h=1080&fit=crop&auto=format"

print("Etape 1 : Creation du container media...")
create_url = f"https://graph.instagram.com/v21.0/{USER_ID}/media"
create_resp = requests.post(create_url, data={
    "image_url": IMAGE_URL,
    "caption": caption,
    "access_token": ACCESS_TOKEN
})
create_data = create_resp.json()
print("Reponse :", create_data)

if "id" not in create_data:
    raise Exception(f"Erreur creation media : {create_data}")

creation_id = create_data["id"]

print("Attente de 10 secondes...")
time.sleep(10)

print("Etape 2 : Publication...")
publish_url = f"https://graph.instagram.com/v21.0/{USER_ID}/media_publish"
publish_resp = requests.post(publish_url, data={
    "creation_id": creation_id,
    "access_token": ACCESS_TOKEN
})
publish_data = publish_resp.json()
print("Reponse :", publish_data)

if "id" not in publish_data:
    raise Exception(f"Erreur publication : {publish_data}")

print(f"Publication reussie ! Post ID : {publish_data['id']}")
print(f"Legende : {caption[:80]}...")

index = tracker.get("last_index", -1) + 1
tracker["last_index"] = index
with open("tracker.json", "w", encoding="utf-8") as f:
    json.dump(tracker, f, ensure_ascii=False, indent=2)

print("Tracker mis a jour.")
