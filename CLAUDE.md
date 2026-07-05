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
| `reels/pick_verse.py` | Choisit le verset du jour (round-robin par thème) ; une fois les 250 publiés, boucle depuis le début, écrit `render_props.json` + `current_verse.json` |
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
> Les **17 thèmes** utilisent désormais un **fond image fixe** présent dans
> `reels/public/` (zoom lent continu via `STILL_IMAGE` dans `QuoteReel.tsx`),
> `paradis` (`Paradis.jpg`) et `enfer` (`Enfer.jpg`) compris → tous rendables
> dans le cloud automatique, plus aucune vidéo de fond locale requise.

## Automatisation — ACTIVE depuis 2026-07-05
Deux publications indépendantes **chaque jour** (pas d'alternance) :
- `daily_post.yml` : parole de Salaf à **17h17 Paris** (cron `17 15 * * *` UTC).
- `daily_reel.yml` : reel verset à **22h22 Paris** (cron `22 20 * * *` UTC).

Horaires volontairement décalés hors pile-heure (`:17`/`:22` plutôt que `:00`)
car les crons GitHub Actions programmés pile à l'heure ronde subissent des
retards de charge (observé : jusqu'à 3h41 de retard le 2026-07-05). Les crons
sont en UTC fixe → dérive d'1h en heure d'hiver (CET) sans ajustement.
`daily_alternate.yml` (ancienne alternance Salaf/reel via `post_state.json`) est
remplacé et gardé en déclenchement manuel uniquement, schedule désactivé, pour
éviter tout double post. Secrets requis : `INSTAGRAM_ACCESS_TOKEN`,
`INSTAGRAM_USER_ID`, `INSTAGRAM_CLIENT_SECRET`, `ANTHROPIC_API_KEY`.

## Règles de travail (IMPORTANT)
- **Rigueur islamique** : ne jamais inventer ni saisir de mémoire un verset, un
  hadith ou une parole du Salaf. Toujours passer par une source authentifiée
  (dorar.net, shamela.ws, API Coran) ou le skill `aqwal-salaf` / `islamic-sciences`.
  Cette règle prime sur tout, y compris la gestion autonome ci-dessous.
- **Gestion autonome de la publication quotidienne (depuis 2026-07-05)** :
  l'utilisateur a demandé de tout gérer sans confirmation. La publication
  elle-même est déjà 100% automatique via GitHub Actions (aucune action de ma
  part n'est nécessaire au quotidien). Pour la maintenance du pipeline
  (réapprovisionnement du réservoir, correction de bugs bloquant une
  publication, mise à jour de `tracker.json`/`posted_reels.json`/
  `post_state.json`), j'agis directement **sans demander confirmation**,
  y compris pour committer et **pousser sur GitHub** (`git push`) — car sans
  ça la publication automatique reste bloquée sur le commit précédent.
  Reste couvert par la prudence habituelle (à ne jamais faire sans demander) :
  force-push, `reset --hard`, suppression de workflows/secrets/branches, ou
  toute action destructive/irréversible sans rapport direct avec le maintien
  de la publication quotidienne.
- **Reels un par un** (hors automatisation) : si l'utilisateur demande un reel
  en interactif, en générer un seul à la fois + aperçu, jamais en lot.
- **Toujours ouvrir l'aperçu** (hors automatisation) : après génération
  interactive d'une image/vidéo, `open <fichier>`.
- **Boucle infinie (depuis 2026-07-05)** : les deux réservoirs (citations Salaf,
  versets) recommencent automatiquement depuis le début une fois entièrement
  épuisés (`tracker.json` / `posted_reels.json` remis à zéro), au lieu de
  bloquer la publication. Le réapprovisionnement (ajout de nouvelles citations
  ou versets vérifiés) reste bienvenu à tout moment pour retarder les
  répétitions, mais n'est plus une condition requise pour que la publication
  continue.
- **Aucun secret dans le code** : tout passe par les secrets GitHub.

## Environnement
- macOS · Python 3 (`pip install -r requirements.txt`) · Node/npm pour `reels/`.
- `ffmpeg`/`ffprobe` dispo pour l'inspection vidéo.
