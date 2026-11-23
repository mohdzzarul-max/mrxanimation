"""Pre-render Mr X head sprites for each eye state (sprite swaps in the browser rig; no morphing).
States are listed in assets/characters/mrx/head_states.json:
  { "<name>": {"view": "front|34|side", "mirror": bool, "eyes": {"L": {...}, "R": {...}}} }
-> assets/characters/mrx/rig/states/<name>.png  (1600x1400 head canvas, neck pivot 800,1200)
"""
import json, sys
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).parent))
from build_eyes import render_head, RIG

R = Path(__file__).resolve().parents[1] / "assets/characters/mrx"
states = json.loads((R / "head_states.json").read_text())
meta = json.loads((RIG / "eyes.json").read_text())
out = RIG / "states"; out.mkdir(exist_ok=True)
only = set(sys.argv[1:])
for name, st in states.items():
    if name.startswith("_") or (only and name not in only): continue
    im = render_head(st["view"], st.get("eyes", {}), meta)
    if st.get("mirror"): im = im.transpose(Image.FLIP_LEFT_RIGHT)
    im.save(out / f"{name}.png", optimize=True)
    print(name)
