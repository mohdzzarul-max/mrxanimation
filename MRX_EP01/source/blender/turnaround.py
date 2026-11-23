"""Render a 4-view turnaround of each character to compare with the reference sheets.
Usage: python3 turnaround.py <MRX|UNCLE|XBOT> <out.png>"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from lib import new_scene, area, camera, plane, mat, world_color, look_at
import characters as C

who, out = sys.argv[-2], sys.argv[-1]
sc = new_scene(res=(400, 560), samples=16)
world_color((0.55, 0.45, 0.40), 0.6)
c = {"MRX": C.build_mrx, "UNCLE": C.build_uncle, "XBOT": C.build_xbot}[who]()
plane("floor", (0, 0, 0), (20, 20), m=mat("floor", (0.75, 0.62, 0.55), rough=0.6))
area("key", (2.0, -3.0, 3.0), (0, 0, 0.7), energy=500, color=(1.0, 0.88, 0.75), size=2.0)
area("fill", (-3, -2, 1.5), (0, 0, 0.7), energy=150, color=(0.75, 0.85, 1.0), size=3.0)
area("rim", (0, 3, 2.5), (0, 0, 0.8), energy=400, color=(1, 0.8, 0.6), size=1.0)
cam, tgt, foc = camera(lens=50)
cam.location = (0, -4.2, 0.85)
tgt.location = (0, 0, 0.62)
paths = []
for i, rz in enumerate((0, 30, 90, 180)):
    c.arm.rotation_euler = (0, 0, math.radians(rz))
    sc.render.filepath = f"/tmp/ta_{who}_{i}.png"
    bpy.ops.render.render(write_still=True)
    paths.append(sc.render.filepath)
os.system(f"convert {' '.join(paths)} +append {out}")
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(os.path.dirname(out), f"{who}_turnaround.blend"))
