#!/usr/bin/env python3
"""
Construit la base de versets pour les Reels.

Principe de rigueur : on ne saisit JAMAIS le texte coranique de mémoire.
On ne fournit ici que des RÉFÉRENCES (sourate:verset) + un thème.
Le texte arabe (rasm ʿuthmānī vocalisé) et la traduction du sens (Hamidullah)
sont téléchargés depuis une source authentifiée (données Tanzil via alquran.cloud).

Sortie : public/verses.json

Usage :
  python3 build_verses.py            # (re)construit tous les thèmes
  python3 build_verses.py temps      # ne (re)construit que "temps", conserve le reste
"""
import json
import os
import sys
import time
import urllib.request

# Références sélectionnées — versets clairs et bien connus sur chaque thème.
# (références uniquement ; le texte est récupéré depuis la source)
REFS = {
    "paradis": [
        (3, 133), (55, 46), (56, 12), (76, 13), (88, 8), (88, 10),
        (36, 55), (43, 71), (13, 35), (9, 72), (18, 31), (2, 25),
    ],
    "enfer": [
        (2, 24), (4, 56), (14, 50), (40, 72), (56, 42), (56, 43),
        (67, 7), (78, 21), (88, 4), (104, 6), (70, 15), (14, 49),
    ],
    # Le temps : serment par le temps, alternance jour/nuit comme signe,
    # brièveté de la vie d'ici-bas, mesure divine du temps.
    "temps": [
        (3, 190), (25, 62), (17, 12), (21, 33), (36, 40),
        (79, 46), (10, 45), (30, 55), (22, 47), (70, 4),
    ],
    # Tawḥīd & création : unicité d'Allah liée à Son acte de création
    # (tawḥīd al-rubūbiyya + al-ulūhiyya). Versets clairs et bien connus.
    "tawhid": [
        (2, 163), (7, 54), (13, 16), (16, 17), (21, 22), (30, 22),
        (39, 62), (40, 62), (51, 56), (59, 24), (67, 3),
    ],
    # Jour du Jugement : la pesée des actions (mīzān), le livre des comptes,
    # la rétribution équitable de chaque bien et chaque mal. Versets clairs.
    "jugement": [
        (99, 7), (99, 8), (21, 47), (7, 8), (7, 9), (101, 6),
        (101, 8), (17, 14), (84, 7), (84, 10), (3, 30), (40, 17),
    ],
    # Le Livre d'Allah (le Coran) : sa nature de guidée, sa préservation,
    # sa facilité à la mémorisation, l'appel à le méditer, sa guérison et sa
    # bénédiction. Versets clairs et bien connus parlant du Coran lui-même.
    "coran": [
        (2, 2), (15, 9), (17, 9), (54, 17), (38, 29), (4, 82),
        (17, 82), (10, 57), (59, 21), (6, 155), (73, 4), (2, 185),
    ],
    # Patience, persévérance, endurance (الصَّبْر) : Allah est avec les patients,
    # leur récompense sans compter, l'ordre d'endurer l'épreuve, la belle patience.
    # Références vérifiées (racine ص-ب-ر présente) via le serveur MCP tafsir.
    "patience": [
        (2, 153), (2, 155), (3, 200), (3, 146), (8, 46), (16, 96),
        (16, 127), (39, 10), (13, 24), (41, 35), (31, 17), (70, 5),
    ],
    # Miséricorde d'Allah (الرَّحْمَة) : Sa miséricorde embrasse toute chose,
    # ne pas désespérer de Sa miséricorde, le Prophète ﷺ miséricorde pour
    # les mondes. Racine ر-ح-م vérifiée via le serveur MCP tafsir.
    "rahma": [
        (7, 156), (39, 53), (21, 107), (6, 54), (7, 56),
        (2, 218), (12, 64), (40, 7), (11, 90), (7, 49),
    ],
    # Repentir & pardon (التَّوْبَة) : Allah accepte le repentir de Ses
    # serviteurs, le repentir sincère, quiconque se repent et fait le bien.
    # Racine ت-و-ب vérifiée via le serveur MCP tafsir.
    "tawba": [
        (28, 67), (20, 82), (25, 71), (4, 17), (9, 104),
        (42, 25), (110, 3), (2, 160), (66, 8), (5, 39),
    ],
    # Gratitude (الشُّكْر) : « si vous êtes reconnaissants, Je vous
    # accroîtrai », qui est reconnaissant l'est pour lui-même.
    # Racine ش-ك-ر vérifiée via le serveur MCP tafsir.
    "shukr": [
        (14, 7), (31, 12), (2, 172), (16, 114), (39, 7),
        (27, 40), (34, 13), (16, 18), (27, 19), (16, 78),
    ],
    # Confiance en Allah (التَّوَكُّل) : quiconque place sa confiance en
    # Allah, Il lui suffit ; c'est sur Lui que comptent les croyants.
    # Racine و-ك-ل vérifiée via le serveur MCP tafsir.
    "tawakkul": [
        (3, 159), (65, 3), (8, 2), (3, 160), (14, 12),
        (9, 51), (39, 38), (67, 29), (25, 58), (11, 123),
    ],
    # Piété filiale (بِرُّ الوَالِدَيْن) : bonté envers les parents associée
    # à l'adoration d'Allah, la douceur envers eux dans leur vieillesse.
    # Vérifié via recherche textuelle (و-ل-د / إحسان) sur le serveur MCP tafsir.
    "birr": [
        (17, 23), (17, 24), (31, 14), (46, 15), (2, 83),
        (4, 36), (6, 151), (29, 8), (31, 15), (19, 14),
    ],
    # Méditation sur la création (التَّفَكُّر) : réfléchir aux signes
    # d'Allah dans les cieux, la terre et soi-même.
    # Racine ف-ك-ر vérifiée via le serveur MCP tafsir.
    "tafakkur": [
        (3, 191), (30, 21), (30, 8), (16, 11), (16, 69),
        (13, 3), (45, 13), (10, 24), (6, 50), (16, 44),
    ],
    # La mort (المَوْت) : toute âme goûtera la mort, elle vous atteindra
    # où que vous soyez, le rappel du retour vers Allah.
    # Racine م-و-ت vérifiée via le serveur MCP tafsir.
    "mort": [
        (3, 185), (21, 35), (29, 57), (4, 78), (3, 145),
        (39, 42), (2, 28), (23, 99), (50, 19), (67, 2),
    ],
    # Crainte révérencielle d'Allah (التَّقْوَى) : craignez Allah comme il
    # se doit, le meilleur viatique est la piété, le plus noble est le plus pieux.
    # Racine و-ق-ي vérifiée via le serveur MCP tafsir.
    "taqwa": [
        (3, 102), (2, 197), (49, 13), (8, 29), (33, 70),
        (3, 76), (9, 119), (7, 96), (5, 35), (16, 128),
    ],
    # Espoir après l'épreuve (الفَرَج بَعْدَ الشِّدَّة) : Allah accordera
    # une aisance après la gêne, une issue à qui Le craint, le secours proche.
    # Vérifié via recherche textuelle (عُسْر/يُسْر, مخرج) sur le serveur MCP tafsir.
    "faraj": [
        (65, 7), (65, 2), (65, 3), (12, 87), (93, 5),
        (93, 3), (2, 286), (40, 60), (2, 214), (3, 139),
    ],
    # Le rappel / évocation d'Allah (الذِّكْر) : c'est par le rappel d'Allah
    # que les cœurs s'apaisent, « évoquez-Moi, Je vous évoquerai ».
    # Racine ذ-ك-ر vérifiée via le serveur MCP tafsir.
    "rappel": [
        (13, 28), (2, 152), (33, 41), (29, 45), (20, 14),
        (33, 35), (63, 9), (73, 8), (87, 15), (2, 200),
    ],
}

