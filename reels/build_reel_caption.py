#!/usr/bin/env python3
"""
build_reel_caption.py — Légende Instagram pour le Reel du jour.

Construite à partir du verset (current_verse.json). On ne saisit jamais le texte
coranique de mémoire : il provient des données authentifiées de verses.json.

Format : traduction du sens + référence + crédits (récitation / traduction) +
hashtags francophones variés et spécifiques au thème (Instagram pénalise la
répétition exacte des mêmes hashtags).
"""
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))

# Identité du compte : toujours présents.
CORE = ["#coran", "#quran", "#islamfr", "#rappelislamique"]

# Découverte francophone (cœur de l'audience).
FR = [
    "#islam", "#rappel", "#musulman", "#musulmane", "#islamfrance",
    "#religionislam", "#foimusulmane", "#musulmansdefrance", "#coranfr",
    "#versetducoran", "#paroledallah", "#mediterlecoran", "#spiritualite",
    "#recitationcoran", "#tajwid",
]

# Hashtags spécifiques au thème du verset (français uniquement).
THEME_TAGS = {
    "coran":    ["#leliredallah", "#mushaf", "#parolededieu"],
    "tawhid":   ["#tawhid", "#unicite", "#aqida"],
    "patience": ["#patience", "#sabr", "#endurance"],
    "jugement": ["#jourdujugement", "#audela", "#rappeldelamort"],
    "temps":    ["#letemps", "#viedicibas", "#mediter"],
}

# Phrase d'accroche sobre par thème (première ligne, en français).
HOOK = {
    "coran":    "📖 Médite la Parole d'Allah",
    "tawhid":   "☝️ L'unicité d'Allah",
    "patience": "🤲 La patience (aṣ-ṣabr)",
    "jugement": "⚖️ Le Jour du Jugement",
    "temps":    "⏳ Le temps qui passe",
}


def _hashtags(theme):
    tags = list(CORE) + random.sample(FR, 7) + THEME_TAGS.get(theme, [])
    seen, out = set(), []
    for t in tags:
        if t.lower() not in seen:
            seen.add(t.lower())
            out.append(t)
    return out[:20]


def build_caption(v):
    theme = v.get("theme", "")
    hook = HOOK.get(theme, "📖 Verset du Coran")
    body = (
        f"{hook}\n\n"
        f"﴿ {v['verse_ar']} ﴾\n\n"
        f"« {v['translation']} »\n\n"
        f"— {v['ref']}\n"
        f"🎙️ Récitation : Mishary al-ʿAfāsī · Traduction du sens : Hamidullah"
    )
    return f"{body}\n\n{' '.join(_hashtags(theme))}"


if __name__ == "__main__":
    v = json.load(open(os.path.join(HERE, "current_verse.json"), encoding="utf-8"))
    print(build_caption(v))
