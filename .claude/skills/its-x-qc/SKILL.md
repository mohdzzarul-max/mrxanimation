---
name: its-x-qc
description: Quality control for IT'S X! animation - character consistency against the model sheet, anatomy, line and colour consistency, frame continuity, timing, and render specs (1920x1080, 24 fps, audio). Use before showing any drawing, animatic or render to the user, and before calling anything approved-ready.
---

# Animation QC

Run BOTH parts. The technical check passing does not mean the art is on model.

## 1. Technical (automatic)
```bash
python3 its-x/tools/qc.py its-x/shots/S01/render.mp4 --expect-seconds 5 --sheet its-x/shots/S01/review/contact.png
python3 its-x/tools/qc.py its-x/shots/S01/frames/        # a folder of frames
```
It FAILS on: resolution ≠ 1920x1080, fps ≠ 24, wrong duration.
It WARNS on: missing or mismatched audio, black frames, dead holds over 12 frames, big frame-to-frame jumps (a pop, a missing in-between, or an intended cut or flash: say which).

## 2. Art review (manual, every key and a sample of in-betweens)
Make side-by-side boards (`its-x-model-lock`), open them, and check:
- **Model**: run the per-drawing checklist in `its-x-model-lock`. Hair silhouette and grey eyes are the first things the client checks.
- **Anatomy**: elbows and knees bend the right way; forearm and upper arm proportional; 4 fingers + thumb; no floating or detached parts; feet contact the ground (no sliding) when visible.
- **Volume**: the head and body do not grow or shrink between drawings (compare head height in pixels across keys, ±3%).
- **Line and colour**: same line weight; the same palette (sample the skin, coat shadow and hair colours: they must not drift); one cel-shadow tone; no colour bleeding.
- **Continuity**: props stay in the same hand; screen direction is consistent; the lab layout matches the background.
- **Timing**: accents on the beat frames from the X-sheet notes; no dead holds; arcs smooth when scrubbing the contact sheet.

## Report format (write to review/QC.md and tell the user)
```
SHOT S01 - QC
Technical: PASS/FAIL (+ warnings, with frame numbers)
Model: K01 ✅ · K02 ❌ hair spikes reversed on the left (B panel 3/4) · ...
Anatomy: ...
Timing: ...
Verdict: READY FOR REVIEW / NEEDS FIXES (list)
```
Be honest: if something is off model, say so plainly. Never present a frame as approved quality when the checklist has an ❌.
