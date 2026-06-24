#!/usr/bin/env python3
"""
pick_verse.py — Choisit le verset du Reel du jour.

Ne retient que les thèmes à fond IMAGE (rendables dans le cloud, assets dans
public/) : paradis & enfer utilisent une vidéo de fond locale absente du dépôt,
donc ils sont exclus du rendu automatique.

Les thèmes sont entrelacés (round-robin) pour qu'un thème ne revienne pas deux
jours de suite. On publie le premier verset non encore publié ; quand les 60
sont épuisés, l'historique repart à zéro.

Sorties :
  reels/render_props.json   — props passées à Remotion (--props)
  reels/current_verse.json  — verset complet (légende + publication)

L'historique est conservé dans reels/posted_reels.json.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
VERSES = os.path.join(HERE, "public", "verses.json")
TRACKER = os.path.join(HERE, "posted_reels.json")
RENDER_PROPS = os.path.join(HERE, "render_props.json")
CURRENT = os.path.join(HERE, "current_verse.json")

# Thèmes à fond image (cf. STILL_IMAGE dans QuoteReel.tsx) — seuls rendables en CI.
IMAGE_THEMES = ["coran", "tawhid", "patience", "jugement", "temps"]

# Champs attendus par le schéma Remotion (verseSchema dans QuoteReel.tsx).
PROP_FIELDS = ("theme", "verse_ar", "translation", "surah_ar", "ref", "audio")


def interleaved(verses):
    """Entrelace les versets par thème (round-robin) pour varier d'un jour à l'autre."""
    by_theme = {t: [v for v in verses if v["theme"] == t] for t in IMAGE_THEMES}
    order, i = [], 0
    while any(by_theme[t][i:] for t in IMAGE_THEMES if len(by_theme[t]) > i):
        for t in IMAGE_THEMES:
            if i < len(by_theme[t]):
                order.append(by_theme[t][i])
        i += 1
    return order


def main():
    verses = [v for v in json.load(open(VERSES, encoding="utf-8"))
              if v["theme"] in IMAGE_THEMES]
    queue = interleaved(verses)

    posted = []
    if os.path.exists(TRACKER):
        posted = json.load(open(TRACKER, encoding="utf-8")).get("posted", [])

    chosen = next((v for v in queue if v["ref"] not in posted), None)
    if chosen is None:  # tout publié → on recommence un cycle
        print("Cycle complet — réinitialisation de l'historique.")
        posted = []
        chosen = queue[0]

    props = {k: chosen[k] for k in PROP_FIELDS}
    json.dump(props, open(RENDER_PROPS, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(chosen, open(CURRENT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print(f"Verset du jour : {chosen['theme']} — {chosen['ref']}")
    print(f"  ({len(posted)}/{len(queue)} déjà publiés)")


if __name__ == "__main__":
    main()
