#!/usr/bin/env python3
"""Build the S01 layout guide (1920x1080) and a transparent reference overlay.
Proportions are measured from the master sheet's 3/4 FRONT turnaround figure
(its-x/reference/scientist/A_turnaround.png, figure box x128-232, y28-279; sole at 275).

  python3 its-x/shots/S01/make_layout.py   -> S01_LAYOUT_GUIDE.png, S01_REFERENCE_OVERLAY.png
"""
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REF = os.path.join(HERE, '../../reference/scientist')
W, H = 1920, 1080
FLOOR, T = 1000, 820                 # floor line, character height (hair top -> sole)
TOP = FLOOR - T                      # 180
R = {'hair top': 0.0, 'eye line': 0.10, 'chin': 0.145, 'shoulders': 0.19, 'belt / waist': 0.415,
     'wrists': 0.46, 'fists': 0.55, 'knees': 0.70, 'coat hem': 0.765, 'shoe top': 0.905, 'floor (sole)': 1.0}
Y = {k: round(TOP + v * T) for k, v in R.items()}
HEAD = Y['chin'] - Y['hair top']     # one head incl. hair
X01, X06 = 1040, 880                 # body centre K01..K05, and K06 after the half-step back
TABLE_TOP_FRONT, TABLE_TOP_BACK, TABLE_L = 560, 522, 1160
FLASK_X, FLASK_BASE, FLASK_RIM = 1360, 545, 362
PIP_TIP, PIP_TOP = 350, 222          # pipette held above the flask (K03-K05)

def font(sz, bold=True):
    for f in (['Inter-Bold.ttf', 'Inter Bold'] if bold else ['Inter-Regular.ttf']):
        try: return ImageFont.truetype(f, sz)
        except Exception: pass
    for p in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if os.path.exists(p): return ImageFont.truetype(p, sz)
    return ImageFont.load_default()
F14, F16, F18, F22, F30 = font(14), font(16), font(18), font(22), font(30)

def model_cutout(box, height, tint=None, alpha=110):
    """Cut a figure from a sheet panel, key out the light paper, scale to `height`."""
    im = Image.open(os.path.join(REF, box[0])).convert('RGB').crop(box[1])
    a = np.asarray(im).astype(np.float32)
    lum = a.mean(2); sat = a.max(2) - a.min(2)
    m = np.clip((235 - lum) / 35, 0, 1); m[(sat > 40)] = 1          # keep lines and colour, drop paper
    out = np.dstack([a, m * alpha]).astype(np.uint8)
    if tint is not None: out[..., :3] = (out[..., :3] * 0.35 + np.array(tint) * 0.65).astype(np.uint8)
    img = Image.fromarray(out, 'RGBA')
    return img.resize((round(img.width * height / img.height), height), Image.LANCZOS)

FIG = ('A_turnaround.png', (128, 28, 228, 279))  # 3/4 FRONT, hair top..below sole (sole at y=275 of 251 rows)
fig_h = round(T * (279 - 28) / (275 - 31))         # so hair top (31) and sole (275) land on TOP and FLOOR
fig_off = round((31 - 28) * fig_h / (279 - 28))

def place(canvas, img, cx):
    canvas.alpha_composite(img, (round(cx - img.width / 2), TOP - fig_off))

