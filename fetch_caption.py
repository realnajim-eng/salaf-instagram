import os
import json
import random
import anthropic

THEMES = [
    ("الصَّبْر", "patience"),
    ("الزُّهْد", "zuhd"),
    ("الْإِخْلَاص", "ikhlas"),
    ("التَّوَكُّل", "tawakkul"),
    ("الْخَشْيَة", "khashya"),
    ("الْعِلْم", "ilm"),
    ("الْعَمَل الصَّالِح", "amal_salih"),
    ("الذِّكْر", "dhikr"),
    ("التَّوْبَة", "tawba"),
    ("الزُّهْد فِي الدُّنْيَا", "zuhd_dunya"),
    ("الْبِدْعَة", "bidah"),
    ("الصِّدْق", "sidq"),
]

theme_ar, theme_lat = random.choice(THEMES)

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

prompt = f"""You are a scholar specialised in the sayings of the Salaf as-Salih.

I need an authentic narration from the Salaf (Companions, Tabi'in or Atba' at-Tabi'in) on the theme: {theme_ar} ({theme_lat})

Strict rules:
- The quote must be a real, well-known saying — do not invent anything
- "name": scholar's name transliterated in French (e.g. "Ibn al-Qayyim", "Al-Hasan al-Basri")
- "quote": faithful French translation of the saying
- "source": book name transliterated in French (e.g. "Madarij as-Salikin")
- "caption": the full Instagram caption in French with hashtags

Reply with ONLY this JSON, no extra text:

---JSON---
{{
  "name": "Scholar name in French transliteration",
  "quote": "Faithful French translation of the saying",
  "source": "Book name in French transliteration",
  "theme": "{theme_lat}",
  "caption": "« [French quote] »\\n\\n— [name] (rahimahullah)\\n📖 [source]\\n\\n#salaf #sunnah #islam #{theme_lat} #salafiyyah #ilm"
}}
---END_JSON---
"""

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": prompt}],
)

response = message.content[0].text

# Accepte ---JSON--- / ---END_JSON--- ou ```json ... ``` ou JSON brut
if "---JSON---" in response and "---END_JSON---" in response:
    start = response.find("---JSON---") + len("---JSON---")
    end   = response.find("---END_JSON---")
    raw   = response[start:end].strip()
elif "```json" in response:
    start = response.find("```json") + len("```json")
    end   = response.find("```", start)
    raw   = response[start:end].strip()
elif "```" in response:
    start = response.find("```") + 3
    end   = response.find("```", start)
    raw   = response[start:end].strip()
else:
    raw = response.strip()

data = json.loads(raw)

with open("daily_quote.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ Citation générée (thème : {theme_ar})")
print(f"   Nom    : {data['name']}")
print(f"   Source : {data['source']}")
print(f"   Extrait: {data['quote'][:60]}…")
