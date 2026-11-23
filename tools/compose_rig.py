"""Assemble Mr X from rig layers (headless body + head on the shared neck pivot + eye state).

  figure = assemble(body="front", head="34", mirror_head=True, eyes={...}, head_rot=0)
returns an RGBA image on the body sprite's canvas (sprites_4x scale). The head is placed so its
pivot (800,1200 on the head canvas) lands on the body's neck pivot from rig/rig.json.
mirror_head flips the head about its pivot (3/4-left -> 3/4-right; the design is symmetrical).
head_rot tilts the head around the pivot (degrees, + = clockwise), like a cut-out rig.
"""
import json, sys
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).parent))
from build_eyes import render_head, RIG

RIGMETA = json.loads((RIG / "rig.json").read_text())
EYEMETA = json.loads((RIG / "eyes.json").read_text())
HPX, HPY = RIGMETA["head_pivot"]

def assemble(body="front", head="front", mirror_head=False, eyes=None, head_rot=0.0, head_offset=(0, 0)):
    b = RIGMETA["views"][body]
    body_im = Image.open(RIG / b["body"]).convert("RGBA")
    h = render_head(head, eyes or {}, EYEMETA) if eyes is not None else Image.open(RIG / f"head_{head}.png").convert("RGBA")
    if mirror_head: h = h.transpose(Image.FLIP_LEFT_RIGHT)        # pivot x is the canvas centre, so it stays put
    if head_rot: h = h.rotate(-head_rot, resample=Image.BICUBIC, center=(HPX, HPY))
    px, py = b["body_pivot"]
    out = body_im.copy()
    out.alpha_composite(h, (int(px - HPX + head_offset[0]), int(py - HPY + head_offset[1])))
    return out
