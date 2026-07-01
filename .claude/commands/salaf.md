---
description: Prévisualiser un post Salaf (image) en local
---

Génère un aperçu local d'un post « parole du Salaf » — **sans publier**.

Règles (voir CLAUDE.md) :
- Parole issue de `quotes_salaf.json` (source authentifiée dorar.net / shamela.ws).
  **Jamais** inventer ni citer de mémoire.
- **Toujours ouvrir l'aperçu** après génération.
- **Ne publie pas** et **ne push pas** sans mon feu vert.

Argument optionnel `$ARGUMENTS` : mot-clé ou thème pour orienter le choix de la parole.

Étapes :
1. Choisis une parole non déjà publiée (voir `tracker.json` → `used_quotes`).
   Si `$ARGUMENTS` est fourni, privilégie une parole en lien.
2. Génère l'image : `python3 generate_image.py` (produit `output.jpg`).
3. **Ouvre l'aperçu** : `open output.jpg`
4. Montre la parole choisie + sa source, et attends mon retour.