def dashed(d, p0, p1, col, w=2, dash=12, gap=8):
    x0, y0 = p0; x1, y1 = p1; L = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5; n = int(L // (dash + gap)) + 1
    for i in range(n):
        s, e = i * (dash + gap) / L, min(1, (i * (dash + gap) + dash) / L)
        d.line([(x0 + (x1 - x0) * s, y0 + (y1 - y0) * s), (x0 + (x1 - x0) * e, y0 + (y1 - y0) * e)], fill=col, width=w)

def props(d, col, w=3):
    # table (3/4 view: top surface visible, front apron, legs)
    top = [(TABLE_L + 30, TABLE_TOP_BACK), (1900, TABLE_TOP_BACK), (1920, TABLE_TOP_FRONT), (TABLE_L, TABLE_TOP_FRONT)]
    d.polygon(top, outline=col, width=w)
    d.rectangle([TABLE_L, TABLE_TOP_FRONT, 1920, TABLE_TOP_FRONT + 40], outline=col, width=w)
    for x in (TABLE_L + 20, 1880): d.line([(x, TABLE_TOP_FRONT + 40), (x, FLOOR)], fill=col, width=w)
    d.line([(TABLE_L + 50, TABLE_TOP_BACK), (TABLE_L + 50, TABLE_TOP_FRONT)], fill=col, width=1)
    # flask (Erlenmeyer) standing on the table top
    fx = FLASK_X
    body = [(fx - 22, FLASK_RIM + 8), (fx - 22, FLASK_RIM + 70), (fx - 78, FLASK_BASE - 6), (fx - 70, FLASK_BASE),
            (fx + 70, FLASK_BASE), (fx + 78, FLASK_BASE - 6), (fx + 22, FLASK_RIM + 70), (fx + 22, FLASK_RIM + 8)]
    d.polygon(body, outline=col, width=w)
    d.rectangle([fx - 30, FLASK_RIM, fx + 30, FLASK_RIM + 10], outline=col, width=w)
    d.line([(fx - 50, 480), (fx + 50, 480)], fill=col, width=1)  # liquid surface

def pipette(d, tip, top, col, w=3):
    (tx, ty), (ux, uy) = tip, top
    d.line([(tx, ty), (ux, uy)], fill=col, width=w + 3)
    bx, by = ux + (ux - tx) * 0.22, uy + (uy - ty) * 0.22
    d.ellipse([bx - 13, by - 13, bx + 13, by + 13], outline=col, width=w)

# ---------------- guide ----------------
g = Image.new('RGBA', (W, H), (250, 249, 253, 255)); d = ImageDraw.Draw(g)
# step-back zone + action-safe frame
d.rectangle([X06 - 140, TOP - 30, X01 - 10, FLOOR], fill=(255, 236, 214, 255))
d.text((X06 - 130, FLOOR - 24), 'K06 STEP-BACK ZONE (half-step left)', fill=(190, 110, 40), font=F14)
dashed(d, (67, 38), (W - 67, 38), (170, 170, 190)); dashed(d, (67, H - 38), (W - 67, H - 38), (170, 170, 190))
dashed(d, (67, 38), (67, H - 38), (170, 170, 190)); dashed(d, (W - 67, 38), (W - 67, H - 38), (170, 170, 190))
d.text((74, 44), 'ACTION SAFE 93%', fill=(150, 150, 170), font=F14)
# proportion lines across the character area
for k, y in Y.items():
    col = (60, 60, 80) if k in ('hair top', 'floor (sole)') else (150, 120, 210)
    (d.line if k in ('hair top', 'floor (sole)') else (lambda *a, **kw: dashed(d, *a[0], **{'col': kw['fill'], 'w': 1})))(
        [(560, y), (1150, y)], fill=col, width=3 if k == 'floor (sole)' else 1)
    d.text((566, y - 17), f'{k}  y={y}', fill=col, font=F14)
d.line([(0, FLOOR), (W, FLOOR)], fill=(40, 40, 60), width=4); d.text((80, FLOOR + 8), f'FLOOR LINE y={FLOOR}  (feet touch this line in every key)', fill=(40, 40, 60), font=F16)
# ruler in heads
rx = 556
for i in range(8):
    y0 = TOP + i * HEAD
    if y0 > FLOOR: break
    d.rectangle([rx - 18, y0, rx - 6, min(FLOOR, y0 + HEAD)], fill=(200, 190, 235) if i % 2 == 0 else (232, 226, 250), outline=(120, 100, 180))
    d.text((rx - 16, y0 + HEAD / 2 - 9), f'{i + 1}', fill=(60, 40, 120), font=F14)
d.text((566, TOP - 62), f'1 head = {HEAD}px · height = {T / HEAD:.1f} heads', fill=(110, 90, 170), font=F14)
# reference overlays: K01 position (purple) and K06 position (orange ghost)
place(g, model_cutout(FIG, fig_h, tint=(255, 150, 60), alpha=70), X06)
place(g, model_cutout(FIG, fig_h, alpha=125), X01)
d = ImageDraw.Draw(g)
for x, lab, col in [(X01, 'K01-K05 body centre', (110, 70, 200)), (X06, 'K06 body centre', (200, 110, 40))]:
    dashed(d, (x, TOP - 40), (x, FLOOR), col, 2); d.text((x - 60, TOP - 36), lab, fill=col, font=F14)
# 3/4 head construction at K01 head (facing right: centre line shifted right of middle)
hx, hy, hr = X01 + 14, (Y['hair top'] + Y['chin']) // 2 + 6, HEAD * 0.42
d.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], outline=(110, 70, 200), width=2)
d.arc([hx - hr * 0.45, hy - hr, hx + hr * 0.95, hy + hr], -90, 90, fill=(110, 70, 200), width=2)
d.text((hx - 70, TOP - 64), '3/4 FACING RIGHT →', fill=(110, 70, 200), font=F16)
# props
props(d, (40, 40, 60))
d.text((TABLE_L + 40, TABLE_TOP_FRONT + 10), f'LAB TABLE  top y={TABLE_TOP_BACK}-{TABLE_TOP_FRONT}  (same in all keys)', fill=(40, 40, 60), font=F14)
d.text((1500, 400), f'FLASK  x={FLASK_X}  rim y={FLASK_RIM}  base y={FLASK_BASE}', fill=(40, 40, 60), font=F14)
# pipette positions
pipette(d, (1180, 550), (1262, 542), (120, 120, 140)); d.text((1500, 470), 'pipette K01-K02: lying on the table\nin front of the flask (grey)', fill=(120, 120, 140), font=F14)
pipette(d, (FLASK_X, PIP_TIP), (FLASK_X, PIP_TOP), (130, 60, 230)); d.text((1500, 244), 'pipette K03-K05 (purple): vertical,\ntip just above the flask rim', fill=(130, 60, 230), font=F14)
dashed(d, (FLASK_X, PIP_TIP + 6), (FLASK_X, 478), (150, 80, 255), 2, 6, 6); d.text((FLASK_X + 30, 452), 'K04 drop', fill=(150, 80, 255), font=F14)
pipette(d, (1250, 262), (1205, 150), (200, 110, 40)); d.text((1500, 130), 'pipette K06 (orange): pulled up + back', fill=(200, 110, 40), font=F14)
# right-hand path (arc) and left-hand marks
hands = [('K01', (1222, 492)), ('K02', (1215, 538)), ('K03', (1356, 252)), ('K04', (1356, 248)), ('K05', (1350, 254)), ('K06', (1236, 272))]
pts = [p for _, p in hands]
for a, b in zip(pts, pts[1:]): dashed(d, a, b, (60, 150, 120), 2, 8, 6)
for i, (lab, (x, y)) in enumerate(hands):
    d.ellipse([x - 11, y - 11, x + 11, y + 11], outline=(40, 140, 110), width=3)
    if lab in ('K03', 'K04', 'K05'): continue
    d.text((x - 52, y - 10), lab, fill=(40, 140, 110), font=F16)
