#!/usr/bin/env python3
"""
post_reel.py — Publie le Reel du jour sur Instagram.

Reprend le mécanisme de post_salaf.py (renouvellement du token, hébergement via
GitHub Releases pour obtenir une URL publique, polling du container) mais pour
une VIDÉO publiée en tant que Reel (media_type=REELS).

Pré-requis (produits par les étapes précédentes du workflow) :
  reels/out/daily_reel.mp4   — vidéo rendue par Remotion
  reels/current_verse.json   — verset du jour (légende)

Met à jour reels/posted_reels.json en fin de publication.
"""
import os
import json
import time
import base64
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from nacl import encoding, public

from build_reel_caption import build_caption

ACCESS_TOKEN  = os.environ["INSTAGRAM_ACCESS_TOKEN"]
USER_ID       = os.environ["INSTAGRAM_USER_ID"]
GITHUB_TOKEN  = os.environ["GITHUB_TOKEN"]
SECRETS_TOKEN = os.environ.get("GH_PAT") or GITHUB_TOKEN
REPO          = "realnajim-eng/salaf-instagram"
RELEASE_TAG   = "daily-reels"
VIDEO_NAME    = "daily_reel.mp4"

HERE       = os.path.dirname(os.path.abspath(__file__))
VIDEO_PATH = os.path.join(HERE, "out", VIDEO_NAME)
CURRENT    = os.path.join(HERE, "current_verse.json")
TRACKER    = os.path.join(HERE, "posted_reels.json")

GH_HEADERS = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}
GH_SECRETS_HEADERS = {"Authorization": f"token {SECRETS_TOKEN}", "Accept": "application/vnd.github+json"}
TIMEOUT = (10, 120)


def make_session():
    session = requests.Session()
    retry = Retry(total=4, backoff_factor=2,
                  status_forcelist=(429, 500, 502, 503, 504),
                  allowed_methods=("GET", "POST", "PUT", "DELETE"),
                  raise_on_status=False)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


http = make_session()


# ── 0. Renouveler le token Instagram (expire tous les 60 jours) ──────────────
def refresh_instagram_token(token):
    resp = http.get("https://graph.instagram.com/refresh_access_token",
                    params={"grant_type": "ig_refresh_token", "access_token": token},
                    timeout=TIMEOUT)
    data = resp.json()
    if "access_token" in data:
        print(f"✅ Token Instagram renouvelé (expire dans {data.get('expires_in', 0) // 86400} jours)")
        return data["access_token"]
    print(f"⚠️  Renouvellement token échoué : {data}")
    return token


def update_github_secret(name, value):
    key_resp = http.get(f"https://api.github.com/repos/{REPO}/actions/secrets/public-key",
                        headers=GH_SECRETS_HEADERS, timeout=TIMEOUT)
    key_data = key_resp.json()
    if "key" not in key_data:
        raise RuntimeError(f"Clé publique inaccessible (HTTP {key_resp.status_code}) : {key_data}. "
                           "Fournis un PAT dans le secret GH_PAT (Secrets: read & write).")
    pk = public.PublicKey(key_data["key"].encode("utf-8"), encoding.Base64Encoder())
    encrypted = base64.b64encode(public.SealedBox(pk).encrypt(value.encode("utf-8"))).decode("utf-8")
    put = http.put(f"https://api.github.com/repos/{REPO}/actions/secrets/{name}",
                   headers=GH_SECRETS_HEADERS,
                   json={"encrypted_value": encrypted, "key_id": key_data["key_id"]},
                   timeout=TIMEOUT)
    if put.status_code in (201, 204):
        print(f"✅ Secret GitHub '{name}' mis à jour")
    else:
        raise RuntimeError(f"Mise à jour secret échouée : {put.status_code} {put.text}")


try:
    new_token = refresh_instagram_token(ACCESS_TOKEN)
    if new_token != ACCESS_TOKEN:
        ACCESS_TOKEN = new_token
        try:
            update_github_secret("INSTAGRAM_ACCESS_TOKEN", new_token)
        except Exception as e:
            print(f"⚠️  Persistance du nouveau token échouée (publication poursuivie) : {e}")
except Exception as e:
    print(f"⚠️  Renouvellement du token échoué (publication avec l'ancien token) : {e}")


# ── 1. Charger le verset du jour + construire la légende ─────────────────────
if not os.path.exists(VIDEO_PATH):
    raise SystemExit(f"{VIDEO_PATH} introuvable — le rendu Remotion a-t-il réussi ?")
