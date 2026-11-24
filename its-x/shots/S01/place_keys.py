#!/usr/bin/env python3
"""Cut the keys out of a submitted key sheet and place each one on the S01 camera (1920x1080, alpha):
same scale for all keys, soles on the floor line (y=1000), feet centred on the body-centre mark
(x=1040 for K01-K05, x=880 for K06). Props are cut once and placed with the SAME scale and floor.
Only position and uniform scale are changed - the drawings themselves are untouched.

  python3 its-x/shots/S01/place_keys.py SHEET.png OUT_DIR
"""
import sys, os
import numpy as np
from PIL import Image

sheet, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
im = Image.open(sheet).convert('RGBA'); A = np.asarray(im)[..., 3] > 40
FLOOR, HEIGHT = 1000, 820
# boxes (x0, y0, x1, y1) on the 1672x941 sheet, above each label badge
BOX = {'K01': (150, 0, 460, 428), 'K02': (560, 0, 890, 428), 'K03': (1020, 0, 1310, 428),
       'K04': (60, 470, 380, 895), 'K05': (440, 470, 780, 895), 'K06': (780, 470, 1160, 895)}
PROPS = (1236, 560, 1640, 878)  # stops above the 'PROPS.png' label
CX = {k: (880 if k == 'K06' else 1040) for k in BOX}

def cut(box):
    x0, y0, x1, y1 = box; m = A[y0:y1, x0:x1]
    ys, xs = np.where(m); bx0, by0, bx1, by1 = xs.min(), ys.min(), xs.max(), ys.max()
    crop = im.crop((x0 + bx0, y0 + by0, x0 + bx1 + 1, y0 + by1 + 1))
    a = np.asarray(crop)[..., 3] > 40; h = a.shape[0]
    feet = a[int(h * 0.93):]; fx = np.where(feet.any(0))[0]
    return crop, (fx.min() + fx.max()) / 2  # crop, feet centre x inside crop

figs = {k: cut(b) for k, b in BOX.items()}
# one scale for all: the mean standing height of K01-K05 -> HEIGHT
s = HEIGHT / np.mean([figs[k][0].height for k in ['K01', 'K02', 'K03', 'K04', 'K05']])
props, _ = cut(PROPS)
pr = props.resize((round(props.width * s), round(props.height * s)), Image.LANCZOS)
pa = np.asarray(pr)[..., 3] > 40
for k, (crop, fcx) in figs.items():
    c = crop.resize((round(crop.width * s), round(crop.height * s)), Image.LANCZOS)
    canvas = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    canvas.alpha_composite(c, (round(CX[k] - fcx * s), FLOOR - c.height))
    canvas.save(os.path.join(out, f'{k}.png'))
# props: legs on the floor, flask centred at x=1360 (the flask is the right-most object on the table)
cols = np.where(pa[: pa.shape[0] // 3].any(0))[0]; flask_cx = (cols.min() + cols.max()) / 2
P = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0)); P.alpha_composite(pr, (round(1360 - flask_cx), FLOOR - pr.height))
P.save(os.path.join(out, 'PROPS.png'))
print(f'scale {s:.3f}; wrote K01-K06 + PROPS to {out}')