d.text((1500, 186), 'green = right-hand path K01→K06\n(K03-K05 grip at the pipette top)', fill=(40, 140, 110), font=F14)
for lab, (x, y) in [('L', (1322, 410)), ('L', (X06 + 170, 370))]:
    d.ellipse([x - 11, y - 11, x + 11, y + 11], outline=(200, 80, 120), width=3)
d.text((1500, 300), 'pink = left hand: K03-K05 holds the flask neck;\nK06 open palm up in front of the chest', fill=(200, 80, 120), font=F14)
# head / eye targets
for lab, (x, y), col in [('K01-K04 look: down at pipette tip', (X01 + 40, Y['eye line']), (110, 70, 200)),
                         ('K06 head pulls back', (X06 + 30, Y['eye line'] + 4), (200, 110, 40))]:
    d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=col)
dashed(d, (X01 + 40, Y['eye line']), (FLASK_X, PIP_TIP), (110, 70, 200), 1, 5, 6)
# legend panel (left)
d.rounded_rectangle([80, 60, 520, 640], 14, fill=(255, 255, 255), outline=(200, 195, 220), width=2)
d.text((100, 74), 'S01 LAYOUT GUIDE', fill=(30, 25, 45), font=F30)
d.text((100, 114), "IT'S X! · Scientist (pre-mask) · 1920×1080 · 24fps", fill=(110, 100, 130), font=F14)
rows = [('K01', 'f1', 'Focus, hand hovers'), ('K02', 'f25', 'Reach + grip (GRAB)'), ('K03', 'f37', 'Lift over flask (L: HOLD)'),
        ('K04', 'f41', '"drop": squeeze, drop'), ('K05', 'f73', 'Notice: ONE brow up'), ('K06', 'f96', '"glow": take, step back')]
