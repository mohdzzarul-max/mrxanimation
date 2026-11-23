# ZSCENTS Clearance — Episode 01 / Scene 01

12 s, vertical 1080×1920, 24 fps. Mr X performs on twos (12 drawings/s) and the camera moves on ones,
the way TV animation of that period was timed.

| File | What it is |
|---|---|
| `out/scene01.mp4` | The scene, with sound |
| `out/scene01_final_frame.png` | The exact last frame: the first frame of Scene 02 must match it |
| `out/bg_plate.png` | The empty studio at the final camera position, for later scenes |
| `out/scene01_mix.wav` | Sound mix (dialogue, X-BOT off-screen right, music bed, SFX) |
| `scene01.html` | The animation: Mr X rig, studio set, timeline (`window.seek(t)`) |
| `tts.py` → `audio/*.wav` | Scratch Malay voice (Meta MMS-TTS Malay) |
| `mix.py` | Places the lines, treats X-BOT's voice, builds the music, writes `lipsync.js` |
| `render.js` | Renders the MP4, final frame and background plate |

## Rebuild

```bash
python3 mix.py          # after changing the dialogue or its timing
node render.js          # → out/
node render.js --stills 0,3.9,8.4,11.99   # quick PNG checks
```

Open `scene01.html` in a browser to watch it loop; add `?t=11.99` to hold a frame or `?bg=1` for the empty set.

## Shots

| Time | Action | Dialogue |
|---|---|---|
| 0–3 s | Medium shot, slow push-in. Mr X holds the bottle at his chest, raises one brow (mask marking) | "Weh! ZSCENTS tengah CLEARANCE!" (0.40–2.52) |
| 3–7 s | Small dip, then lifts the bottle toward camera with overshoot and settle; camera reframes left/up | "Korang kena tengok offer kali ni!" (3.50–5.53) |
| 7–10 s | Brings the bottle down, head tilts, looks at it; blink at 8.35 s, slow wrist turns | — |
| 10–12 s | X-BOT shouts from off-screen right; eyes widen, head snaps to screen-right; hold | "MR X!!" (10.10–10.76, panned right) |

## Continuity lock (end of Scene 01 = start of Scene 02)

- Camera: medium shot, scale 1.065, offset (−24, −6) px about (540, 760). The camera holds still from 10.7 s.
- Mr X: bottle in his right hand (screen-left) at chest height. Head turned to screen-right (3/4), eyes wide, looking screen-right.
  Head tilt +4°. Right arm (screen-right) hanging, with a fist.
- X-BOT: not shown. He enters from screen-right.
- Set: purple-blue studio, arched panel behind Mr X, unlabelled shelf bottles left and right, display counter across the bottom.
- Sound: the music drops to about 35% at the shout, so Scene 02 can bring it back up.

## Open items

- **Product bottle:** no ZSCENTS product image was supplied, so the bottle is a blank placeholder with no label. Drop the real cut-out in `assets/zscents-bottle.png` and re-render (see `assets/README.md`).
- **Voice:** the dialogue is a synthetic scratch track. Replace `audio/mrx_l1.wav`, `audio/mrx_l2.wav` and `audio/xbot_l3.wav` with
  real recordings (same names), then run `python3 mix.py && node render.js`. The lip-sync follows the new audio.
