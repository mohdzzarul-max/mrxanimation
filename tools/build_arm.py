"""Cut Mr X's screen-right arm (his left) from the headless front body, for one controlled arm move.

The arm sits against the torso, whose own lavender rim marks the torso's drawn edge. Per row, the cut
runs just right of that rim: the torso keeps its edge, the arm takes everything outward of it.
The arm's top is extended up under the sleeve by repeating one drawn row (hidden by the sleeve),
so it can rotate a few degrees about the sleeve hem.
  -> rig/body_front_noRarm.png, rig/arm_front_R.png (same canvas as body_front), pivot in rig.json
"""
import json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

R = Path(__file__).resolve().parents[1] / "assets/characters/mrx/rig"
body = np.asarray(Image.open(R / "body_front.png").convert("RGBA")).copy()
H, W = body.shape[:2]
rgb = body[..., :3].astype(float); lum = rgb @ [0.299, 0.587, 0.114]
lav = (lum > 165) & (rgb[..., 2] > rgb[..., 0] + 8) & (body[..., 3] > 0)
Y0, Y1, XIN = 1196, 2010, 0           # arm rows (sleeve hem -> below the fist), a column inside the arm
HEM = [(900, 1214), (1036, 1166)]        # sleeve hem line (arm starts below it)
arm = np.zeros((H, W), bool)
hem_y = lambda x: np.interp(x, [HEM[0][0], HEM[1][0]], [HEM[0][1], HEM[1][1]])
XT = 820                                   # a column inside the torso
skinpx = (rgb[..., 0] > 150) & (rgb[..., 0] > rgb[..., 2] + 40)
light = (lum > 190) & ~skinpx & (body[..., 3] > 0)   # the torso's near-white lavender rim
prev = 880                                 # measured torso-rim position at the top of the arm (row ~1250)
for y in range(Y0, Y1):
    x = XT
    while x < W - 1 and not light[y, x] and not skinpx[y, x]: x += 1
    if light[y, x] and (prev is None or abs(x - prev) < 40):
        while x < W - 1 and light[y, x]: x += 1    # just past the rim: the torso keeps it
        prev = x
    else:
        x = prev if prev is not None else x        # no rim on this row (fist over the pants): carry the line
    arm[y, x:] = body[y, x:, 3] > 0
xs = np.arange(W)[None, :]; ys = np.arange(H)[:, None]
arm &= ys > hem_y(xs) + 2                    # below the sleeve hem only
lab, n = ndimage.label(arm)
sizes = ndimage.sum(arm, lab, range(1, n + 1)); arm = lab == (np.argmax(sizes) + 1)
arm_img = body.copy(); arm_img[..., 3] = np.where(arm, body[..., 3], 0)
# extend the arm's top under the sleeve (repeat a drawn row 12 px below the hem)
src_y = 1232
row = arm_img[src_y].copy()
sleeve_cover = body[..., 3] > 0                     # only where the sleeve/torso will hide it
row_ok = (row[:, 3] > 0) & ~light[src_y]
for y in range(1120, src_y):
    m = row_ok & (arm_img[y, :, 3] < 128) & sleeve_cover[y] & ~arm[y]
    arm_img[y, m] = row[m]
rest = body.copy(); rest[..., 3] = np.where(arm, 0, body[..., 3])
Image.fromarray(arm_img).save(R / "arm_front_R.png")
Image.fromarray(rest).save(R / "body_front_noRarm.png")
meta = json.loads((R / "rig.json").read_text())
meta["arms"] = {"front_R": {"layer": "arm_front_R.png", "body": "body_front_noRarm.png", "pivot": [968, 1190],
                "note": "draw UNDER the body layer (the sleeve covers the arm top); rotate outward only (about -7..+1 deg)"}}
(R / "rig.json").write_text(json.dumps(meta, indent=1))
print("arm px", int(arm.sum()))
