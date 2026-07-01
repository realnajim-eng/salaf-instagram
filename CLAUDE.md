# CLAUDE.md — Un Jour Un Salaf

Bot Instagram qui publie du contenu islamique authentique : **paroles des Salaf**
(posts image) et **versets coraniques** (Reels vidéo). Rendu + publication via
GitHub Actions. Langue de travail : **français**.

## Deux pipelines

### 1. Posts Salaf (racine du dépôt) — Python + Pillow
Citation authentifiée (dorar.net) → image → publication Instagram.

| Fichier | Rôle |
|---|---|
| `fetch_caption.py` | Choisit la citation du jour dans `quotes_salaf.json`, évite les répétitions via `tracker.json`, écrit `daily_quote.json` |
| `build_caption.py` | Construit la légende (texte + hashtags + handle) |
| `generate_image.py` | Compose l'image (fond `images/` + texte arabe + logo) → `output.jpg` |
| `post_salaf.py` | Renouvelle le token IG, héberge l'image en GitHub Release, crée le container média, publie |
| `quotes_salaf.json` | Base de paroles (source : dorar.net / shamela.ws) |
| `tracker.json` | `used_quotes` déjà publiées |

### 2. Reels versets (`reels/`) — Remotion (React/TS) + Python
Référence sourate:verset → texte récupéré d'une source authentifiée → vidéo verticale.

| Fichier | Rôle |
|---|---|
| `reels/build_verses.py` | (Re)construit `public/verses.json` depuis les **références** REFS. **Ne saisit jamais le texte coranique de mémoire** — télécharge rasm ʿuthmānī + traduction Hamidullah via alquran.cloud |
| `reels/pick_verse.py` | Choisit le verset du jour (round-robin par thème, jamais de republication), écrit `render_props.json` + `current_verse.json` |
| `reels/prune_verses.py` | Élague le réservoir de versets |
| `reels/build_reel_caption.py` | Légende du reel |
| `reels/post_reel.py` | Publie le reel sur Instagram |
| `reels/src/` | Composition Remotion (`Verse`) |
| `reels/public/` | Fonds (`.jpg`/`.png`), `audio/`, `fonts/`, `verses.json` |
| `reels/posted_reels.json` | Historique des reels publiés |

**Réservoir actuel : 250 versets, 17 thèmes** (paradis, enfer, temps, tawhid,
patience, jugement, coran, rahma, tawba, shukr, tawakkul, birr, tafakkur, mort,
taqwa, faraj, rappel).

Commandes reels (depuis `reels/`) :
```bash
python3 build_verses.py <theme>        # (re)construit un thème ; sans arg = tous
python3 pick_verse.py                  # sélectionne le verset du jour
node_modules/.bin/remotion render Verse out/reel.mp4 --props=render_props.json
npx remotion studio                    # aperçu interactif
```
> `paradis` & `enfer` utilisent une vidéo de fond locale **absente du dépôt** →
> exclus du rendu cloud automatique (fond image fixe pour les autres thèmes).

## Alternance de publication
`daily_alternate.yml` alterne Salaf ↔ reel via le compteur `post_state.json`
(`{"next": "salaf"|"reel"}`).

## Automatisation — EN PAUSE
Les workflows GitHub Actions (`.github/workflows/`) sont **en pause depuis
2026-06-24** à la demande. La logique est prête ; publication 18h Paris quand
réactivée. Secrets requis : `INSTAGRAM_ACCESS_TOKEN`, `INSTAGRAM_USER_ID`,
`INSTAGRAM_CLIENT_SECRET`, `ANTHROPIC_API_KEY`.

## Règles de travail (IMPORTANT)
- **Rigueur islamique** : ne jamais inventer ni saisir de mémoire un verset, un
  hadith ou une parole du Salaf. Toujours passer par une source authentifiée
  (dorar.net, shamela.ws, API Coran) ou le skill `aqwal-salaf` / `islamic-sciences`.
- **Reels un par un** : générer un seul reel à la fois + aperçu, jamais en lot.
- **Toujours ouvrir l'aperçu** : après génération d'une image/vidéo, `open <fichier>`.
- **Demander avant `git push`** : ne jamais pousser automatiquement.
- **Réapprovisionnement** : à épuisement d'un thème, ajouter du neuf vérifié ;
  ne republier qu'au véritable épuisement du Coran sur le thème.
- **Aucun secret dans le code** : tout passe par les secrets GitHub.

## Environnement
- macOS · Python 3 (`pip install -r requirements.txt`) · Node/npm pour `reels/`.
- `ffmpeg`/`ffprobe` dispo pour l'inspection vidéo.
