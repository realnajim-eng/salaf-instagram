import os
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

prompt = f"""أنتَ عالِمٌ متخصِّصٌ في أَقْوَالِ السَّلَفِ الصَّالِح.

أُريدُ أَثَرًا صَحِيحًا مِن أَقْوَالِ السَّلَفِ (الصَّحَابَة أو التَّابِعِين أو أَتْبَاعِ التَّابِعِين) حَوْلَ مَوْضُوع : {theme_ar}

القواعد المُطلَقة :
- النَّصُّ العربيُّ بِتَشْكِيلٍ كامِلٍ (حَرَكَات كَامِلَة)
- مَصْدَرٌ حَقِيقِيٌّ مَعْرُوف (اسم الكتاب)
- لا تَخْتَرِع أَثَرًا — فقط أَثَرٌ مَشْهُورٌ وَمَعْرُوف
- إِذَا لَمْ تَكُنْ مُتَأَكِّدًا فَاخْتَرْ أَثَرًا مَشْهُورًا جِدًّا

أعطِني الجوابَ بهذا التنسيق الحَرْفي بِدُونِ أَيِّ نَصٍّ إِضَافِيّ :

---CAPTION---
قَالَ [الاسم] [رَضِيَ اللَّهُ عَنْهُ / رَحِمَهُ اللَّهُ] :

«[النص العربي المُشَكَّل]»

📖 [المصدر]

✨ [Traduction française fidèle]

#salaf #sunnah #islam #{theme_lat} #salafiyyah #ilm
---END_CAPTION---
"""

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": prompt}],
)

response = message.content[0].text

start = response.find("---CAPTION---")
end = response.find("---END_CAPTION---")
if start != -1 and end != -1:
    caption = response[start + len("---CAPTION---"):end].strip()
else:
    caption = "📚 Paroles des Salaf\n\n#salaf #sunnah #islam #ilm"

with open("daily_caption.txt", "w", encoding="utf-8") as f:
    f.write(caption)

print(f"✅ Légende générée (thème : {theme_ar})")
print("─" * 50)
print(caption)
