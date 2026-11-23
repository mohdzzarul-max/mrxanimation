"""Replace the drawn placeholder bottle in Mr X's hand with the real ZSCENTS product.

For each drawing in bottle_boxes.json: the drawn bottle is located by its white rim inside the search box;
the real bottle (assets/products/zscents_bottle.png) is scaled to the drawn bottle's height and centred on it;
the drawing's own skin pixels (fingers, plus their ink outline) are laid back on top, so the drawn grip holds
the real bottle. Every drawing (with or without a bottle) is written to poses_draft/final/.
  python3 tools/place_product.py"""
import json, shutil
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

R = Path(__file__).resolve().parents[1] / "assets"
P = R / "characters/mrx/poses_draft"; OUT = P / "final"; OUT.mkdir(exist_ok=True)
boxes = {k: v for k, v in json.loads((P / "bottle_boxes.json").read_text()).items() if not k.startswith("_")}
bottle = Image.open(R / "products/zscents_bottle.png").convert("RGBA")
for f in sorted((P / "fixed").glob("*.png")):
    tid = f.stem; base = tid[:3]
    if base not in boxes: shutil.copy(f, OUT / f.name); continue
    im = Image.open(f).convert("RGBA"); a = np.asarray(im).astype(float)
    x0, y0, x1, y1 = boxes[base]
    sub = a[y0:y1, x0:x1]; rgb = sub[..., :3]; al = sub[..., 3] > 128
    lum = rgb @ [.299, .587, .114]; sat = rgb.max(2) - rgb.min(2)
    skin = al & (rgb[..., 0] > 150) & (rgb[..., 0] > rgb[..., 2] + 40)
    rim = al & (lum > 195) & (sat < 35)
    # the rim is broken up by the fingers: take every rim piece big enough to be drawn line, not a speck
    lab, n = ndimage.label(rim)
    sizes = ndimage.sum(rim, lab, range(1, n + 1))
    comp = np.isin(lab, [i + 1 for i, z in enumerate(sizes) if z > 25])
    ys, xs = np.nonzero(comp)
    bx0, by0, bx1, by1 = xs.min() + x0, ys.min() + y0, xs.max() + x0, ys.max() + y0
    h = by1 - by0; s = h / bottle.height
    b = bottle.resize((max(1, int(bottle.width * s)), max(1, int(h))), Image.LANCZOS)
    cx = (bx0 + bx1) / 2
    out = im.copy(); out.alpha_composite(b, (int(round(cx - b.width / 2)), int(by0)))
    # fingers back on top: only skin that lay ON the drawn bottle (in front of it); skin beside it now
    # falls behind the (wider) real bottle. Each finger keeps its drawn ink outline; edges are feathered.
    fing = np.zeros(a.shape[:2], bool); fing[y0:y1, x0:x1] = skin
    onb = np.zeros_like(fing); onb[by0 + 2:by1 - 1, bx0 + 2:bx1 - 1] = True
    lab, n = ndimage.label(fing)
    front = np.isin(lab, [i for i in range(1, n + 1) if (onb & (lab == i)).sum() > 0.35 * (lab == i).sum()])
    front &= ndimage.binary_dilation(onb, iterations=12)
    lab2, n2 = ndimage.label(front)                       # drop specks (< 0.4% of the bottle's area)
    front = np.isin(lab2, [i for i in range(1, n2 + 1) if (lab2 == i).sum() > 0.004 * b.width * b.height])
    lumA = a[..., :3] @ [.299, .587, .114]
    ink = ndimage.binary_dilation(front, iterations=9) & ~front & (lumA < 90) & (a[..., 3] > 128)
    keep = front | ink
    soft = ndimage.gaussian_filter(keep.astype(float), 0.7)[..., None]
    o = np.asarray(out).astype(float); o[..., :3] = o[..., :3] * (1 - soft) + a[..., :3] * soft
    o = o.clip(0, 255).astype(np.uint8)
    Image.fromarray(o).save(OUT / f.name)
    print(tid, "drawn bottle", (bx0, by0, bx1, by1), "-> real bottle", b.size)
