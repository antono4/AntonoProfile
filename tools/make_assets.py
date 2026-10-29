#!/usr/bin/env python3
"""Generate the site's raster assets (social card, PWA icons, touch icon).

Optional: the site itself needs no dependencies. Run this only when you want to
regenerate the images under assets/img/.

Run:  python3 tools/make_assets.py

Requires Pillow, plus the brand fonts. Download them once with:

    mkdir -p /tmp/fonts
    curl -L -o /tmp/fonts/Sora.ttf \
      'https://raw.githubusercontent.com/google/fonts/main/ofl/sora/Sora%5Bwght%5D.ttf'
    curl -L -o /tmp/fonts/Manrope.ttf \
      'https://raw.githubusercontent.com/google/fonts/main/ofl/manrope/Manrope%5Bwght%5D.ttf'

Point FONT_DIR at wherever you put them.
"""
import pathlib
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
FONT_DIR = pathlib.Path("/tmp/fonts")

# Mirrors the tokens in assets/css/style.css so the cards match the live site.
BG = (11, 17, 22)
FOREGROUND = (230, 241, 244)
MUTED = (120, 138, 150)
ACCENT = (58, 217, 191)
ACCENT_DEEP = (26, 122, 112)
GLOW_A = (34, 211, 238)
GLOW_B = (74, 222, 128)


def font(name, size, weight=None):
    path = FONT_DIR / name
    if not path.exists():
        sys.exit(
            "Missing font %s. See the docstring for the curl commands." % path
        )
    f = ImageFont.truetype(str(path), size)
    if weight is not None:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass  # static font: the default weight is fine
    return f


def radial(size, centre, radius, colour, alpha):
    """One soft glow, composited additively-ish over the dark canvas."""
    layer = Image.new("RGB", size, (0, 0, 0))
    d = ImageDraw.Draw(layer)
    steps = 48
    for i in range(steps, 0, -1):
        r = radius * i / steps
        a = alpha * (1 - i / steps) ** 1.7
        box = [centre[0] - r, centre[1] - r, centre[0] + r, centre[1] + r]
        d.ellipse(box, fill=tuple(int(c * a) for c in colour))
    return layer


def texture(size, step=26, alpha=0.045):
    """Faint diagonal hatch, echoing the .portrait frame on the site."""
    layer = Image.new("RGB", size, (0, 0, 0))
    d = ImageDraw.Draw(layer)
    v = int(255 * alpha)
    for x in range(-size[1], size[0], step):
        d.line([(x, 0), (x + size[1], size[1])], fill=(v, v, v), width=1)
    return layer


def composite_glow(base, layer):
    """Additive screen of `layer` onto `base`, clamped."""
    return ImageChops.screen(base, layer)


def gradient_text(text, fnt, top, bottom):
    """Render `text` once and return (gradient-filled RGB, alpha mask)."""
    probe = Image.new("L", (10, 10))
    pd = ImageDraw.Draw(probe)
    box = fnt.getbbox(text)
    size = (int(pd.textlength(text, font=fnt)) + 6, box[3] - box[1] + 8)

    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).text((3 - box[0], 4 - box[1]), text, font=fnt, fill=255)

    grad = Image.new("RGB", size)
    gd = ImageDraw.Draw(grad)
    h = size[1]
    for y in range(h):
        t = y / max(1, h - 1)
        gd.line(
            [(0, y), (size[0], y)],
            fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)),
        )
    return grad, mask


