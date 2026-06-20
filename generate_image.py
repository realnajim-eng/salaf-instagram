import textwrap
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BACKGROUND_PATH = "images/background.jpg"
OUTPUT_PATH = "output.jpg"

# Police arabe embarquée (le runner GitHub n'a pas de police arabe système)
ARABIC_FONT_PATHS = [
    "fonts/Amiri-Regular.ttf",
    "/System/Library/Fonts/Supplemental/Baghdad.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]

# Police du nom du compte — sans-serif nette, embarquée (rendu identique partout)
ACCOUNT_FONT_PATHS = [
    "fonts/Poppins-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

# Formule de bénédiction selon la génération
HONORIFIC_SAHABI = "رَضِيَ اللَّهُ عَنْهُ"   # Compagnon
HONORIFIC_OTHER  = "رَحِمَهُ اللَّهُ"        # Tābiʿī / Atbāʿ et au-delà

CANVAS_SIZE = 1080

# Suréchantillonnage : on dessine tout à SS× la taille finale puis on réduit en
# LANCZOS au moment de sauvegarder. Le texte, les contours et les traits dorés
# en ressortent beaucoup plus nets (anti-aliasing fin) qu'un rendu direct à 1080.
SS = 3

# Bordure colorée « cuite » dans background.jpg (~37 px). On rogne ce nombre de
# pixels sur chaque bord avant redimensionnement pour l'affiner de moitié.
BORDER_CROP = 18

# Épaisseur du contour doré autour du texte (était 2 ; affiné à 1).
GOLD_STROKE = 1

# Épaisseur de contour (en unités avant ×SS) partagée par le titre et la
# citation centrale, pour un rendu identique des deux.
TITLE_STROKE = 3

WHITE      = (255, 255, 255, 255)
WHITE_DIM  = (255, 255, 255, 200)
GOLD        = (212, 175, 55, 230)
GOLD_BRIGHT = (255, 209, 92, 255)   # doré clair et éclatant (nom du compte)
OVERLAY_BG  = (0, 0, 0, 155)

# Couleurs du dégradé Instagram (violet → rose → orange)
IG_PURPLE = (131, 58, 180)
IG_PINK   = (225, 48, 108)
IG_ORANGE = (247, 119, 55)
IG_GRADIENT = [IG_PURPLE, IG_PINK, IG_ORANGE]

FONT_NAME_SIZE      = 38
FONT_QUOTE_SIZE     = 38
FONT_SOURCE_SIZE    = 24
FONT_HONORIFIC_SIZE = 33   # bénédiction arabe sur la ligne du nom

FONT_PATHS = [
    "/System/Library/Fonts/Supplemental/Georgia Bold Italic.ttf",
    "/System/Library/Fonts/Supplemental/Georgia Italic.ttf",
    "/System/Library/Fonts/Supplemental/Georgia.ttf",
    "/Library/Fonts/Arial Bold Italic.ttf",
    "/Library/Fonts/Arial Italic.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-BoldItalic.ttf",
]


def load_font(size):
    for path in FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def load_arabic_font(size):
    # Moteur BASIC forcé : on fait nous-mêmes la mise en forme (reshape +
    # bidi) dans shape_arabic(). Sans ça, si libraqm est présent (runner
    # GitHub), Pillow refait le bidi par-dessus et inverse le texte.
    try:
        basic = ImageFont.Layout.BASIC
    except AttributeError:
        basic = ImageFont.LAYOUT_BASIC
    for path in ARABIC_FONT_PATHS:
        try:
            return ImageFont.truetype(path, size, layout_engine=basic)
        except Exception:
            continue
    return ImageFont.load_default()


def load_account_font(size):
    for path in ACCOUNT_FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return load_font(size)


def shape_arabic(text):
    """Met en forme un texte arabe (liaisons + sens droite-à-gauche) pour Pillow."""
    return get_display(arabic_reshaper.reshape(text))


def honorific_for(generation):
    """Bénédiction à afficher selon la génération du Salaf."""
    return HONORIFIC_SAHABI if generation == "sahabi" else HONORIFIC_OTHER


def book_from_source(source):
    """Ne garde que le livre (avant le tiret cadratin) ; retire le site
    (Al-Durar al-Sanniyya / dorar.net) et le chapitre."""
    return source.split("—")[0].strip()


def shadow_text(draw, xy, text, font, anchor="mm", stroke_width=GOLD_STROKE):
    draw.text(xy, text, font=font, fill=GOLD, anchor=anchor,
              stroke_width=stroke_width, stroke_fill=(0, 0, 0, 255))


def stroke_px():
    """Épaisseur du contour doré, mise à l'échelle du suréchantillonnage."""
    return GOLD_STROKE * SS


# Glyphe ﷺ (ligature « ṣallā Allāhu ʿalayhi wa-sallam ») — absent des polices
# latines, présent dans Amiri. On le rend avec la police arabe au sein de la ligne.
PROPHET_GLYPH = "ﷺ"


def draw_quote_line(draw, cx, y, line, latin_font, ar_font):
    """Dessine une ligne de citation centrée ; si elle contient ﷺ, ce glyphe
    est rendu avec la police arabe, le reste avec la police latine."""
    sw = 4 * SS   # contour noir épais de la citation (lisibilité sur fond clair)
    if PROPHET_GLYPH not in line:
        shadow_text(draw, (cx, y), line, latin_font, stroke_width=sw)
        return
    # Découper la ligne en segments (texte latin / glyphe ﷺ)
    segs, buf = [], ""
    for ch in line:
        if ch == PROPHET_GLYPH:
            if buf:
                segs.append((buf, latin_font))
                buf = ""
            segs.append((PROPHET_GLYPH, ar_font))
        else:
            buf += ch
    if buf:
        segs.append((buf, latin_font))
    total = sum(draw.textlength(s, font=f) for s, f in segs)
    x = cx - total / 2
    for s, f in segs:
        draw.text((x, y), s, font=f, fill=GOLD, anchor="lm",
                  stroke_width=sw, stroke_fill=(0, 0, 0, 255))
        x += draw.textlength(s, font=f)


def text_gold_thin_outline(overlay, cx, cy, text, font_size, ss=3, stroke=2,
                           canvas_w=CANVAS_SIZE):
    """Texte DORÉ avec un fin contour noir sous-pixel : rendu à ss× avec un
    contour de `stroke` px, puis réduction → contour effectif = stroke/ss px."""
    big_font = load_font(font_size * ss)
    lw, lh = canvas_w * ss, (font_size + 24) * ss
    layer = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text(
        (lw // 2, lh // 2), text, font=big_font, fill=GOLD,
        anchor="mm", stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    layer = layer.resize((lw // ss, lh // ss), Image.LANCZOS)
    overlay.alpha_composite(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)))


def gradient_line(draw, x0, x1, y, width, stops):
    """Trace une ligne horizontale au dégradé de couleurs (stops = liste RGB)."""
    n = max(1, int(round(x1 - x0)))
    half = width / 2
    for i in range(n + 1):
        t = i / n
        seg = t * (len(stops) - 1)
        idx = min(int(seg), len(stops) - 2)
        f = seg - idx
        c0, c1 = stops[idx], stops[idx + 1]
        color = tuple(int(c0[k] + (c1[k] - c0[k]) * f) for k in range(3)) + (255,)
        x = x0 + i
        draw.line([(x, y - half), (x, y + half)], fill=color, width=1)


def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines, current = [], []
    for word in words:
        test = " ".join(current + [word])
        w = draw.textlength(test, font=font)
        if w <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def generate(name: str, quote: str, source: str, output_path: str = OUTPUT_PATH,
             generation: str = ""):
    S  = SS                      # facteur de suréchantillonnage
    RC = CANVAS_SIZE * S         # taille du canevas de rendu (haute résolution)

    bg = Image.open(BACKGROUND_PATH).convert("RGBA")
    if BORDER_CROP > 0:
        w, h = bg.size
        bg = bg.crop((BORDER_CROP, BORDER_CROP, w - BORDER_CROP, h - BORDER_CROP))
    bg = bg.resize((RC, RC), Image.LANCZOS)

    overlay = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_name   = load_font(FONT_NAME_SIZE * S)
    font_quote  = load_font(FONT_QUOTE_SIZE * S)
    font_source = load_font(FONT_SOURCE_SIZE * S)

    cx     = RC // 2
    margin = 70 * S
    max_w  = RC - margin * 2
    sw     = stroke_px()

    quote_lines = wrap_text(f'« {quote} »', font_quote, max_w, draw)
    line_h      = (FONT_QUOTE_SIZE + 14) * S
    quote_h     = len(quote_lines) * line_h

    # Nom + bénédiction arabe sur LA MÊME LIGNE, centrés comme un groupe
    y_name = 65 * S
    font_hon = load_arabic_font(FONT_HONORIFIC_SIZE * S)
    hon_text = shape_arabic(honorific_for(generation))
    name_w  = draw.textlength(name, font=font_name)
    hon_w   = draw.textlength(hon_text, font=font_hon)
    gap     = 16 * S
    x_left  = cx - (name_w + gap + hon_w) / 2

    # Titre — mêmes couleurs/contour que le texte central : doré + contour noir épais
    title_stroke = 4 * S
    draw.text((x_left, y_name), name, font=font_name, fill=GOLD,
              anchor="lm", stroke_width=title_stroke, stroke_fill=(0, 0, 0, 255))
    # Bénédiction arabe — même couleur/style que le titre
    draw.text((x_left + name_w + gap, y_name), hon_text, font=font_hon, fill=GOLD,
              anchor="lm", stroke_width=title_stroke, stroke_fill=(0, 0, 0, 255))

    # (Soulignement du titre retiré)
    sep_y = y_name + FONT_NAME_SIZE * S // 2 + 3 * S

    # Citation — placée HAUT, juste sous le titre (et non plus centrée verticalement)
    font_quote_ar = load_arabic_font(FONT_QUOTE_SIZE * S)
    quote_total_h = len(quote_lines) * line_h
    zone_top    = sep_y + 70 * S                          # sous le titre (descendu légèrement)
    y_q = zone_top
    for i, line in enumerate(quote_lines):
        draw_quote_line(draw, cx, y_q + i * line_h + FONT_QUOTE_SIZE * S // 2, line,
                        font_quote, font_quote_ar)

    # Source — placée en bas, mais TOUJOURS sous la citation (descend si elle est longue)
    quote_bottom = y_q + quote_total_h
    y_src = max(RC - 115 * S, quote_bottom + 45 * S)

    # Source — en bas de l'image (livre seul) ; texte doré, tout petit contour noir
    text_gold_thin_outline(overlay, cx, y_src, f"— {book_from_source(source)}",
                           FONT_SOURCE_SIZE * S, canvas_w=RC)

    # Compte Instagram — logo + nom
    IG_PURPLE = (131, 58, 180, 255)
    IG_PINK   = (225, 48, 108, 255)
    IG_ORANGE = (247, 119, 55, 255)
    BLACK     = (0, 0, 0, 255)

    ACCOUNT_TEXT = "Un_Jour_Un_Salaf"
    ICON_SIZE    = 23 * S   # taille du logo Instagram
    font_account = load_account_font(22 * S)

    y_account = RC - 50 * S

    # Largeur totale logo + espace + texte
    text_w = draw.textlength(ACCOUNT_TEXT, font=font_account)
    gap    = 8 * S
    total_w = ICON_SIZE + gap + text_w
    x_start = cx - total_w / 2

    # ── Logo Instagram (PNG officiel) ────────────────────────────────────────
    ix = int(x_start)
    iy = int(y_account - ICON_SIZE // 2)
    try:
        logo = Image.open("images/instagram_logo.png").convert("RGBA")
        logo = logo.resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS)
        overlay.paste(logo, (ix, iy), logo)
    except Exception:
        # fallback : carré arrondi dégradé simple
        r = 7
        for stroke, color in [(3, IG_PURPLE), (2, IG_PINK), (1, IG_ORANGE)]:
            draw.rounded_rectangle(
                [ix - stroke, iy - stroke, ix + ICON_SIZE + stroke, iy + ICON_SIZE + stroke],
                radius=r + stroke, outline=color, width=2,
            )

    # ── Texte avec contour dégradé (affiné : 2 couches au lieu de 3) ──────────
    tx = int(x_start + ICON_SIZE + gap)
    ty = y_account
    for stroke, color in [(2 * S, IG_PURPLE)]:
        draw.text((tx, ty), ACCOUNT_TEXT, font=font_account, fill=color, anchor="lm",
                  stroke_width=stroke, stroke_fill=color)
    draw.text((tx, ty), ACCOUNT_TEXT, font=font_account, fill=GOLD_BRIGHT, anchor="lm")

    result = Image.alpha_composite(bg, overlay).convert("RGB")

    # Réduction du canevas haute résolution vers la taille finale : c'est cette
    # étape LANCZOS qui produit des bords nets et lisses.
    if S != 1:
        result = result.resize((CANVAS_SIZE, CANVAS_SIZE), Image.LANCZOS)

    # Léger renforcement de netteté après réduction (subtil, sans halo visible).
    result = result.filter(ImageFilter.UnsharpMask(radius=1.2, percent=80, threshold=2))

    # subsampling=0 (4:4:4) : pas de sous-échantillonnage de la chrominance, ce
    # qui évite la bavure de couleur sur le texte doré et le dégradé Instagram.
    result.save(output_path, "JPEG", quality=95, subsampling=0, optimize=True)
    print(f"✅ Image générée : {output_path}")
    return output_path


if __name__ == "__main__":
    generate(
        name="Ibn al-Qayyim",
        quote="La patience est de trois sortes : la patience dans l'obéissance à Allah, la patience face aux interdits d'Allah, et la patience face aux décrets douloureux d'Allah.",
        source="Madarij as-Salikin",
    )
