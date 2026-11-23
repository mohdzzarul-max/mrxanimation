"""Split the approved Mr X turnaround sprites into rig layers (no redrawing).

For each view (front, 3/4, side) in assets/characters/mrx/rig_layers.json:
  head_<view>.png   the head exactly as drawn, cut along the jaw where it meets the neck.
                    Fixed 1600x1400 canvas, neck pivot at (800, 1200) for every view.
  body_<view>.png   the same figure without its head. The neck stub is the drawn neck; its top is
                    extended upward by repeating one drawn row of the neck (outline included).
                    That extension always sits under the head.
  rig.json          canvas sizes and pivot points.
Outputs go to assets/characters/mrx/rig/.
"""
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

R = Path(__file__).resolve().parents[1] / "assets/characters/mrx"
cfg = {k: v for k, v in json.loads((R / "rig_layers.json").read_text()).items() if not k.startswith("_")}
OUT = R / "rig"; OUT.mkdir(exist_ok=True)
HEAD_W, HEAD_H, HEAD_PIV = 1600, 1400, (800, 1200)
meta = {"head_canvas": [HEAD_W, HEAD_H], "head_pivot": list(HEAD_PIV), "views": {}}

for view, c in cfg.items():
    im = Image.open(R / f"sprites_4x/{c['sprite']}.png").convert("RGBA")
    a = np.asarray(im).copy()
    alpha = a[..., 3] > 8
    # sever the head from the neck along the cut line
    cutimg = Image.new("L", im.size, 0); ImageDraw.Draw(cutimg).line([tuple(p) for p in c["cut"]], fill=255, width=5)
    cut = np.asarray(cutimg) > 0
    lab, n = ndimage.label(alpha & ~cut)
    hx, hy = c["head_seed"]
    head_mask = lab == lab[hy, hx]
    # include the cut seam pixels that belong above the line (keep the jaw outline whole)
    above = np.zeros_like(cut); ys = np.arange(im.size[1])[:, None]
    line_y = np.interp(np.arange(im.size[0]), [p[0] for p in c["cut"]], [p[1] for p in c["cut"]])
    above = ys < line_y[None, :]
    head_mask |= cut & above & alpha
    head = a.copy(); head[..., 3] = np.where(head_mask, a[..., 3], 0)
    body = a.copy(); body[..., 3] = np.where(head_mask, 0, a[..., 3])
    # neck extension under the jaw: repeat one drawn row of the neck upward (hidden by the head)
    x0, x1 = c["neck_x"]; row = c["neck_row"]
    src = a[row, x0:x1].copy()
    top = int(min(line_y[x0:x1].min(), row) - c["neck_up"])
    for y in range(top, row):
        dst = body[y, x0:x1]
        fill = (dst[:, 3] < 128) & (src[:, 3] > 0)
        dst[fill] = src[fill]
    Image.fromarray(body).save(OUT / f"body_{view}.png")
    # head into the shared canvas, pivot aligned
    px, py = c["pivot"]
    canvas = Image.new("RGBA", (HEAD_W, HEAD_H), (0, 0, 0, 0))
    canvas.alpha_composite(Image.fromarray(head), (HEAD_PIV[0] - px, HEAD_PIV[1] - py))
    canvas.save(OUT / f"head_{view}.png")
    meta["views"][view] = {"body": f"body_{view}.png", "body_size": list(im.size), "body_pivot": [px, py],
                           "head": f"head_{view}.png", "source_sprite": c["sprite"]}
    print(view, "head px:", int(head_mask.sum()), "body size:", im.size)
(OUT / "rig.json").write_text(json.dumps(meta, indent=1))