for i, (k, f, t) in enumerate(rows):
    y = 146 + i * 28; d.text((100, y), k, fill=(110, 70, 200), font=F18); d.text((152, y), f, fill=(150, 140, 170), font=F18); d.text((204, y), t, fill=(40, 35, 55), font=F18)
notes = ['Character on a transparent layer; no background.', 'Same camera, floor line, table and flask in all 6.',
         'Purple figure = master model (proportion only,', '   not the pose). Orange ghost = K06 position.',
         'Grey eyes · messy black hair (asset pack)', 'Wristbands on BOTH wrists · 4 fingers + thumb']
for i, t in enumerate(notes): d.text((100, 324 + i * 22), t, fill=(70, 65, 90), font=F14)
# model insets: 3/4 FRONT head and full figure from the master sheet
head = Image.open(os.path.join(REF, 'B_head_angles.png')).convert('RGB')
hw = head.width // 4; head = head.crop((hw, 18, 2 * hw, head.height // 2 - 8)).resize((150, 150), Image.LANCZOS)
g.paste(head, (100, 470)); d.text((100, 624), 'REF: head 3/4 FRONT', fill=(110, 100, 130), font=F14)
full = Image.open(os.path.join(REF, 'A_turnaround.png')).convert('RGB').crop((128, 28, 228, 279))
full = full.resize((round(full.width * 150 / full.height), 150), Image.LANCZOS)
g.paste(full, (270, 470)); d.text((270, 624), 'REF: body 3/4 FRONT', fill=(110, 100, 130), font=F14)
g.convert('RGB').save(os.path.join(HERE, 'S01_LAYOUT_GUIDE.png'))

# ---------------- transparent overlay (put it on a layer at 20-40% opacity) ----------------
o = Image.new('RGBA', (W, H), (0, 0, 0, 0))
place(o, model_cutout(FIG, fig_h, alpha=170), X01)
place(o, model_cutout(FIG, fig_h, tint=(255, 150, 60), alpha=90), X06)
od = ImageDraw.Draw(o)
od.line([(0, FLOOR), (W, FLOOR)], fill=(40, 40, 60, 255), width=3)
for k, y in Y.items(): dashed(od, (X06 - 160, y), (X01 + 160, y), (150, 120, 210, 200), 1, 8, 8)
props(od, (40, 40, 60, 220))
pipette(od, (FLASK_X, PIP_TIP), (FLASK_X, PIP_TOP), (130, 60, 230, 220))
o.save(os.path.join(HERE, 'S01_REFERENCE_OVERLAY.png'))
print('wrote S01_LAYOUT_GUIDE.png and S01_REFERENCE_OVERLAY.png in', HERE)
