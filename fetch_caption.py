import os
import random
import anthropic

THEMES = [
    ("patience", "patience"),
    ("zuhd (détachement du monde)", "zuhd"),
    ("sincérité (ikhlas)", "ikhlas"),
    ("confiance en Allah (tawakkul)", "tawakkul"),
    ("crainte d'Allah (khashya)", "khashya"),
    ("la science et la connaissance", "ilm"),
    ("les bonnes oeuvres", "amal_salih"),
    ("le rappel d'Allah (dhikr)", "dhikr"),
    ("le repentir (tawba)", "tawba"),
    ("le détachement de la dunya", "zuhd_dunya"),
    ("l'innovation blâmable (bid'ah)", "bidah"),
    ("la véracité (sidq)", "sidq"),
    ("l'humilité", "tawadu"),
    ("la mort et l'au-delà", "akhira"),
]

theme_fr, theme_lat = random.choice(THEMES)

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

prompt = f"""Tu es un expert en sciences islamiques spécialisé dans les paroles des Salaf al-Salih.

Donne-moi une parole authentique d'un Salaf (Compagnon, Tabi'i ou Atba' al-Tabi'in) sur le thème : {theme_fr}

Règles absolues :
- Uniquement en FRANÇAIS (pas de texte arabe)
- Mentionner clairement QUI a dit cette parole (prénom complet du Salaf)
- Source réelle et connue (nom du livre)
- Ne jamais inventer — uniquement des paroles vérifiées et connues
- Si incertain, choisir une parole très célèbre et bien attestée

Réponds UNIQUEMENT avec ce format exact, sans aucun texte supplémentaire :

---CAPTION---
📚 Parole de [Prénom complet du Salaf] — [رَضِيَ اللَّهُ عَنْهُ si Compagnon / رَحِمَهُ اللَّهُ si Tabi'i ou savant]

« [Traduction française fidèle et complète de la parole] »

📖 Source : [Nom du livre]

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

print(f"✅ Légende générée (thème : {theme_fr})")
print("-" * 50)
print(caption)
