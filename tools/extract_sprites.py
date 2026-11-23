"""Cut Mr X sprites out of the approved reference sheets.

Every sprite is a crop of approved artwork; nothing is redrawn. The cut follows Mr X's own lavender
sticker outline (see cut()), so the edge is the artist's edge.

  python3 tools/extract_sprites.py            -> assets/characters/mrx/sprites/*.png + contact sheet
Crop boxes live in assets/characters/mrx/crops.json so they can be tuned without code changes.
"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1] / "assets/characters/mrx"
SRC = {"turnaround": ROOT / "source/mrx_turnaround.png", "sheet": ROOT / "source/mrx_character_sheet.png"}

def cut(img, box, thr=150, grow=1, seeds=None):
    """Mr X is drawn with a light lavender sticker outline on every sheet. Use it as a wall:
    flood-fill the background from the crop border through pixels darker than `thr`;
    everything the fill can't reach (outline included) is the character. Exact pixels, nothing redrawn."""
    crop = np.asarray(img.crop(box).convert("RGB")).astype(float)
    lum = crop @ [0.299, 0.587, 0.114]
    wall = lum > thr
    if grow: wall = ndimage.binary_dilation(wall, iterations=grow)
    lab, n = ndimage.label(~wall)
    if seeds:   # explicit background points (x, y in crop space) for art that touches its panel frame
        border = {lab[y, x] for x, y in seeds} - {0}
    else:
        border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(border))
    fg = ~bg
    if grow: fg = ndimage.binary_erosion(fg, iterations=grow) | (fg & (lum > thr))  # give back the dilation
    lab2, n2 = ndimage.label(fg)
    if n2 > 1:
        sizes = ndimage.sum(fg, lab2, range(1, n2 + 1))
        fg = np.isin(lab2, [i + 1 for i, s in enumerate(sizes) if s > 0.03 * sizes.max()])
    alpha = ndimage.gaussian_filter(fg.astype(float), 0.5)
    rgba = np.dstack([crop, alpha * 255]).clip(0, 255).astype(np.uint8)
    im = Image.fromarray(rgba, "RGBA")
    return im.crop(im.getbbox())

def cut_color(img, box, sat_min=0.16, v_min=0.12, v_max=0.80, close=2):
    """For sheet panels where the art touches frames (no closed outline): background = the sheet's
    purple panel colour. Mr X is black / white / skin / blue, so purple is safe to drop; interior
    holes (purple rim-light on his clothes) are filled back in."""
    crop = np.asarray(img.crop(box).convert("RGB")).astype(float) / 255
    mx, mn = crop.max(2), crop.min(2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    r, g, b = crop[..., 0], crop[..., 1], crop[..., 2]
    purple = (b > g + 0.04) & (r > g - 0.02) & (sat > sat_min) & (mx > v_min) & (mx < v_max)
    fg = ~purple
    fg = ndimage.binary_opening(fg, iterations=1)
    fg = ndimage.binary_closing(fg, iterations=close)
    fg = ndimage.binary_fill_holes(fg)
    lab, n = ndimage.label(fg)
    if n > 1:
        sizes = ndimage.sum(fg, lab, range(1, n + 1))
        fg = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s > 0.05 * sizes.max()])
    alpha = ndimage.gaussian_filter(fg.astype(float), 0.5)
    rgba = np.dstack([crop * 255, alpha * 255]).clip(0, 255).astype(np.uint8)
    im = Image.fromarray(rgba, "RGBA")
    return im.crop(im.getbbox())

crops = json.loads((ROOT / "crops.json").read_text())
only = set(sys.argv[1:])
from PIL import ImageDraw
def erased(img, polys, fill):
    """Paint sheet background colour over stray marks (impact lines, panel edges) that touch the art.
    Only removes non-character marks; never adds artwork."""
    if not polys: return img
    img = img.copy(); d = ImageDraw.Draw(img)
    for poly in polys: d.polygon([tuple(p) for p in poly], fill=fill)
    return img

for name, spec in crops.items():
    if only and name not in only: continue
    img = Image.open(SRC[spec["src"]]).convert("RGB")
    img = erased(img, spec.get("erase"), tuple(spec.get("erase_fill", [104, 84, 150])))
    if spec.get("method") == "color": sp = cut_color(img, tuple(spec["box"]), spec.get("sat_min", 0.16))
    else: sp = cut(img, tuple(spec["box"]), spec.get("thr", 150), spec.get("grow", 1), spec.get("seeds"))
    if spec.get("mirror"): sp = sp.transpose(Image.FLIP_LEFT_RIGHT)
    sp.save(ROOT / f"sprites/{name}.png")
    print(f"{name:22s} {sp.size}")

# review sheet on a checkerboard
names = [n for n in crops if (ROOT / f"sprites/{n}.png").exists()]
th = 360
tiles = []
for n in names:
    sp = Image.open(ROOT / f"sprites/{n}.png")
    s = th / sp.height; sp = sp.resize((max(1, int(sp.width * s)), th), Image.LANCZOS)
    bg = Image.new("RGBA", (sp.width + 20, th + 20), (255, 255, 255, 255))
    ck = np.indices((th + 20, sp.width + 20)).sum(0) // 12 % 2
    bg = Image.fromarray(np.where(ck[..., None], [230, 230, 230, 255], [200, 255, 200, 255]).astype(np.uint8))
    bg.alpha_composite(sp, (10, 10)); tiles.append(bg)
W = sum(t.width for t in tiles); sheet = Image.new("RGBA", (W, th + 20), "white")
x = 0
for t in tiles: sheet.paste(t, (x, 0)); x += t.width
sheet.convert("RGB").save(ROOT / "sprites_contact.png")
