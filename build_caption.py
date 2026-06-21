"""
build_caption.py — Constructeur de légende Instagram optimisée pour la portée.

Reconstruit la `caption` à partir des champs structurés de la citation
(quote, name, source, generation, theme) au lieu de réutiliser une légende
figée. Objectif : croissance organique (visibilité / abonnés).

Principes :

1. **Source épurée** : on ne garde que l'ouvrage (le site et le chapitre sont
   retirés) pour une mention propre et sobre.
2. **Hashtags francophones uniquement et variés** : ~15-18 tags français
   choisis dans des pools, donc jamais strictement identiques d'un jour à
   l'autre — Instagram pénalise la répétition exacte des mêmes hashtags.
"""
import random

# ── Pools de hashtags (français uniquement) ──────────────────────────────────
# Identité du compte : toujours présents (cohérence de marque + tag propre).
CORE = ["#UnJourUnSalaf", "#salaf", "#salafiyyah", "#sunnah"]

# Découverte francophone (cœur de l'audience).
FR = [
    "#islamfr", "#rappelislamique", "#rappel", "#musulman", "#musulmane",
    "#islamfrance", "#religionislam", "#foimusulmane", "#musulmansdefrance",
    "#savoirislamique", "#piqurederappel", "#tawhid", "#minhajsalaf",
    "#parolesdesages", "#coranfr",
]

# Hashtags spécifiques au thème de la parole (français uniquement).
THEME = {
    "patience":   ["#patience"],
    "zuhd":       ["#renoncement"],
    "ilm":        ["#scienceislamique"],
    "samt":       ["#langue", "#silence"],
    "ikhlas":     ["#sincerite"],
    "amal_salih": ["#bonnesoeuvres"],
    "amal":       ["#bonnesoeuvres"],
    "wara":       ["#scrupule"],
    "ittiba":     ["#suivrelasunna"],
    "khashya":    ["#craintedallah"],
    "khawf":      ["#craintedallah"],
    "hawa":       ["#manhaj"],
    "sunnah":     ["#manhaj"],
    "bidah":      ["#manhaj"],
    "haqq":       ["#verite"],
    "manhaj":     ["#manhaj"],
    "adab":       ["#comportement"],
    "insaf":      ["#equite"],
    "salat":      ["#priere"],
    "ibada":      ["#adoration"],
    "jihad":      ["#effortsursoi"],
    "dhikr":      ["#rappeldallah"],
    "husn-dhann": ["#bonneopinion"],
    "muhasaba":   ["#introspection"],
    "hikma":      ["#sagesse"],
    "langue":     ["#langue", "#silence"],
    "dua":        ["#invocation"],
    "afw":        ["#pardon"],
}


def _honorific(generation):
    # Compagnon -> radiallahu anhu ; Tabiʿi / Atbaʿ -> rahimahullah.
    return "(radiallahu anhu)" if generation == "sahabi" else "(rahimahullah)"


def clean_source(source):
    """Ne garde que l'ouvrage : retire le site (après le tiret) et le chapitre."""
    s = (source or "").strip()
    if not s:
        return s
    # Couper le site (après un tiret cadratin/demi-cadratin/court).
    for sep in (" — ", " – ", " - "):
        if sep in s:
            s = s.split(sep, 1)[0]
            break
    # Couper la précision après une virgule (chapitre, tome/page, etc.).
    s = s.split(",", 1)[0]
    return s.strip()


def _hashtags(theme):
    tags = list(CORE)
    tags += random.sample(FR, 6)
    tags += THEME.get(theme, [])
    # Dédoublonner en conservant l'ordre, puis plafonner.
    seen, out = set(), []
    for t in tags:
        key = t.lower()
        if key not in seen:
            seen.add(key)
            out.append(t)
    return out[:20]


def build_caption(q):
    """Construit la légende complète à partir d'une entrée de citation."""
    quote = q.get("quote", "").strip()
    name = q.get("name", "").strip()
    source = clean_source(q.get("source", ""))
    honor = _honorific(q.get("generation", ""))
    tags = " ".join(_hashtags(q.get("theme", "")))

    body = f"« {quote} »\n\n— {name} {honor}"
    if source:
        body += f"\n📖 {source}"
    return f"{body}\n\n{tags}"


if __name__ == "__main__":
    # Démo rapide
    import json
    db = json.load(open("quotes_salaf.json", encoding="utf-8"))
    for q in random.sample(db, 3):
        print("─" * 60)
        print(build_caption(q))
