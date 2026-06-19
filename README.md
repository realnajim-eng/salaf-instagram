# Un Jour Un Salaf — bot Instagram

Bot automatisé qui publie chaque jour sur Instagram une parole authentique des
**Salaf as-Salih** (Compagnons, Tābiʿūn, Atbāʿ al-Tābiʿīn), illustrée sur une
image générée, avec sa source.

## Fonctionnement

Chaque jour à **8h00 UTC** (10h Paris), GitHub Actions exécute :

1. **`fetch_caption.py`** — choisit une citation dans `quotes_salaf.json`
   (base issue de [dorar.net](https://dorar.net)), en évitant les répétitions
   grâce à `tracker.json`, et écrit `daily_quote.json`.
   *Fallback :* si `quotes_salaf.json` est absent, une citation est générée via
   l'API Claude.
2. **`post_salaf.py`** —
   - renouvelle automatiquement le token Instagram (valable 60 jours) et met à
     jour le secret GitHub correspondant ;
   - génère l'image (`generate_image.py`, Pillow) ;
   - héberge l'image en pièce jointe d'une *GitHub Release* (URL publique, sans
     commit) ;
   - crée le container média Instagram, attend qu'il soit `FINISHED` (polling),
     puis publie.

## Structure

| Fichier               | Rôle                                                        |
|-----------------------|-------------------------------------------------------------|
| `fetch_caption.py`    | Sélection de la citation du jour                            |
| `generate_image.py`   | Composition de l'image (fond + texte + logo)               |
| `post_salaf.py`       | Token, hébergement image, publication Instagram            |
| `quotes_salaf.json`   | Base de citations (28 paroles, dorar.net)                  |
| `tracker.json`        | Suivi des citations déjà publiées (`used_quotes`)          |
| `images/`             | Fond + logo Instagram                                       |
| `.github/workflows/`  | `daily_post.yml` (publication) · `get_token.yml` (token)   |

## Secrets GitHub requis

À définir dans **Settings → Secrets and variables → Actions** :

| Secret                      | Description                                              |
|-----------------------------|---------------------------------------------------------|
| `INSTAGRAM_ACCESS_TOKEN`    | Token longue durée (renouvelé automatiquement)          |
| `INSTAGRAM_USER_ID`         | Identifiant du compte Instagram professionnel           |
| `INSTAGRAM_CLIENT_SECRET`   | Secret de l'app Meta (pour l'échange de token)          |
| `ANTHROPIC_API_KEY`         | Clé API Claude (fallback de génération)                 |

> `GITHUB_TOKEN` est fourni automatiquement par GitHub Actions.

## Obtenir le token Instagram (première installation)

1. Récupérer un **token courte durée** depuis le
   [Graph API Explorer](https://developers.facebook.com/tools/explorer/) de Meta.
2. Lancer manuellement le workflow **Get Instagram Token**
   (`get_token.yml`) en collant ce token dans le champ `short_token`.
3. Copier le token longue durée affiché dans les logs et le placer dans le
   secret `INSTAGRAM_ACCESS_TOKEN`. Il sera ensuite renouvelé automatiquement à
   chaque publication.

## Exécution locale (test)

```bash
pip install -r requirements.txt

# Tester uniquement la génération d'image
python generate_image.py        # produit output.jpg

# Chaîne complète (nécessite les variables d'environnement ci-dessus)
python fetch_caption.py
python post_salaf.py
```

## Sécurité

Aucun secret ne doit figurer dans le code ou les workflows. Tout identifiant
(token, client secret, clé API) passe exclusivement par les secrets GitHub.
