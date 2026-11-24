#!/usr/bin/env python3
"""Model-lock reference boards for the scientist (pre-mask).

  python3 its-x/tools/ref_board.py crops
      cuts the master sheet into labelled panels -> its-x/reference/scientist/<panel>.png
  python3 its-x/tools/ref_board.py compare FRAME.png [--panels B,D,E] [--out OUT.png]
      puts a drawing next to the reference panels, at the same height, for side-by-side review

Master sheet (LOCKED): ITS_X_CLAUDE_STARTER_PACK/02_POSE_AND_EXPRESSION_REFERENCES/SCIENTIST_PREMASK_20_POSES.png
("SCIENTIST (PRE-MASK) - ANIMATION ASSET PACK"). Boxes are in that sheet's 1536x1024 pixels.
"""
import argparse, os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.join(os.path.dirname(__file__), '..')
SHEET = os.path.join(ROOT, 'ITS_X_CLAUDE_STARTER_PACK/02_POSE_AND_EXPRESSION_REFERENCES/SCIENTIST_PREMASK_20_POSES.png')
OUT = os.path.join(ROOT, 'reference/scientist')
S = 1536 / 1400  # boxes were measured on a 1400-wide preview
PANELS = {
    'P_portrait':     (0, 50, 220, 340),
    'A_turnaround':   (225, 55, 690, 340),
    'B_head_angles':  (700, 55, 1030, 340),
    'C_details':      (1035, 55, 1395, 340),
    'D_expressions':  (5, 350, 435, 590),
    'E_eye_layers':   (440, 350, 655, 590),
    'F_mouth_layers': (660, 350, 880, 590),
    'G_hands':        (885, 350, 1100, 590),
    'H_props':        (1105, 350, 1395, 590),
    'I_poses':        (5, 598, 1395, 930),
}

def crops():
    im = Image.open(SHEET).convert('RGB'); os.makedirs(OUT, exist_ok=True)
    for k, b in PANELS.items():
        im.crop(tuple(round(v * S) for v in b)).save(os.path.join(OUT, k + '.png'))
    print('wrote', len(PANELS), 'panels to', os.path.normpath(OUT))

def compare(frame, keys, out):
    if not os.path.isdir(OUT): crops()
    H = 720
    tiles = [('YOUR DRAWING', Image.open(frame).convert('RGB'))]
    for k in keys:
        name = next(n for n in PANELS if n.startswith(k + '_'))
        tiles.append(('REF ' + name, Image.open(os.path.join(OUT, name + '.png')).convert('RGB')))
    tiles = [(l, t.resize((round(t.width * H / t.height), H))) for l, t in tiles]
    W = sum(t.width for _, t in tiles) + 10 * (len(tiles) + 1)
    board = Image.new('RGB', (W, H + 60), (18, 15, 24)); d = ImageDraw.Draw(board); x = 10
    try: font = ImageFont.truetype('Inter-Bold.ttf', 26)
    except Exception: font = ImageFont.load_default()
    for l, t in tiles:
        board.paste(t, (x, 50)); d.text((x, 12), l, fill=(235, 230, 255), font=font); x += t.width + 10
    board.save(out); print('wrote', out)

ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='cmd', required=True)
sub.add_parser('crops')
p = sub.add_parser('compare'); p.add_argument('frame'); p.add_argument('--panels', default='B,D,E'); p.add_argument('--out', default='compare.png')
a = ap.parse_args()
crops() if a.cmd == 'crops' else compare(a.frame, a.panels.split(','), a.out)
