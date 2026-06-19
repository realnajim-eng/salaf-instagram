import textwrap
from PIL import Image, ImageDraw, ImageFont

BACKGROUND_PATH = "images/background.jpg"
OUTPUT_PATH = "output.jpg"

CANVAS_SIZE = 1080

WHITE      = (255, 255, 255, 255)
WHITE_DIM  = (255, 255, 255, 200)
GOLD       = (212, 175, 55, 230)
OVERLAY_BG = (0, 0, 0, 155)

FONT_NAME_SIZE   = 38
FONT_QUOTE_SIZE  = 38
FONT_SOURCE_SIZE = 30

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


def shadow_text(draw, xy, text, font, anchor="mm"):
    draw.text(xy, text, font=font, fill=(0, 0, 0, 255), anchor=anchor,
              stroke_width=2, stroke_fill=GOLD)


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


def generate(name: str, quote: str, source: str, output_path: str = OUTPUT_PATH):
    bg = Image.open(BACKGROUND_PATH).convert("RGBA")
    bg = bg.resize((CANVAS_SIZE, CANVAS_SIZE), Image.LANCZOS)

    overlay = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_name   = load_font(FONT_NAME_SIZE)
    font_quote  = load_font(FONT_QUOTE_SIZE)
    font_source = load_font(FONT_SOURCE_SIZE)

    cx     = CANVAS_SIZE // 2
    margin = 70
    max_w  = CANVAS_SIZE - margin * 2

    quote_lines = wrap_text(f'« {quote} »', font_quote, max_w, draw)
    line_h      = FONT_QUOTE_SIZE + 14
    quote_h     = len(quote_lines) * line_h

    # Nom — en haut de l'image
    y_name = 80
    shadow_text(draw, (cx, y_name), name, font_name)

    # Soulignement doré exactement sous le nom
    name_w = draw.textlength(name, font=font_name)
    sep_y = y_name + FONT_NAME_SIZE // 2 + 8
    draw.line([(cx - name_w / 2, sep_y), (cx + name_w / 2, sep_y)], fill=GOLD, width=2)

    # Citation — centrée verticalement
    quote_total_h = len(quote_lines) * line_h
    y_q = (CANVAS_SIZE - quote_total_h) // 2 - 250
    for i, line in enumerate(quote_lines):
        shadow_text(draw, (cx, y_q + i * line_h + FONT_QUOTE_SIZE // 2), line, font_quote)

    # Source — en bas de l'image
    y_src = CANVAS_SIZE - 130
    shadow_text(draw, (cx, y_src), f"— {source}", font_source)

    # Compte Instagram — logo + nom
    IG_PURPLE = (131, 58, 180, 255)
    IG_PINK   = (225, 48, 108, 255)
    IG_ORANGE = (247, 119, 55, 255)
    BLACK     = (0, 0, 0, 255)

    ACCOUNT_TEXT = "Un_Jour_Un_Salaf"
    ICON_SIZE    = 26   # taille du logo Instagram
    try:
        font_account = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 26)
    except Exception:
        font_account = load_font(24)

    y_account = CANVAS_SIZE - 65

    # Largeur totale logo + espace + texte
    text_w = draw.textlength(ACCOUNT_TEXT, font=font_account)
    gap    = 8
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

    # ── Texte avec contour dégradé ───────────────────────────────────────────
    tx = int(x_start + ICON_SIZE + gap)
    ty = y_account
    for stroke, color in [(3, IG_PURPLE), (2, IG_PINK), (1, IG_ORANGE)]:
        draw.text((tx, ty), ACCOUNT_TEXT, font=font_account, fill=color, anchor="lm",
                  stroke_width=stroke, stroke_fill=color)
    draw.text((tx, ty), ACCOUNT_TEXT, font=font_account, fill=BLACK, anchor="lm")

    result = Image.alpha_composite(bg, overlay).convert("RGB")
    result.save(output_path, "JPEG", quality=95)
    print(f"✅ Image générée : {output_path}")
    return output_path


if __name__ == "__main__":
    generate(
        name="Ibn al-Qayyim",
        quote="La patience est de trois sortes : la patience dans l'obéissance à Allah, la patience face aux interdits d'Allah, et la patience face aux décrets douloureux d'Allah.",
        source="Madarij as-Salikin",
    )
