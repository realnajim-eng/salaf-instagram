import os
import json
import random
import anthropic

QUOTES_DB = "quotes_salaf.json"
TRACKER   = "tracker.json"

# ── 1. Charger la base de données dorar.net ──────────────────────────────────
if os.path.exists(QUOTES_DB):
    with open(QUOTES_DB, "r", encoding="utf-8") as f:
        db = json.load(f)

    # Éviter de répéter la même citation (suivi via tracker)
    if os.path.exists(TRACKER):
        with open(TRACKER, "r", encoding="utf-8") as f:
            tracker = json.load(f)
    else:
        tracker = {}

    used = set(tracker.get("used_quotes", []))
    available = [q for q in db if q["quote_ar"] not in used]

    if not available:
        # Tout a été utilisé — recommencer depuis le début
        available = db
        tracker["used_quotes"] = []

    quote_data = random.choice(available)

    # Marquer comme utilisé
    tracker.setdefault("used_quotes", []).append(quote_data["quote_ar"])
    with open(TRACKER, "w", encoding="utf-8") as f:
        json.dump(tracker, f, ensure_ascii=False, indent=2)

    print(f"✅ Citation chargée depuis quotes_salaf.json (dorar.net)")
    print(f"   Nom        : {quote_data['name']}")
    print(f"   Génération : {quote_data.get('generation','?')} | Catégorie : {quote_data.get('category','?')}")
    print(f"   Source     : {quote_data['source']}")
    print(f"   Extrait    : {quote_data['quote'][:80]}…")

# ── 2. Fallback : Claude API (si quotes_salaf.json absent) ───────────────────
else:
    print("⚠️  quotes_salaf.json introuvable — fallback vers Claude API")

    THEMES = [
        ("الصَّبْر", "patience"), ("الزُّهْد", "zuhd"), ("الْإِخْلَاص", "ikhlas"),
        ("التَّوَكُّل", "tawakkul"), ("الْخَشْيَة", "khashya"), ("الْعِلْم", "ilm"),
        ("الْعَمَل الصَّالِح", "amal_salih"), ("الذِّكْر", "dhikr"),
        ("التَّوْبَة", "tawba"), ("الْوَرَع", "wara"),
    ]
    theme_ar, theme_lat = random.choice(THEMES)
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    prompt = f"""Tu es un spécialiste des paroles authentiques des Salaf as-Salih.
RÈGLES ABSOLUES : cite uniquement une parole réelle des 3 premières générations avec source précise (livre + référence).
Thème : {theme_ar} ({theme_lat})

---JSON---
{{
  "name_ar": "...", "name": "...", "generation": "sahabi|tabiʿi|atba",
  "category": "mawquf|maqtuʿ", "quote_ar": "...", "quote": "traduction française",
  "source_ar": "...", "source": "...", "theme": "{theme_lat}",
  "caption": "« [quote] »\\n\\n— [name] (rahimahullah)\\n📖 [source]\\n\\n#{theme_lat} #salaf #sunnah #islam #salafiyyah #ilm #UnJourUnSalaf"
}}
---END_JSON---"""

    message = client.messages.create(model="claude-sonnet-4-6", max_tokens=1500,
        messages=[{"role": "user", "content": prompt}])
    response = message.content[0].text

    if "---JSON---" in response:
        start = response.find("---JSON---") + 10
        end   = response.find("---END_JSON---")
        raw   = response[start:end].strip()
    elif "```json" in response:
        start = response.find("```json") + 7
        end   = response.find("```", start)
        raw   = response[start:end].strip()
    else:
        raw = response.strip()

    quote_data = json.loads(raw)
    print(f"✅ Citation générée via Claude API (thème : {theme_ar})")

# ── 3. Sauvegarder pour post_salaf.py ────────────────────────────────────────
with open("daily_quote.json", "w", encoding="utf-8") as f:
    json.dump(quote_data, f, ensure_ascii=False, indent=2)
