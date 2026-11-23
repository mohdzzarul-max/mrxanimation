"""Locate the draft head in each pose drawing (white mask markings + the dark blob around them).
Writes assets/characters/mrx/poses_draft/heads_detected.json: per drawing the head ellipse
(cx, cy, rx, ry), its bounding box, and a suggested neck point (bottom of the blob at its centre).
Only used to place approved heads; tune by hand in headswap.json where needed."""
import json, glob
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

P = Path(__file__).resolve().parents[1] / "assets/characters/mrx/poses_draft"
out = {}
for f in sorted(glob.glob(str(P / "src/T*.png"))):
    tid = Path(f).name[:3]
    a = np.asarray(Image.open(f).convert("RGBA")).astype(float)
    al = a[..., 3] > 128
    rgb = a[..., :3]; lum = rgb @ [0.299, 0.587, 0.114]
    sat = rgb.max(2) - rgb.min(2)
    ys, xs = np.nonzero(al); top, bot = ys.min(), ys.max()
    white = al & (lum > 215) & (sat < 40)
    white[int(top + 0.55 * (bot - top)):] = False                      # shoes / lower body
    lab, n = ndimage.label(ndimage.binary_dilation(white, iterations=3))
    if n == 0: continue
    sizes = ndimage.sum(white, lab, range(1, n + 1))
    k = int(np.argmax(sizes)) + 1
    cy0, cx0 = ndimage.center_of_mass(lab == k)
    keep = [i + 1 for i in range(n) if sizes[i] > 150 and np.hypot(*(np.array(ndimage.center_of_mass(lab == i + 1)) - (cy0, cx0))) < 230]
    marks = np.isin(lab, keep) & white
    my, mx = np.nonzero(marks)
    mcx, mcy = mx.mean(), my.mean()
    R = 1.15 * max(mx.max() - mx.min(), my.max() - my.min())
    yy, xx = np.mgrid[0:al.shape[0], 0:al.shape[1]]
    near = np.hypot(xx - mcx, yy - mcy) < R
    blob = near & al & ((lum < 80) | marks | ((rgb[..., 0] > 170) & (rgb[..., 0] > rgb[..., 2] + 40)))
    lab2, _ = ndimage.label(blob)
    blob = lab2 == lab2[int(mcy), int(mx[np.argmin(np.abs(mx - mcx))])] if lab2[int(mcy), int(mcx)] == 0 else lab2 == lab2[int(mcy), int(mcx)]
    by, bx = np.nonzero(blob)
    cx, cy = bx.mean(), by.mean()
    rx, ry = (np.percentile(bx, 98) - np.percentile(bx, 2)) / 2, (np.percentile(by, 98) - np.percentile(by, 2)) / 2
    out[tid] = {"ell": [round(cx), round(cy), round(rx * 1.08), round(ry * 1.08)], "marks_c": [round(mcx), round(mcy)],
                "neck": [round(cx), round(np.percentile(by, 99))]}
(P / "heads_detected.json").write_text(json.dumps(out, indent=1))
for k, v in out.items(): print(k, v)