# Entrées combinées (plusieurs āyāt d'une même sourate présentées comme un bloc).
# Pour une sourate ENTIÈRE, on utilise la récitation de toute la sourate (CDN).
COMBINED = {
    "temps": [
        # Sourate al-ʿAsr (103) en entier — la sourate-phare sur le temps.
        {"surah": 103, "ayat": [1, 2, 3], "full_surah_audio": True},
    ],
    "tawhid": [
        # Sourate al-Ikhlāṣ (112) en entier — la sourate du Tawḥīd par excellence.
        {"surah": 112, "ayat": [1, 2, 3, 4], "full_surah_audio": True},
    ],
    "patience": [
        # Sourate aš-Šarḥ (94) en entier — « car avec la difficulté est, certes,
        # une facilité » : l'aube après la nuit, le fruit de la patience.
        {"surah": 94, "ayat": [1, 2, 3, 4, 5, 6, 7, 8], "full_surah_audio": True},
    ],
}

# La basmala est récupérée depuis la source (al-Fātiḥa 1:1), jamais saisie de
# mémoire — l'ordre exact des harakāt doit venir des données authentifiées.
_BASMALA = None
API = "https://api.alquran.cloud/v1/ayah/{s}:{a}/{ed}"
# Récitation d'une sourate entière (Mishary al-ʿAfāsī, 128 kbps)
SURAH_AUDIO = "https://cdn.islamic.network/quran/audio-surah/128/ar.alafasy/{s}.mp3"


