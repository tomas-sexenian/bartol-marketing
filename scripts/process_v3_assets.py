#!/usr/bin/env python3
"""Round-3 assets: rounded favicons, transparent client logos, footer lockup.

Sources are already in the repo:
  assets/img/brand/isotipo-dark-t.png      -> favicon source (white B. + pink dot)
  assets/img/brand/logo-principal-dark.png -> footer lockup source (white+pink on black)
  assets/img/clients/deluno.png            -> teal logo on white
  assets/img/clients/magnolias.png         -> rose-gold logo on white
"""
import os
from PIL import Image, ImageDraw

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND = os.path.join(REPO, "assets/img/brand")
CLIENTS = os.path.join(REPO, "assets/img/clients")
FAV = os.path.join(REPO, "assets/img/favicon")


# ---------- helpers ----------
def autocrop(rgba, pad_frac=0.04):
    bbox = rgba.getbbox()
    if not bbox:
        return rgba
    l, t, r, b = bbox
    w, h = rgba.size
    pad = int(max(r - l, b - t) * pad_frac)
    return rgba.crop((max(0, l - pad), max(0, t - pad), min(w, r + pad), min(h, b + pad)))


def white_to_transparent(path):
    """Remove white background, keep colored ink crisp (min-channel threshold)."""
    img = Image.open(path).convert("RGB")
    px = img.load()
    w, h = img.size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    op = out.load()
    HI, LO = 248, 232  # min>=HI -> transparent; min<=LO -> opaque; ramp between
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            m = min(r, g, b)
            if m >= HI:
                continue
            a = 255 if m <= LO else int((HI - m) / (HI - LO) * 255)
            op[x, y] = (r, g, b, a)
    return autocrop(out)


def extract_on_black(path):
    """Logo on black -> RGBA transparent, un-premultiplied (white stays white)."""
    img = Image.open(path).convert("RGB")
    px = img.load()
    w, h = img.size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    op = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            a = max(r, g, b)
            if a < 8:
                continue
            op[x, y] = (min(255, int(r * 255 / a)), min(255, int(g * 255 / a)),
                        min(255, int(b * 255 / a)), a)
    return autocrop(out)


def recolor_white_ink_to_black(rgba):
    """Whitish ink -> black; keep pink. Alpha preserved."""
    img = rgba.copy()
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a and min(r, g, b) > 135:
                px[x, y] = (0, 0, 0, a)
    return img


def rounded_icon(src_rgba, size, bg, radius_frac=0.22, pad_frac=0.20):
    """Square icon with rounded corners (transparent outside), B. centered."""
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    # rounded-rect alpha mask
    mask = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=int(size * radius_frac), fill=255)
    plate = Image.new("RGBA", (size, size), bg + (255,))
    canvas = Image.composite(plate, canvas, mask)
    # paste logo
    logo = src_rgba.copy()
    inner = int(size * (1 - pad_frac * 2))
    lw, lh = logo.size
    scale = min(inner / lw, inner / lh)
    logo = logo.resize((max(1, int(lw * scale)), max(1, int(lh * scale))), Image.LANCZOS)
    canvas.alpha_composite(logo, ((size - logo.size[0]) // 2, (size - logo.size[1]) // 2))
    return canvas


# ---------- 1. client logos -> transparent ----------
white_to_transparent(os.path.join(CLIENTS, "deluno.png")).save(
    os.path.join(CLIENTS, "deluno-t.png"), optimize=True)
white_to_transparent(os.path.join(CLIENTS, "magnolias.png")).save(
    os.path.join(CLIENTS, "magnolias-t.png"), optimize=True)
print("client logos -> transparent: deluno-t, magnolias-t")


# ---------- 2. footer principal lockup -> transparent (dark + light) ----------
principal_dark = extract_on_black(os.path.join(BRAND, "logo-principal-dark.png"))
principal_dark.save(os.path.join(BRAND, "principal-dark-t.png"), optimize=True)
recolor_white_ink_to_black(principal_dark).save(
    os.path.join(BRAND, "principal-light-t.png"), optimize=True)
print("footer lockup -> principal-dark-t / principal-light-t", principal_dark.size)


# ---------- 3. rounded favicons from isotipo ----------
iso = Image.open(os.path.join(BRAND, "isotipo-dark-t.png")).convert("RGBA")
for size, fname in [(512, "icon-512.png"), (192, "icon-192.png"),
                    (180, "apple-touch-icon.png"), (48, "favicon-48.png"),
                    (32, "favicon-32.png"), (16, "favicon-16.png")]:
    r = 0.20 if size >= 64 else 0.16  # slightly less rounding at tiny sizes
    rounded_icon(iso, size, (10, 10, 10), radius_frac=r).save(
        os.path.join(FAV, fname), optimize=True)
print("rounded favicons regenerated")

# multi-size .ico (rounded). ICO has no alpha rounding in all viewers, but PNG-in-ICO keeps it.
ico = rounded_icon(iso, 256, (10, 10, 10), radius_frac=0.20)
ico.save(os.path.join(REPO, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
print("favicon.ico (rounded)")

print("DONE")
