#!/usr/bin/env python3
"""Process Bartol Marketing brand assets into web-ready files.

Run once from the repo root: python3 scripts/process_assets.py
Source PNGs live in /tmp/bartol-assets (extracted from temp-resources zips).
"""
import os
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = "/tmp/bartol-assets"

OUT_MANUELA = os.path.join(REPO, "assets/img/manuela")
OUT_BRAND = os.path.join(REPO, "assets/img/brand")
OUT_FAV = os.path.join(REPO, "assets/img/favicon")
for d in (OUT_MANUELA, OUT_BRAND, OUT_FAV):
    os.makedirs(d, exist_ok=True)

PINK = (243, 104, 150)  # #F36896

def alpha_from_darkness(img):
    """Return L-mode alpha channel: dark pixels -> opaque, white -> transparent."""
    gray = img.convert("L")
    return gray.point(lambda p: 255 - p)

def cropped_bbox(alpha, thresh=22, pad_frac=0.06):
    mask = alpha.point(lambda p: 255 if p > thresh else 0)
    bbox = mask.getbbox()
    if not bbox:
        return None
    l, t, r, b = bbox
    w, h = alpha.size
    pad = int(max(r - l, b - t) * pad_frac)
    return (max(0, l - pad), max(0, t - pad), min(w, r + pad), min(h, b + pad))

# ---- 1. Manuela faces -> transparent alpha masks (black ink) ----
manuela_map = {1: "happy", 2: "surprised", 3: "heart", 4: "shy", 5: "pensive"}
manuela_imgs = {}
for n, name in manuela_map.items():
    img = Image.open(os.path.join(SRC, "elementos", f"{n}.png"))
    alpha = alpha_from_darkness(img)
    bbox = cropped_bbox(alpha)
    size = img.size
    z = Image.new("L", size, 0)
    rgba = Image.merge("RGBA", (z, z, z, alpha))  # black ink + darkness alpha
    if bbox:
        rgba = rgba.crop(bbox)
    rgba.save(os.path.join(OUT_MANUELA, f"manuela-{name}.png"), optimize=True)
    manuela_imgs[name] = (rgba, alpha, bbox)
    print(f"manuela-{name}.png {rgba.size}")

# ---- 2. Keep a few curated brand logos (source PNGs) ----
# Catalogued from the source set:
#   4.png = "B." white + pink dot on BLACK   (isotipo, dark)
#   6.png = "B." black + white dot on PINK   (isotipo, on pink)
#   7.png = "BARTOL" white + "MARKETING" pink on BLACK (principal, dark)
#   8.png = "BARTOL" black + "MARKETING" pink on WHITE (principal, light)
brand_keep = {
    "7.png": "logo-principal-dark.png",
    "8.png": "logo-principal-light.png",
    "4.png": "isotipo-dark.png",
    "6.png": "isotipo-light.png",
}
for src, dst in brand_keep.items():
    Image.open(os.path.join(SRC, "logos", src)).save(os.path.join(OUT_BRAND, dst), optimize=True)
    print("brand:", dst)

def content_square(img, pad_frac=0.16, bg=(0, 0, 0)):
    """Crop to non-bg content, re-center on a square canvas with padding."""
    gray = img.convert("L")
    corner = gray.getpixel((2, 2))
    if corner < 40:  # dark bg -> content is bright
        mask = gray.point(lambda p: 255 if p > 40 else 0)
    else:            # light bg -> content is dark
        mask = gray.point(lambda p: 255 if p < 215 else 0)
    bbox = mask.getbbox()
    if not bbox:
        bbox = (0, 0, img.size[0], img.size[1])
    l, t, r, b = bbox
    cx, cy = (l + r) // 2, (t + b) // 2
    half = int(max(r - l, b - t) * (1 + pad_frac) / 2)
    canvas = Image.new("RGB", (half * 2, half * 2), bg)
    region = img.convert("RGB").crop((cx - half, cy - half, cx + half, cy + half))
    canvas.paste(region, (0, 0))
    return canvas

# ---- 3. Favicons / app icons from the B. isotipo (white B on black) ----
iso = Image.open(os.path.join(SRC, "logos", "8.png"))
iso_sq = content_square(iso, pad_frac=0.30, bg=(10, 10, 10))
for size, fname in [(512, "icon-512.png"), (192, "icon-192.png"),
                    (180, "apple-touch-icon.png"), (48, "favicon-48.png"),
                    (32, "favicon-32.png"), (16, "favicon-16.png")]:
    iso_sq.resize((size, size), Image.LANCZOS).save(os.path.join(OUT_FAV, fname), optimize=True)
    print("favicon:", fname)
iso_sq.resize((256, 256), Image.LANCZOS).save(
    os.path.join(REPO, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
print("favicon.ico")

# ---- 4. OG image (1200x630) ----
og = Image.new("RGB", (1200, 630), (10, 10, 10))
# Build a clean alpha for the principal logo: black bg -> transparent, letters opaque.
logo_rgb = Image.open(os.path.join(SRC, "logos", "7.png")).convert("RGB")
logo_alpha = logo_rgb.convert("L").point(lambda p: 0 if p < 24 else 255)
logo = logo_rgb.copy()
logo.putalpha(logo_alpha)
lb = logo_alpha.getbbox()
logo_c = logo.crop(lb)
tw = 640
th = int(logo_c.size[1] * tw / logo_c.size[0])
logo_c = logo_c.resize((tw, th), Image.LANCZOS)
og.paste(logo_c, ((1200 - tw) // 2, (630 - th) // 2 - 18), logo_c)
_, h_alpha, h_bbox = manuela_imgs["heart"]
hp = h_alpha.crop(h_bbox) if h_bbox else h_alpha
pr = Image.new("L", hp.size, PINK[0]); pg = Image.new("L", hp.size, PINK[1]); pb = Image.new("L", hp.size, PINK[2])
manuela_pink = Image.merge("RGBA", (pr, pg, pb, hp))
mh = 180
mw = int(manuela_pink.size[0] * mh / manuela_pink.size[1])
manuela_pink = manuela_pink.resize((mw, mh), Image.LANCZOS)
og.paste(manuela_pink, (1200 - mw - 60, 630 - mh - 36), manuela_pink)
og.save(os.path.join(REPO, "assets/img/og-image.png"), optimize=True)
print("og-image.png", og.size)

print("DONE")
