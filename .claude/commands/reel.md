---
description: Générer UN reel verset pour un thème + ouvrir l'aperçu
---

Génère **un seul** reel pour le thème : `$ARGUMENTS`

Règles (voir CLAUDE.md) :
- **Un par un** : ne rends jamais plusieurs reels en lot. Un seul verset, un seul aperçu.
- **Jamais de texte coranique de mémoire** : le texte vient de `reels/public/verses.json`
  (construit via `build_verses.py` depuis des références authentifiées).
- Les thèmes `paradis`/`enfer` utilisent une vidéo de fond locale absente du dépôt.

Étapes :
1. Vérifie que le thème existe dans `reels/public/verses.json`. Sinon, propose de le
   créer avec `/reappro`.
2. Choisis un verset non encore publié de ce thème (regarde `reels/posted_reels.json`).
   Écris ses props dans `reels/render_props.json`.
3. Rends la vidéo :
   `cd reels && node_modules/.bin/remotion render Verse out/$ARGUMENTS.mp4 --props=render_props.json`
4. **Ouvre l'aperçu** : `open reels/out/$ARGUMENTS.mp4`
5. Résume le verset choisi (réf, thème) et attends mon feu vert avant toute publication.
   **Ne publie pas** et **ne push pas** sans que je le demande.
