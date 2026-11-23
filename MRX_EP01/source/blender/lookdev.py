"""Look-development validation sheets: turnaround (front / 3-4 / side / back) next to the reference,
plus face close-ups for expressions. Usage: python3 lookdev.py <MRX|UNCLE|XBOT> [lid tests...]"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from lib import ROOT, new_scene, area, camera, plane, mat, world_color, obj_key
import characters as C
import shotkit as K

who = sys.argv[-1] if len(sys.argv) > 1 else "MRX"
OUT = os.path.join(ROOT, "character_models", "lookdev")
os.makedirs(OUT, exist_ok=True)
REF = {"MRX": "MRX_turnaround_ref.png", "UNCLE": "UNCLE_turnaround_ref.png", "XBOT": "XBOT_turnaround_ref.png"}[who]

sc = new_scene(res=(420, 640), samples=24)
sc.cycles.denoising_quality = "HIGH"
world_color((0.62, 0.50, 0.44), 0.25)
c = {"MRX": C.build_mrx, "UNCLE": C.build_uncle, "XBOT": C.build_xbot}[who]()
plane("floor", (0, 0, 0), (20, 20), m=mat("ld_floor", (0.80, 0.66, 0.58), rough=0.7))
plane("bg", (0, 3, 0), (20, 20), m=mat("ld_bg", (0.80, 0.66, 0.58), rough=0.9), rot=(math.pi / 2, 0, 0))
area("key", (1.6, -2.6, 2.6), (0, 0, 0.7), energy=260, color=(1.0, 0.92, 0.84), size=2.2)
area("fill", (-2.6, -1.8, 1.4), (0, 0, 0.7), energy=160, color=(0.85, 0.9, 1.0), size=3.0)
area("rim", (-0.8, 2.4, 2.4), (0, 0, 0.9), energy=320, color=(1.0, 0.95, 0.9), size=1.2)
cam, tgt, foc = camera(lens=50, focus=(0, 0, 0.8), fstop=8)
H = 1.0 if who != "UNCLE" else 1.04


def shot(name, rz, campos, look, frame=1):
    c.arm.rotation_euler = (0, 0, math.radians(rz))
    sc.frame_set(frame)
    cam.location = campos
    tgt.location = look
    foc.location = look
    sc.render.filepath = os.path.join(OUT, f"_{who}_{name}.png")
    bpy.ops.render.render(write_still=True)
    return sc.render.filepath


# expression keys on separate frames
EX = [("neutral", 1), ("angry", 2), ("blink", 3), ("surprised", 4), ("look_left", 5)]
if who in ("MRX", "UNCLE"):
    K.expr(c, 0, "neutral")
    K.expr(c, 1, "angry")
    K.expr(c, 2, "closed")
    K.expr(c, 3, "wide")
    K.expr(c, 4, "neutral")
    K.gaze(c, 3, 0, 0)
    K.gaze(c, 4, 22, 4)
    if who == "UNCLE":
        K.brows(c, 0, 0, 0)
        K.brows(c, 1, -1.0, -1.0, angle=14)
        K.brows(c, 3, 2.5, 2.5)
        K.brows(c, 4, 0, 0)
else:
    K.xeyes(c, 0, 1.0, 1.0, 1.0)
    K.xeyes(c, 1, 1.0, 1.6, 1.0)
    K.xeyes(c, 2, 0.08, 1.0, 1.0)
    K.xeyes(c, 3, 1.3, 0.0, 1.2)
    K.xeyes(c, 4, 1.0, 1.0, 1.0)

full = [shot(n, rz, (0, -2.35, 0.8), (0, 0, 0.66)) for n, rz in (("front", 0), ("q34", 30), ("side", 90), ("back", 180))]
sc.render.resolution_x, sc.render.resolution_y = 420, 420
face = []
for n, fr in EX:
    face.append(shot("face_" + n, 0, (0, -1.05, H), (0, 0, H - 0.03), frame=fr))
face.append(shot("face_q34", 30, (0, -1.05, H), (0, 0, H - 0.03)))
face.append(shot("face_side", 90, (0, -1.05, H), (0, 0, H - 0.03)))
ref = os.path.join(ROOT, "references", REF)
os.system(f"convert {' '.join(full)} +append /tmp/ld_{who}_full.png")
os.system(f"convert {ref} -resize x640 /tmp/ld_{who}_ref.png")
os.system(f"convert /tmp/ld_{who}_ref.png /tmp/ld_{who}_full.png +append /tmp/ld_{who}_row1.png")
os.system(f"convert {' '.join(face)} +append /tmp/ld_{who}_row2.png")
os.system(f"convert /tmp/ld_{who}_row1.png /tmp/ld_{who}_row2.png -background '#d8c2b4' -gravity west -append "
          f"{os.path.join(OUT, who + '_lookdev.png')}")
print("SHEET", os.path.join(OUT, who + "_lookdev.png"))
