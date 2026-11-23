"""Replace the draft head in each user-supplied pose drawing with an approved Mr X rig head.

Body poses come from assets/characters/mrx/poses_draft/src (the user's draft pack); every head pixel in
the output is an approved head-state sprite (assets/characters/mrx/rig/states), placed by its neck pivot,
scaled to the turnaround's head:body proportion and rotated only. No morphing.
Also applies the per-row ground shift so every drawing shares one ground line (y=1760).
  python3 tools/headswap_poses.py [T01 T03 ...]  -> assets/characters/mrx/poses_draft/fixed/T##.png
"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

R = Path(__file__).resolve().parents[1] / "assets/characters/mrx"
P = R / "poses_draft"; OUT = P / "fixed"; OUT.mkdir(exist_ok=True)
cfg = json.loads((P / "headswap.json").read_text())
HPX, HPY = 800, 1200

def shift_for(tid):
    n = int(tid[1:])
    for rng, dy in cfg["ground_shift"].items():
        a, b = [int(x[1:]) for x in rng.split("-")]
        if a <= n <= b: return dy
    return 0

ids = sys.argv[1:] or [k for k in cfg if k.startswith("T")]
for tid in ids:
    c = cfg[tid]
    src = next(P.glob(f"src/{tid}_*.png"))
    im = Image.open(src).convert("RGBA")
    if c.get("state"):
        m = Image.new("L", im.size, 0); d = ImageDraw.Draw(m)
        for cx, cy, rx, ry in c["erase"].get("ell", []): d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=255)
        for box in c["erase"].get("box", []): d.rectangle(box, fill=255)
        a = np.asarray(im).copy(); a[..., 3] = np.where(np.asarray(m) > 0, 0, a[..., 3]); im = Image.fromarray(a)
        head = Image.open(R / f"rig/states/{c['state']}.png").convert("RGBA")
        s = c.get("scale", cfg["head_scale"])
        head = head.resize((int(head.width * s), int(head.height * s)), Image.LANCZOS)
        px, py = HPX * s, HPY * s
        if c.get("rot"): head = head.rotate(-c["rot"], resample=Image.BICUBIC, center=(px, py))
        im.alpha_composite(head, (int(round(c["pivot"][0] - px)), int(round(c["pivot"][1] - py))))
    dy = shift_for(tid)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0)); out.alpha_composite(im, (0, dy))
    out.save(OUT / f"{tid}.png"); print(tid, "shift", dy)
