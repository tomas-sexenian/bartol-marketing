#!/usr/bin/env python3
"""Process round-2 feedback assets for Bartol Marketing.

Sources live in /tmp/bartol-feedback (extracted from the client's zip).
Outputs:
  assets/img/brand/   -> transparent, theme-aware isotipo + vertical logos
  assets/img/clients/ -> deluno/magnolias logos + romina photo
  assets/img/reel/    -> carrete photos (webp)
  assets/img/favicon/ -> regenerated from the B. isotipo (bugfix)
"""
import os
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FB = "/tmp/bartol-feedback"
LOGOS = os.path.join(FB, "drive-download-20260530T231941Z-3-001/logos_src")
CLIENT_LOGOS = os.path.join(FB, "Logo deluno y magnolias")
CARRETE = os.path.join(FB, "carrete_jpg")

OUT_BRAND = os.path.join(REPO, "assets/img/brand")
OUT_CLIENTS = os.path.join(REPO, "assets/img/clients")
OUT_REEL = os.path.join(REPO, "assets/img/reel")
OUT_FAV = os.path.join(REPO, "assets/img/favicon")
for d in (OUT_BRAND, OUT_CLIENTS, OUT_REEL, OUT_FAV):
    os.makedirs(d, exist_ok=True)

PINK = (243, 104, 150)


# ---------- helpers ----------
def extract_on_black(path):
    """Logo on black bg -> RGBA transparent, un-premultiplied. White stays white, pink stays pink."""
    img = Image.open(path).convert("RGB")
    px = img.load()
    w, h = img.size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    op = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            a = max(r, g, b)  # distance from black
            if a < 8:
                continue
            # un-premultiply against black
            R = min(255, int(r * 255 / a))
            G = min(255, int(g * 255 / a))
            B = min(255, int(b * 255 / a))
            op[x, y] = (R, G, B, a)
    return out


def to_light_variant(rgba):
    """Recolor near-white ink to black; keep pink. Alpha preserved."""
    img = rgba.copy()
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            if min(r, g, b) > 135:           # whitish ink -> black
                px[x, y] = (0, 0, 0, a)
            # else keep (pink dot / pink MARKETING)
    return img


def autocrop(rgba, pad_frac=0.04):
    bbox = rgba.getbbox()
    if not bbox:
        return rgba
    l, t, r, b = bbox
    w, h = rgba.size
    pad = int(max(r - l, b - t) * pad_frac)
    return rgba.crop((max(0, l - pad), max(0, t - pad), min(w, r + pad), min(h, b + pad)))


def trim_white(path, pad_frac=0.08):
    """Trim white border from a logo-on-white image; return RGB on white."""
    img = Image.open(path).convert("RGB")
    gray = img.convert("L")
    mask = gray.point(lambda p: 0 if p > 244 else 255)
    bbox = mask.getbbox()
    if not bbox:
        bbox = (0, 0, img.size[0], img.size[1])
    l, t, r, b = bbox
    w, h = img.size
    pad = int(max(r - l, b - t) * pad_frac)
    return img.crop((max(0, l - pad), max(0, t - pad), min(w, r + pad), min(h, b + pad)))


# ---------- 1. Brand logos: isotipo (4.png) + vertical (1.png) ----------
# 4.png = B. white + pink dot on black  (isotipo)
iso_dark = autocrop(extract_on_black(os.path.join(LOGOS, "4.png")))
iso_dark.save(os.path.join(OUT_BRAND, "isotipo-dark-t.png"), optimize=True)
to_light_variant(iso_dark).save(os.path.join(OUT_BRAND, "isotipo-light-t.png"), optimize=True)
print("isotipo-dark-t / isotipo-light-t", iso_dark.size)

