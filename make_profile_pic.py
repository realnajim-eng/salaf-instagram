from PIL import Image, ImageDraw
import numpy as np
import math
import sys

def make_instagram_profile(input_path, output_path, size=800, border=25):
    img = Image.open(input_path).convert("RGBA")

    w, h = img.size
    # Remove original gradient border (~3% each side)
    trim = int(min(w, h) * 0.03)
    img = img.crop((trim, trim, w - trim, h - trim))
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = max(0, (h - side) // 2 - int(side * 0.05))
    top = min(top, h - side)
    img = img.crop((left, top, left + side, top + side))
    img = img.resize((size, size), Image.LANCZOS)

    total = size + border * 2
    cx = cy = total // 2

    # Build angular gradient ring pixel by pixel
    # Colors from original: purple (#C13584) → pink (#E1306C) → red (#FD1D1D) → orange (#F77737) → yellow (#FCAF45)
    # Angle: 0=top → clockwise
    # Instagram story ring gradient: yellow → orange → red → pink → purple → blue → back
    gradient_colors = [
        (0.00, (252, 175, 69)),   # yellow
        (0.15, (247, 119, 55)),   # orange
        (0.30, (253, 29,  29)),   # red
        (0.45, (225, 48, 108)),   # pink
        (0.60, (193, 53, 132)),   # purple-pink
        (0.75, (131, 58, 180)),   # purple
        (0.88, (88,  86, 214)),   # indigo
        (1.00, (252, 175, 69)),   # back to yellow
    ]

    def interp_color(t):
        t = t % 1.0
        for i in range(len(gradient_colors) - 1):
            t0, c0 = gradient_colors[i]
            t1, c1 = gradient_colors[i + 1]
            if t0 <= t <= t1:
                f = (t - t0) / (t1 - t0)
                return tuple(int(c0[j] + f * (c1[j] - c0[j])) for j in range(3))
        return gradient_colors[-1][1]

    # Create ring image using numpy
    xs = np.arange(total)
    ys = np.arange(total)
    xx, yy = np.meshgrid(xs, ys)
    dx = xx - cx
    dy = yy - cy
    dist = np.sqrt(dx**2 + dy**2)

    r_outer = total // 2
    r_inner = r_outer - border

    ring_mask = (dist >= r_inner) & (dist <= r_outer)

    # Angle: atan2(dy, dx), shift so 0 = top, clockwise
    angle = (np.arctan2(dy, dx) + math.pi / 2) % (2 * math.pi)
    t_map = angle / (2 * math.pi)

    ring_img = np.zeros((total, total, 4), dtype=np.uint8)
    ys_idx, xs_idx = np.where(ring_mask)
    for y, x in zip(ys_idx, xs_idx):
        t = t_map[y, x]
        c = interp_color(t)
        ring_img[y, x] = (c[0], c[1], c[2], 255)

    result = Image.fromarray(ring_img, "RGBA")

    # Circular mask for the photo
    photo_mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(photo_mask).ellipse((0, 0, size, size), fill=255)
    photo_circle = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    photo_circle.paste(img, (0, 0))
    photo_circle.putalpha(photo_mask)

    result.paste(photo_circle, (border, border), photo_circle)

    result.save(output_path, "PNG")
    print(f"Saved: {output_path} ({total}x{total}px)")

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "images/background.jpg"
    dst = sys.argv[2] if len(sys.argv) > 2 else "images/profile_instagram.png"
    make_instagram_profile(src, dst)
