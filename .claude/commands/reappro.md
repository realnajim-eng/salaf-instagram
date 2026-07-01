---
description: Réapprovisionner un thème en versets vérifiés
---

Ajoute de nouveaux versets **vérifiés** au thème : `$ARGUMENTS`

Règles (voir CLAUDE.md — rigueur islamique) :
- On ne saisit **que des références** (sourate:verset) dans le dict `REFS` de
  `reels/build_verses.py`. Le texte arabe (rasm ʿuthmānī) et la traduction Hamidullah
  sont téléchargés depuis la source authentifiée par le script — **jamais de mémoire**.
- Vérifie chaque référence (pertinence au thème + clarté) via le skill
  `islamic-sciences` / MCP `tafsir` avant de l'ajouter.
- **Ne republie jamais** un verset déjà publié. On ne réapprovisionne qu'en versets
  neufs ; au véritable épuisement du Coran sur le thème, le dire clairement.

Étapes :
1. Liste les références déjà présentes pour `$ARGUMENTS` dans `REFS`.
2. Propose-moi de nouvelles références pertinentes (avec justification courte) et
   attends validation.
3. Ajoute-les à `REFS["$ARGUMENTS"]`, puis reconstruis :
   `cd reels && python3 build_verses.py $ARGUMENTS`
4. Confirme le nouveau total pour ce thème.