# 1.png = vertical: MARKETING (pink) + big B (white) on black
vert_dark = autocrop(extract_on_black(os.path.join(LOGOS, "1.png")))
vert_dark.save(os.path.join(OUT_BRAND, "vertical-dark-t.png"), optimize=True)
to_light_variant(vert_dark).save(os.path.join(OUT_BRAND, "vertical-light-t.png"), optimize=True)
print("vertical-dark-t / vertical-light-t", vert_dark.size)


# ---------- 2. Favicon bugfix: regenerate from isotipo on black square ----------
def square_iso(bg=(10, 10, 10), pad_frac=0.26):
    base = iso_dark  # white B + pink dot, transparent
    c = base
    w, h = c.size
    side = int(max(w, h) * (1 + pad_frac * 2))
    canvas = Image.new("RGBA", (side, side), bg + (255,))
    canvas.alpha_composite(c, ((side - w) // 2, (side - h) // 2))
    return canvas.convert("RGB")

iso_sq = square_iso()
for size, fname in [(512, "icon-512.png"), (192, "icon-192.png"),
                    (180, "apple-touch-icon.png"), (48, "favicon-48.png"),
                    (32, "favicon-32.png"), (16, "favicon-16.png")]:
    iso_sq.resize((size, size), Image.LANCZOS).save(os.path.join(OUT_FAV, fname), optimize=True)
iso_sq.resize((256, 256), Image.LANCZOS).save(
    os.path.join(REPO, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
print("favicons regenerated from isotipo")


# ---------- 3. Client logos (deluno teal / magnolias rose-gold) on white plaque ----------
trim_white(os.path.join(CLIENT_LOGOS, "10.png")).save(os.path.join(OUT_CLIENTS, "deluno.png"), optimize=True)
trim_white(os.path.join(CLIENT_LOGOS, "11.png")).save(os.path.join(OUT_CLIENTS, "magnolias.png"), optimize=True)
print("client logos: deluno, magnolias")


# ---------- 4. Romina Lucero photo ----------
def to_webp(src, dst, max_side=1100, quality=82):
    img = Image.open(src).convert("RGB")
    w, h = img.size
    if max(w, h) > max_side:
        if w >= h:
            img = img.resize((max_side, round(h * max_side / w)), Image.LANCZOS)
        else:
            img = img.resize((round(w * max_side / h), max_side), Image.LANCZOS)
    img.save(dst, "WEBP", quality=quality, method=6)

to_webp(os.path.join(CARRETE, "IMG_6471.jpg"), os.path.join(OUT_CLIENTS, "romina.webp"))
print("client photo: romina")


# ---------- 5. Carrete photos -> webp ----------
# (IMG_6471 excluded — it's Romina's client photo)
reel_map = [
    ("IMG_1822.jpg", "reel-01.webp"),   # Camila pointing / talking (YouTube)
    ("IMG_3226.jpg", "reel-02.webp"),   # nutrition content shoot
    ("IMG_5370.jpg", "reel-03.webp"),   # Bravery book
    ("IMG_5887.jpg", "reel-04.webp"),   # Bernese (grooming)
    ("IMG_6169.jpg", "reel-05.webp"),   # Bernese (grooming)
    ("IMG_8887.jpg", "reel-06.webp"),   # filming setup (YouTube)
    ("3CC1F40C-934F-425C-A2A3-3ACBA7491011.jpg", "reel-07.webp"),  # Bauta bag
    ("5BA2A07D-7C78-423C-899B-69AF46D3D305.jpg", "reel-08.webp"),  # pizza counter
    ("73DF2CAC-4918-4388-9621-DE67DB5EBAC1.jpg", "reel-09.webp"),  # dough
    ("B960C670-B69F-4719-97B4-D85C7BD81EA9.jpg", "reel-10.webp"),  # Bauta man
    ("D5A58A76-3C8D-4E55-B24E-1F17DFB59115.jpg", "reel-11.webp"),  # oven
]
for src, dst in reel_map:
    to_webp(os.path.join(CARRETE, src), os.path.join(OUT_REEL, dst))
print(f"carrete: {len(reel_map)} photos")

print("DONE")