def fetch(surah, ayah, edition):
    url = API.format(s=surah, a=ayah, ed=edition)
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)["data"]


def basmala():
    global _BASMALA
    if _BASMALA is None:
        # al-Fātiḥa 1:1 EST la basmala — source authentifiée, harakāt exacts.
        raw = fetch(1, 1, "quran-uthmani")["text"].replace("﻿", "")
        _BASMALA = " ".join(raw.split())
    return _BASMALA


def clean(text_ar, surah, ayah):
    # Retirer la basmala accolée au 1er verset (sauf al-Fatiha)
    if ayah == 1 and surah != 1:
        b = basmala()
        norm = " ".join(text_ar.split())
        if norm.startswith(b):
            text_ar = norm[len(b):].lstrip()
    # Retirer marques ornementales hors-texte (rub' el-hizb ۞, sajda ۩) et BOM
    text_ar = text_ar.replace("۞", "").replace("۩", "").replace("﻿", "")
    return " ".join(text_ar.split())


def build_single(theme, surah, ayah):
    ar = fetch(surah, ayah, "quran-uthmani")
    fr = fetch(surah, ayah, "fr.hamidullah")
    rec = fetch(surah, ayah, "ar.alafasy")  # récitation Mishary al-ʿAfāsī
    audio_rel = f"audio/{theme}_{surah}_{ayah}.mp3"
    urllib.request.urlretrieve(rec["audio"], os.path.join("public", audio_rel))
    rec_entry = {
        "theme": theme,
        "surah": surah,
        "ayah": ayah,
        "surah_ar": ar["surah"]["name"],
        "surah_fr": ar["surah"]["englishName"],
        "ref": f"{ar['surah']['englishName']} {surah}:{ayah}",
        "verse_ar": clean(ar["text"], surah, ayah),
        "translation": fr["text"],
        "audio": audio_rel,
    }
    print(f"  ✓ {theme:8} {surah}:{ayah}  {ar['surah']['name']}")
    time.sleep(0.2)
    return rec_entry


def build_combined(theme, spec):
    surah = spec["surah"]
    ayat = spec["ayat"]
    ar_parts, fr_parts = [], []
    surah_ar = surah_fr = None
    for a in ayat:
        ar = fetch(surah, a, "quran-uthmani")
        fr = fetch(surah, a, "fr.hamidullah")
        surah_ar = ar["surah"]["name"]
        surah_fr = ar["surah"]["englishName"]
        ar_parts.append(clean(ar["text"], surah, a))
        fr_parts.append(fr["text"].strip())
        time.sleep(0.2)
    audio_rel = f"audio/{theme}_{surah}_{ayat[0]}-{ayat[-1]}.mp3"
    if spec.get("full_surah_audio"):
        urllib.request.urlretrieve(SURAH_AUDIO.format(s=surah),
                                   os.path.join("public", audio_rel))
    rng = f"{ayat[0]}-{ayat[-1]}"
    print(f"  ✓ {theme:8} {surah}:{rng}  {surah_ar}")
    return {
        "theme": theme,
        "surah": surah,
        "ayah": ayat[0],
        "surah_ar": surah_ar,
        "surah_fr": surah_fr,
        "ref": f"{surah_fr} {surah}:{rng}",
        "verse_ar": "  ".join(ar_parts),
        "translation": " ".join(fr_parts),
        "audio": audio_rel,
    }


def main():
    os.makedirs("public/audio", exist_ok=True)
    only = set(sys.argv[1:])  # thèmes à (re)construire ; vide = tous
    themes = [t for t in REFS if not only or t in only]

    # Conserver les entrées des thèmes NON reconstruits
    out = []
    path = "public/verses.json"
    if only and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            out = [v for v in json.load(f) if v["theme"] not in themes]

    for theme in themes:
        for surah, ayah in REFS[theme]:
            out.append(build_single(theme, surah, ayah))
        for spec in COMBINED.get(theme, []):
            out.append(build_combined(theme, spec))

    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    counts = {}
    for v in out:
        counts[v["theme"]] = counts.get(v["theme"], 0) + 1
    summary = ", ".join(f"{k}={n}" for k, n in counts.items())
    print(f"\n{len(out)} versets écrits → {path}  ({summary})")


if __name__ == "__main__":
    main()
