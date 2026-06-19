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
    ("الْخَوْف مِنَ اللَّه", "khawf"),
    ("الرَّجَاء", "raja"),
    ("التَّوَاضُع", "tawadu"),
    ("الصَّمْت وَحِفْظ اللِّسَان", "samt"),
    ("مُجَاهَدَة النَّفْس", "mujahada"),
    ("حُبّ الْآخِرَة", "hubb_akhira"),
    ("الاسْتِغْفَار", "istighfar"),
    ("الْوَرَع", "wara"),
]

theme_ar, theme_lat = random.choice(THEMES)

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

prompt = f"""Tu es un spécialiste des paroles authentiques des Salaf as-Salih (السَّلَفُ الصَّالِح).

RÈGLES ABSOLUES (standards aqwal-salaf) :
1. Cite UNIQUEMENT une parole réelle et vérifiable — JAMAIS d'invention, JAMAIS d'extrapolation
2. La parole doit venir d'un Compagnon (صَحَابِيّ), Tābiʿī ou Atbāʿ at-Tābiʿīn (3 premières générations uniquement)
3. Tu dois citer le LIVRE SOURCE exact avec numéro/tome/page réel
4. Indique la catégorie : مَوْقُوف (Compagnon) ou مَقْطُوع (Tābiʿī/Atbāʿ)

SOURCES CLASSIQUES DE RÉFÉRENCE :
- الزُّهد — ابن المبارك (181 هـ)
- الزُّهد — الإمام أحمد (241 هـ)
- حِلْيَة الأَوْلِيَاء — أبو نُعَيم (430 هـ)
- جَامِع بَيَان العِلم — ابن عبد البر (463 هـ)
- الإِبَانَة الكُبْرَى — ابن بطة (387 هـ)
- شَرْح أُصُول اعتقاد أهل السنة — اللالكائي (418 هـ)
- مَدَارِج السَّالِكِين — ابن القيم (751 هـ)
- سِيَر أَعْلَام النُّبَلَاء — الذهبي (748 هـ)
- الطَّبَقَات الكُبْرَى — ابن سعد (230 هـ)
- الشَّرِيعَة — الآجري (360 هـ)
- السُّنَّة — عبد الله بن أحمد (290 هـ)

Thème demandé : {theme_ar} ({theme_lat})

Réponds UNIQUEMENT avec ce JSON :

---JSON---
{{
  "name_ar": "اسم العالم بالعربية مشكولاً",
  "name": "Nom translittéré en français (ex: Ibn al-Mubarak, Al-Hasan al-Basri)",
  "generation": "sahabi | tabiʿi | atba",
  "category": "mawquf | maqtuʿ",
  "quote_ar": "النص العربي الأصلي",
  "quote": "Traduction française fidèle et littérale",
  "source_ar": "المصدر بالعربية مع الجزء والصفحة أو الرقم",
  "source": "Nom du livre translittéré en français avec référence (ex: Al-Zuhd li-Ibn al-Mubarak, n° 234)",
  "theme": "{theme_lat}",
  "caption": "« [traduction française] »\\n\\n— [name] (rahimahullah)\\n📖 [source]\\n\\n#salaf #sunnah #islam #{theme_lat} #salafiyyah #ilm #UnJourUnSalaf"
}}
---END_JSON---
"""

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1500,
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
print(f"   Nom        : {data['name']}")
print(f"   Génération : {data.get('generation', '?')} | Catégorie : {data.get('category', '?')}")
print(f"   Source     : {data['source']}")
print(f"   Extrait    : {data['quote'][:80]}…")