if not os.path.exists(CURRENT):
    raise SystemExit(f"{CURRENT} introuvable — pick_verse.py a-t-il été exécuté ?")

verse = json.load(open(CURRENT, encoding="utf-8"))
caption = build_caption(verse)
print(f"Verset : {verse['theme']} — {verse['ref']}")


# ── 2. Héberger la vidéo via GitHub Releases (URL publique) ──────────────────
print("Upload de la vidéo sur GitHub Releases...")
rel = http.get(f"https://api.github.com/repos/{REPO}/releases/tags/{RELEASE_TAG}",
               headers=GH_HEADERS, timeout=TIMEOUT)
if rel.status_code == 404:
    rel = http.post(f"https://api.github.com/repos/{REPO}/releases",
                    headers=GH_HEADERS,
                    json={"tag_name": RELEASE_TAG, "name": "Daily reels", "body": "Auto-generated reels"},
                    timeout=TIMEOUT)
release_id = rel.json()["id"]

# Supprimer l'asset précédent (même nom) pour le remplacer.
assets = http.get(f"https://api.github.com/repos/{REPO}/releases/{release_id}/assets",
                  headers=GH_HEADERS, timeout=TIMEOUT)
for asset in assets.json():
    if asset["name"] == VIDEO_NAME:
        http.delete(f"https://api.github.com/repos/{REPO}/releases/assets/{asset['id']}",
                    headers=GH_HEADERS, timeout=TIMEOUT)

with open(VIDEO_PATH, "rb") as f:
    up = http.post(
        f"https://uploads.github.com/repos/{REPO}/releases/{release_id}/assets?name={VIDEO_NAME}",
        headers={**GH_HEADERS, "Content-Type": "video/mp4"}, data=f, timeout=TIMEOUT)
if up.status_code not in (200, 201):
    raise Exception(f"Erreur upload GitHub Release : {up.json()}")
video_url = up.json()["browser_download_url"]
print(f"URL publique : {video_url}")


# ── 3. Créer le container Reel ───────────────────────────────────────────────
print("Création du container Reel...")
create = http.post(f"https://graph.instagram.com/v21.0/{USER_ID}/media",
                   data={"media_type": "REELS", "video_url": video_url,
                         "caption": caption, "share_to_feed": "true",
                         "access_token": ACCESS_TOKEN},
                   timeout=TIMEOUT)
create_data = create.json()
print("Create media response:", create_data)
if "id" not in create_data:
    raise Exception(f"Erreur création media : {create_data}")
creation_id = create_data["id"]


# ── 4. Attendre la fin du traitement vidéo (les Reels prennent du temps) ─────
print("Attente du traitement de la vidéo...")
MAX_ATTEMPTS, POLL_DELAY = 40, 10   # jusqu'à ~6,5 min
for attempt in range(1, MAX_ATTEMPTS + 1):
    st = http.get(f"https://graph.instagram.com/v21.0/{creation_id}",
                  params={"fields": "status_code", "access_token": ACCESS_TOKEN},
                  timeout=TIMEOUT)
    status_code = st.json().get("status_code")
    print(f"   Tentative {attempt}/{MAX_ATTEMPTS} : status = {status_code}")
    if status_code == "FINISHED":
        break
    if status_code == "ERROR":
        raise Exception(f"Container Instagram en ERROR : {st.json()}")
    time.sleep(POLL_DELAY)
else:
    raise Exception("Container Reel non prêt après le délai maximum")


# ── 5. Publier ───────────────────────────────────────────────────────────────
print("Publication...")
pub = http.post(f"https://graph.instagram.com/v21.0/{USER_ID}/media_publish",
                data={"creation_id": creation_id, "access_token": ACCESS_TOKEN},
                timeout=TIMEOUT)
pub_data = pub.json()
print("Publish response:", pub_data)
if "id" not in pub_data:
    raise Exception(f"Erreur publication : {pub_data}")
print(f"Publication réussie ! Reel ID : {pub_data['id']}")


# ── 6. Mettre à jour l'historique ────────────────────────────────────────────
posted = []
if os.path.exists(TRACKER):
    posted = json.load(open(TRACKER, encoding="utf-8")).get("posted", [])
if verse["ref"] not in posted:
    posted.append(verse["ref"])
json.dump({"posted": posted}, open(TRACKER, "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print(f"Historique mis à jour ({len(posted)} reels publiés).")
