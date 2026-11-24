#!/usr/bin/env python3
"""Technical QC for a rendered shot or a folder of frames.

  python3 its-x/tools/qc.py VIDEO.mp4 [--expect-seconds 5] [--sheet OUT.png]
  python3 its-x/tools/qc.py FRAMES_DIR [--sheet OUT.png]

Checks: 1920x1080, 24 fps, duration, audio present and same length, black/blank frames,
exact duplicate runs (holds) and frame-to-frame jumps that look like pops or missing in-betweens.
Writes a contact sheet (every 6th frame) for the human/visual review. Exit 1 on a hard failure.
"""
import argparse, glob, json, os, subprocess, sys
import numpy as np, cv2

ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('--expect-seconds', type=float)
ap.add_argument('--sheet'); ap.add_argument('--every', type=int, default=6)
a = ap.parse_args(); fails, warns = [], []

if os.path.isdir(a.src):
    files = sorted(glob.glob(os.path.join(a.src, '*.png')) + glob.glob(os.path.join(a.src, '*.jpg')))
    frames = [cv2.imread(f) for f in files]; fps = 24
else:
    info = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', a.src],
                                     capture_output=True, text=True, check=True).stdout)
    v = next((s for s in info['streams'] if s['codec_type'] == 'video'), None)
    au = next((s for s in info['streams'] if s['codec_type'] == 'audio'), None)
    num, den = map(int, v['r_frame_rate'].split('/')); fps = num / den
    if (int(v['width']), int(v['height'])) != (1920, 1080): fails.append(f"resolution {v['width']}x{v['height']} (need 1920x1080)")
    if abs(fps - 24) > 0.01: fails.append(f'fps {fps:.3f} (need 24)')
    vd = float(v.get('duration', info['format']['duration']))
    if a.expect_seconds and abs(vd - a.expect_seconds) > 1 / 24 + 1e-3: fails.append(f'duration {vd:.3f}s (expected {a.expect_seconds}s)')
    if not au: warns.append('no audio stream')
    elif abs(float(au.get('duration', vd)) - vd) > 0.1: warns.append(f"audio {float(au['duration']):.2f}s vs video {vd:.2f}s")
    cap = cv2.VideoCapture(a.src); frames = []
    while True:
        ok, f = cap.read()
        if not ok: break
        frames.append(f)

n = len(frames); print(f'{n} frames @ {fps:g} fps = {n / fps:.3f}s')
small = [cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), (240, 135)).astype(np.float32) for f in frames]
for i, s in enumerate(small, 1):
    if s.mean() < 8 or s.std() < 2: warns.append(f'frame {i}: black/blank')
diffs = [float(np.abs(small[i] - small[i - 1]).mean()) for i in range(1, n)]
holds, run = [], 1
for i, d in enumerate(diffs, 2):
    if d < 0.15: run += 1
    else:
        if run >= 2: holds.append((i - run, run))
        run = 1
if run >= 2: holds.append((n - run + 1, run))
if diffs:
    med = float(np.median([d for d in diffs if d >= 0.15] or [0]))
    for i, d in enumerate(diffs, 2):
        if med and d > max(8 * med, 6): warns.append(f'frame {i}: big jump ({d:.1f} vs median {med:.1f}) - cut, pop or missing in-between?')
long = [h for h in holds if h[1] > 12]
print(f'holds (identical runs): {len(holds)}; longest {max([h[1] for h in holds], default=0)} frames')
for s, l in long: warns.append(f'frames {s}-{s + l - 1}: dead hold of {l} frames (consider a moving hold)')
if a.sheet and n:
    picks = list(range(0, n, a.every)); w, h = 384, 216; cols = 6; rows = (len(picks) + cols - 1) // cols
    sheet = np.full((rows * (h + 24), cols * w, 3), 20, np.uint8)
    for k, i in enumerate(picks):
        r, c = divmod(k, cols); y, x = r * (h + 24), c * w
        sheet[y:y + h, x:x + w] = cv2.resize(frames[i], (w, h))
        cv2.putText(sheet, f'f{i + 1}  {i / fps:.2f}s', (x + 6, y + h + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (230, 230, 240), 1)
    cv2.imwrite(a.sheet, sheet); print('contact sheet:', a.sheet)
for m in fails: print('FAIL', m)
for m in warns: print('WARN', m)
print('RESULT', 'FAIL' if fails else 'PASS (technical only - drawing/model checks are manual, see its-x-qc skill)')
sys.exit(1 if fails else 0)
