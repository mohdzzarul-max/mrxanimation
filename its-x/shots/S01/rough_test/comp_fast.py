#!/usr/bin/env python3
"""2.5D camera comp (same camera keys as comp.json) done with OpenCV affine warps, because headless
Blender EEVEE on this CPU-only machine takes ~22 s/frame. Each layer moves by its depth: for a
camera shift X (scene units) and focal L, a layer at depth d shifts X / (d*36/L) * 1920 px and scales L/50.

  python3 its-x/shots/S01/rough_test/comp_fast.py
"""
import json, os
import numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__)); C = json.load(open(os.path.join(HERE, 'comp.json')))
keys = C['camera']; W, H = 1920, 1080
def cam(f):
    for (f0, x0, y0, l0), (f1, x1, y1, l1) in zip(keys, keys[1:]):
        if f0 <= f <= f1:
            t = (f - f0) / max(1, f1 - f0); t = t * t * (3 - 2 * t)
            return x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, l0 + (l1 - l0) * t
    return keys[-1][1:]
def place(img, d, x, y, L, margin=1.0):
    s = L / keys[0][3] * margin; fw = d * 36 / L
    dx, dy = -x / fw * W, y / fw * W
    M = np.float32([[s, 0, W / 2 - s * W / 2 + dx], [0, s, H / 2 - s * H / 2 + dy]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE if img.shape[2] == 3 else cv2.BORDER_CONSTANT)
bg = cv2.imread(os.path.join(HERE, 'bg_lab.png')).astype(np.float32)
lay = C['layers'][0]; ch = C['character']
yy, xx = np.mgrid[0:H, 0:W]; vig = 1 - 0.35 * np.clip(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2 - 0.35, 0, 1)
for f in range(1, C['frames'] + 1):
    x, y, L = cam(f)
    out = place(bg, lay['depth'], x, y, L, lay['margin'])
    fg = cv2.imread(os.path.join(HERE, ch['frames_dir'], f'{f:04d}.png'), cv2.IMREAD_UNCHANGED).astype(np.float32)
    fg = place(fg, ch['depth'], x, y, L); a = fg[..., 3:4] / 255
    out = fg[..., :3] * a + out * (1 - a)
    if 96 <= f <= 98:                                  # flash on the "glow" hit
        k = [0.45, 0.22, 0.08][f - 96]; out = out * (1 - k) + np.array([255, 215, 240]) * k
    out *= vig[..., None]
    cv2.imwrite(os.path.join(HERE, 'render', f'f_{f:04d}.png'), np.clip(out, 0, 255).astype(np.uint8))
print('rendered', C['frames'], 'frames')
