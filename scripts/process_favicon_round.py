#!/usr/bin/env python3
"""Regenerate favicons with clearly rounded corners (app-icon style).

Source: assets/img/brand/isotipo-dark-t.png (white B. + pink dot, transparent).
Outputs rounded PNG icons + a rounded multi-size favicon.ico.
"""
import os
from PIL import Image, ImageDraw

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND = os.path.join(REPO, "assets/img/brand")
FAV = os.path.join(REPO, "assets/img/favicon")
os.makedirs(FAV, exist_ok=True)

iso = Image.open(os.path.join(BRAND, "isotipo-dark-t.png")).convert("RGBA")


def rounded_icon(size, bg=(10, 10, 10), radius_frac=0.24, pad_frac=0.22, supersample=4):
    """Rounded-square icon, transparent outside the radius, B. centered."""
    S = size * supersample
    # rounded-rect mask (anti-aliased via supersampling)
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, S - 1, S - 1], radius=int(S * radius_frac), fill=255)
    plate = Image.new("RGBA", (S, S), bg + (255,))
    canvas = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    canvas = Image.composite(plate, canvas, mask)
    # paste logo
    logo = iso.copy()
    inner = int(S * (1 - pad_frac * 2))
    lw, lh = logo.size
    scale = min(inner / lw, inner / lh)
    logo = logo.resize((max(1, int(lw * scale)), max(1, int(lh * scale))), Image.LANCZOS)
    canvas.alpha_composite(logo, ((S - logo.size[0]) // 2, (S - logo.size[1]) // 2))
    return canvas.resize((size, size), Image.LANCZOS)


sizes = [(512, "icon-512.png"), (192, "icon-192.png"), (180, "apple-touch-icon.png"),
         (48, "favicon-48.png"), (32, "favicon-32.png"), (16, "favicon-16.png")]
for size, fname in sizes:
    # tiny sizes: a touch more radius so the rounding is unmistakable
    rf = 0.24 if size >= 48 else 0.27
    rounded_icon(size, radius_frac=rf).save(os.path.join(FAV, fname), optimize=True)
    print("favicon:", fname, size)

# Multi-size .ico with rounded transparent corners (PNG-compressed entries keep alpha)
ico = rounded_icon(64, radius_frac=0.25)
ico.save(os.path.join(REPO, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
print("favicon.ico (rounded, 16/32/48/64)")
print("DONE")
