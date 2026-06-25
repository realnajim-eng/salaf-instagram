#!/usr/bin/env python3
"""
Élagage automatique du réservoir de versets (public/verses.json).

Filet de sécurité du réapprovisionnement « tout automatique » : on ne garde
QUE les versets dont le texte (rasm sans tashkīl) contient bien une racine du
thème, et dont la longueur reste compatible avec une belle mise en page de Reel.

- Les versets retenus restent intacts (texte = source authentifiée, jamais
  reconstruit ici).
- Les versets écartés sont retirés de verses.json et leur audio orphelin est
  supprimé de public/audio/.
- Ne touche QUE les thèmes passés en argument (ou ceux de THEME_MARKERS).

Usage :
  python3 prune_verses.py                 # élague les thèmes du réservoir auto
  python3 prune_verses.py rahma tawba     # n'élague que ceux-là
"""
import json
import os
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
VERSES = os.path.join(HERE, "public", "verses.json")
AUDIO_DIR = os.path.join(HERE, "public", "audio")

MIN_LEN, MAX_LEN = 12, 230  # bornes de longueur du verset arabe (lisibilité Reel)

# Racines/marqueurs attendus par thème (rasm sans tashkīl). None = longueur seule
# (concept non porté par une racine unique : on fait confiance à la curation amont).
THEME_MARKERS = {
    "rahma":    ["رحم", "رحيم", "راحم"],
    "tawba":    ["تاب", "توب", "تب", "تواب"],
    "shukr":    ["شكر", "شاكر", "شكور", "مشكور"],
    "tawakkul": ["وكل", "توكل", "حسبن", "حسبي", "حسبه", "حسبك"],
    "tafakkur": ["فكر"],
    "mort":     ["موت", "ميت", "مات", "يميت", "نميت", "امات", "اموات",
                 "موتى", "توف", "تتوف", "يتوف", "اجل"],
    "taqwa":    ["تق", "اتق", "متق", "وق", "يتق"],
    "rappel":   ["ذكر", "اذكر", "تطمئن"],
    "birr":     None,
    "faraj":    None,
}


def strip(s):
    s = "".join(c for c in unicodedata.normalize("NFD", s)
                if unicodedata.category(c) != "Mn")
    return s.replace("ٰ", "").replace("ـ", "").replace("ۖ", "").replace("ۚ", "")


def main():
    only = set(sys.argv[1:])
    themes = only or set(THEME_MARKERS)
    data = json.load(open(VERSES, encoding="utf-8"))

    kept, dropped = [], []
    for v in data:
        t = v["theme"]
        if t not in themes:
            kept.append(v)
            continue
        txt = strip(v["verse_ar"])
        n = len(v["verse_ar"])
        markers = THEME_MARKERS.get(t)
        ok_root = (markers is None) or any(strip(m) in txt for m in markers)
        ok_len = MIN_LEN <= n <= MAX_LEN
        if ok_root and ok_len:
            kept.append(v)
        else:
            reason = []
            if not ok_root:
                reason.append("racine absente")
            if not ok_len:
                reason.append(f"longueur {n}")
            dropped.append((v, ", ".join(reason)))

    for v, reason in dropped:
        print(f"  ✗ {v['theme']:9} {v['ref']:22} — {reason}")

    json.dump(kept, open(VERSES, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    # Balayage des audios orphelins : tout mp3 de public/audio non référencé par
    # un verset retenu est supprimé (l'audio vit dans public/, cf. staticFile).
    kept_basenames = {os.path.basename(v["audio"]) for v in kept}
    removed = 0
    for f in os.listdir(AUDIO_DIR):
        if f.endswith(".mp3") and f not in kept_basenames:
            os.remove(os.path.join(AUDIO_DIR, f))
            removed += 1
    print(f"{removed} audio(s) orphelin(s) supprimé(s)")

    import collections
    c = collections.Counter(v["theme"] for v in kept if v["theme"] in themes)
    print(f"\n{len(dropped)} écarté(s) · {sum(c.values())} retenus sur les thèmes traités")
    for k, n in sorted(c.items()):
        print(f"  {k:10} {n}")


if __name__ == "__main__":
    main()