def rounded_icon(size, radius_ratio=0.22, pad_ratio=0.30, maskable=False):
    """App icon: dark tile with the accent bracket mark.

    Transparent outside the rounded corners so the icon sits cleanly on light
    backgrounds and in launchers. A maskable icon is full-bleed with the mark
    inside the safe zone, because the launcher supplies its own mask.
    """
    s = size
    ss = 4  # supersample for smooth curves
    tile = Image.new("RGB", (s * ss, s * ss), BG)
    tile = composite_glow(
        tile, radial((s * ss, s * ss), (s * ss * 0.18, s * ss * 0.12), s * ss * 0.9, GLOW_A, 0.55)
    )

    d = ImageDraw.Draw(tile)
    inset = int(s * ss * (0.22 if maskable else pad_ratio))
    lo, hi = inset, s * ss - inset
    w = max(3, int(s * ss * 0.075))
    d.line([(lo, hi), (lo, lo), (hi, hi), (hi, lo)], fill=ACCENT, width=w, joint="curve")
    for pt in [(lo, hi), (lo, lo), (hi, hi), (hi, lo)]:
        d.ellipse(
            [pt[0] - w // 2, pt[1] - w // 2, pt[0] + w // 2, pt[1] + w // 2],
            fill=ACCENT,
        )
    tile = tile.resize((s, s), Image.LANCZOS)

    if maskable:
        return tile.convert("RGBA")

    mask = Image.new("L", (s * ss, s * ss), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, s * ss - 1, s * ss - 1], radius=int(s * ss * radius_ratio), fill=255
    )
    mask = mask.resize((s, s), Image.LANCZOS)

    out = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    out.paste(tile, (0, 0), mask)
    return out


def og_cover():
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), BG)

    img = composite_glow(img, radial((W, H), (W * 0.08, H * 0.05), 760, GLOW_A, 0.55))
    img = composite_glow(img, radial((W, H), (W * 0.95, H * 1.0), 820, GLOW_B, 0.40))
    img = composite_glow(img, texture((W, H)))

    d = ImageDraw.Draw(img)

    # Hairline frame, echoing the site's bordered panels.
    d.rectangle([28, 28, W - 29, H - 29], outline=(30, 42, 50), width=2)

    mono = font("Manrope.ttf", 21, 600)
    label = "EKOSISTEM TEKNOLOGI PERSONAL"
    d.text((78, 92), " ".join(label), font=mono, fill=ACCENT)

    # Wordmark, gradient-filled via a mask.
    big = font("Sora.ttf", 168, 700)
    grad, mask = gradient_text("Antono", big, FOREGROUND, ACCENT)
    img.paste(grad, (74, 168), mask)

    body = font("Manrope.ttf", 34, 500)
    d = ImageDraw.Draw(img)
    for i, line in enumerate(
        [
            "Produk, alat, portal pengetahuan,",
            "dan sistem rekayasa.",
        ]
    ):
        d.text((80, 400 + i * 50), line, font=body, fill=(196, 210, 218))

    small = font("Manrope.ttf", 24, 500)
    d.text((80, H - 96), "antono4.github.io/AntonoProfile", font=small, fill=MUTED)

    # A restrained bracket mark on the right, balancing the type block.
    mark = rounded_icon(300, radius_ratio=0.16, pad_ratio=0.26)
    img.paste(mark, (W - 300 - 96, (H - 300) // 2 - 14))

    img.save(IMG / "og-cover.png", "PNG", optimize=True)
    print("wrote assets/img/og-cover.png", img.size)


def main():
    IMG.mkdir(parents=True, exist_ok=True)
    og_cover()
    # iOS ignores alpha and composites on black, so the touch icon is full-bleed
    # opaque like the maskable one; iOS applies its own corner mask.
    rounded_icon(180, maskable=True).save(IMG / "apple-touch-icon.png", "PNG", optimize=True)
    print("wrote assets/img/apple-touch-icon.png")
    rounded_icon(192).save(IMG / "icon-192.png", "PNG", optimize=True)
    print("wrote assets/img/icon-192.png")
    rounded_icon(512).save(IMG / "icon-512.png", "PNG", optimize=True)
    print("wrote assets/img/icon-512.png")
    rounded_icon(512, maskable=True).save(IMG / "icon-maskable-512.png", "PNG", optimize=True)
    print("wrote assets/img/icon-maskable-512.png")


if __name__ == "__main__":
    main()
