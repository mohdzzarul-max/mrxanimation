#!/usr/bin/env python3
"""
Prepare derived assets for the ZSCENTS film.

Reads ORIGINAL files from  public/assets/
Writes DERIVED layers into public/derived/

Run again after replacing any original image:
    python3 scripts/prepare_assets.py

Nothing here alters a logo's design: logo layers are pixel crops of the
supplied files (the X logo is light-on-black, so a crop shown with
`mix-blend-mode: screen` over black is pixel-identical to the original).
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageEnhance

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "public" / "assets"
OUT = ROOT / "public" / "derived"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1920


def cover(im: Image.Image, w: int, h: int) -> Image.Image:
    s = max(w / im.width, h / im.height)
    r = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = (r.width - w) // 2
    y = (r.height - h) // 2
    return r.crop((x, y, x + w, y + h))


def backplate(name: str, src: str, blur=28, dark=0.55):
    """Small blurred, darkened 9:16 plate used behind non-9:16 photos."""
    im = Image.open(SRC / src).convert("RGB")
    im = cover(im, W // 4, H // 4).filter(ImageFilter.GaussianBlur(blur / 4))
    im = ImageEnhance.Brightness(im).enhance(dark)
    im = im.resize((W // 2, H // 2), Image.BICUBIC)
    im.save(OUT / f"{name}-bg.jpg", quality=88)


# ------------------------------------------------ 03: wooden room stand-in
# The full-resolution wooden-room photo was NOT among the uploads. Until it is
# supplied, a stand-in is lifted from storyboard panel 03 (only ~261x500 px).
# Drop the real photo at public/assets/03-wooden-room.jpg and re-run: the
# stand-in is only generated when that file is missing.
room = SRC / "03-wooden-room.jpg"
if not room.exists():
    sb = Image.open(SRC / "_storyboard-reference.png").convert("RGB")
    crop = sb.crop((362, 886, 623, 1386))
    up = crop.resize((crop.width * 3, crop.height * 3), Image.LANCZOS)
    up = up.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    up.save(room, quality=94)
    (SRC / "03-wooden-room.STANDIN.txt").write_text(
        "03-wooden-room.jpg is a low-resolution stand-in cut from the storyboard.\n"
        "Replace it with the original photo and delete this note.\n")
    print("WARNING: 03-wooden-room.jpg missing -> stand-in created from storyboard")

# ---------------------------------------------------------------- backplates
for n, s in [
    ("01", "01-father-advice.png"),
    ("02", "02-reflection.png"),
    ("03", "03-wooden-room.jpg"),
    ("05", "05-mosque-hands.png"),
    ("06", "06-booth-crowd.png"),
    ("07", "07-tiktok-live.png"),
    ("08", "08-final-collection.png"),
]:
    backplate(n, s)

# ------------------------------------------------- 08: product band, no text
# The supplied poster has farewell text baked in. The film animates that text
# as separate, editable layers, so only the bottles band is used here.
col = Image.open(SRC / "08-final-collection.png").convert("RGB")
col.crop((0, 0, col.width, 660)).save(OUT / "08-band.jpg", quality=94)

# ------------------------------------------ 07: livestream UI as layers
live = Image.open(SRC / "07-tiktok-live.png").convert("RGB")
PURCHASE_TEXT = [(284, 324), (361, 400), (436, 479), (510, 552), (586, 626),
                 (663, 706), (741, 780), (819, 858), (897, 937), (979, 1018)]
COMMENT_TEXT = [(616, 658), (684, 722), (751, 793), (818, 860), (886, 923), (953, 990)]
P_X = (884, 1192)
C_X = (24, 404)

base = live.copy()
blurred = live.filter(ImageFilter.GaussianBlur(26))
dim = ImageEnhance.Brightness(blurred).enhance(0.68)
p_box = (P_X[0] - 22, PURCHASE_TEXT[0][0] - 40, P_X[1] + 30, PURCHASE_TEXT[-1][1] + 40)
c_box = (C_X[0] - 30, COMMENT_TEXT[0][0] - 36, C_X[1] + 22, COMMENT_TEXT[-1][1] + 32)
def feather_mask(size, box, r):
    m = Image.new("L", size, 0)
    m.paste(255, box)
    return m.filter(ImageFilter.GaussianBlur(r))


for box in (p_box, c_box):
    base = Image.composite(dim, base, feather_mask(live.size, box, 12))
base.save(OUT / "07-base.jpg", quality=93)

def soft_layer(box, r=6):
    """Crop with feathered alpha edges so it sits softly on the base."""
    im = live.crop(box).convert("RGBA")
    w, h = im.size
    m = Image.new("L", (w, h), 0)
    m.paste(255, (r, r, w - r, h - r))
    im.putalpha(m.filter(ImageFilter.GaussianBlur(r / 2)))
    return im


layers = []
for i, (t, b) in enumerate(PURCHASE_TEXT):
    box = (P_X[0], t - 16, P_X[1], b + 16)
    soft_layer(box).save(OUT / f"07-purchase-{i:02d}.png")
    layers.append(("purchase", i, box))
for i, (t, b) in enumerate(COMMENT_TEXT):
    box = (C_X[0], t - 10, C_X[1], b + 8)
    soft_layer(box).save(OUT / f"07-comment-{i:02d}.png")
    layers.append(("comment", i, box))
with open(OUT / "07-layers.txt", "w") as f:
    for kind, i, box in layers:
        f.write(f"{kind} {i} {box}\n")

# --------------------------------------------- 10: X logo emblem / wordmark
xl = Image.open(SRC / "10-logo-experimental.png").convert("RGB")
xa = np.array(xl)
EMB_ROWS = (290, 775)
WORD_ROWS = (780, 925)
emb = np.zeros_like(xa)
emb[EMB_ROWS[0]:EMB_ROWS[1]] = xa[EMB_ROWS[0]:EMB_ROWS[1]]
word = np.zeros_like(xa)
word[WORD_ROWS[0]:WORD_ROWS[1]] = xa[WORD_ROWS[0]:WORD_ROWS[1]]
Image.fromarray(emb).save(OUT / "10-emblem.png")
Image.fromarray(word).save(OUT / "10-wordmark.png")
# white-with-alpha versions, used only as masks / particle targets
for nm, arr in (("emblem", emb), ("wordmark", word)):
    lum = arr.mean(2)
    a = np.clip((lum - 12) * (255 / 200), 0, 255).astype(np.uint8)
    rgba = np.dstack([np.full_like(a, 255)] * 3 + [a])
    Image.fromarray(rgba, "RGBA").save(OUT / f"10-{nm}-alpha.png")

# ----------------------------------------------------------- film grain
rng = np.random.default_rng(7)
for i in range(6):
    n = rng.normal(128, 38, (H // 3, W // 3)).clip(0, 255).astype(np.uint8)
    Image.fromarray(n, "L").resize((W, H), Image.NEAREST).save(OUT / f"grain-{i}.png")

print("derived assets written to", OUT)
