"""Build + render one shot.
  python3 render_shot.py <shot_id> [--preview N] [--frames a:b] [--threads T] [--noblend]
Preview: renders N evenly spaced frames at quarter res into renders/_preview/.
Full: renders the shot's render range into renders/<id>/NNNN.png (local frame index), skipping
frames that already exist (resumable). Saves the editable scene to scenes/<id>.blend."""
import os, sys, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from lib import ROOT

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
ap = argparse.ArgumentParser()
ap.add_argument("sid")
ap.add_argument("--preview", type=int, default=0)
ap.add_argument("--frames", default=None)
ap.add_argument("--threads", type=int, default=0)
ap.add_argument("--noblend", action="store_true")
a = ap.parse_args(argv)

import shots_a
SH = dict(shots_a.SHOTS)
try:
    import shots_b
    SH.update(shots_b.SHOTS)
except ImportError as e:
    if "shots_b" not in str(e):
        raise

ctx = SH[a.sid]()
sc = bpy.context.scene
if a.threads:
    sc.render.threads_mode = "FIXED"
    sc.render.threads = a.threads
if not a.noblend:
    os.makedirs(os.path.join(ROOT, "scenes"), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "scenes", a.sid + ".blend"), compress=True)

r0, r1 = ctx.spec["render"]
if a.preview:
    sc.render.resolution_percentage = 50
    sc.cycles.samples = 6
    out = os.path.join(ROOT, "renders", "_preview", os.environ.get("PV", "v1"))
    os.makedirs(out, exist_ok=True)
    n = a.preview
    frames = sorted(set(int(r0 + (r1 - 1 - r0) * i / max(1, n - 1)) for i in range(n)))
    for lf in frames:
        sc.frame_set(lf + 1)
        sc.render.filepath = os.path.join(out, f"{a.sid}_{lf:04d}.png")
        bpy.ops.render.render(write_still=True)
    sys.exit(0)

out = os.path.join(ROOT, "renders", a.sid)
os.makedirs(out, exist_ok=True)
if a.frames:
    x, y = a.frames.split(":")
    r0, r1 = max(r0, int(x)), min(r1, int(y))
t0 = time.time()
done = 0
for lf in range(r0, r1):
    p = os.path.join(out, f"{lf:04d}.png")
    if os.path.exists(p) and os.path.getsize(p) > 0:
        continue
    sc.frame_set(lf + 1)
    sc.render.filepath = p
    bpy.ops.render.render(write_still=True)
    done += 1
print(f"DONE {a.sid} {done} frames in {time.time() - t0:.0f}s", flush=True)
