# Episode 01 / Scene 01 — sprite-rig version (approved pipeline)

12 s · 1080×1920 · 24 fps. Every Mr X pixel comes from the approved sheets (the rig layers in `assets/characters/mrx/rig`, plus `sprites_4x/pose_hold_bottle.png`).
GSAP drives all timing. The character is on twos; the camera and graphics are on ones.

Render: `node tools/render_video.js episodes/ep01/scene01_rig/scene01.html episodes/ep01/scene01_rig/out/scene01_rig.mp4 --audio episodes/ep01/scene01/out/scene01_music_sfx.wav`

**Audio: music + SFX only, no voices.** Build it with `python3 mix.py --no-voice` in `episodes/ep01/scene01/`.
X-BOT's call is an off-screen-right alert SFX (two robotic blips at 10.04 s, panned right) followed by the stinger.
Preview: open `scene01.html` in Chrome (loops). Add `?t=11.96` to hold a frame, or `?bg=1` for the empty set.

| Time | Shot | Action | Sound |
|---|---|---|---|
| 0–3.42 | A medium, push-in | Settles, smug look (one lid lowered), confident arm gesture, one blink, dip | music bed |
| 3.42–7.0 | B insert | Bottle pose rises in (cut on action), ZSCENTS super, CLEARANCE! slam, OFFER KALI NI!, sparkles | whoosh on the cut, pop, slam thump, shimmer, pop |
| 7.0–10.1 | C medium | Skeptical look down-left, head tilts, pause, deadpan glance to camera | music |
| 10.1–12.0 | C | X-BOT off-screen right: eyes snap right, jolt, anticipation, swap to 3/4-right head, settle, hold | alert blips (right), stinger, whoosh on the turn; music drops to ~35% |

## Continuity lock (last frame = `out/scene01_final_frame.png`)
- **Camera:** scale 1.07, offset (−26, −4) px about (540, 760). Static from about 10.55 s.
- **Mr X:**
  - Front body with the `34R_open` head (3/4 facing screen-right), gaze screen-right.
  - Head offset (+8, 0) px, tilted +1.5°; body offset (+8, 0) px, leaning 0.8° (rig units, before the 0.6152 character scale).
  - Arms hanging; no bottle in hand.
- **X-BOT:** never shown. He enters from screen-right.
- **Set:** studio back plus counter (`out/bg_plate.png` at the final camera).

## Known gaps (need illustration)
- **Real ZSCENTS bottle:** not supplied. The insert uses the sheet's X bottle and invents no label.
- **Examining the bottle in the medium shot (7–10 s):** needs a front-view bottle-holding arm, so the skeptical beat is played on the eyes and head only.
- **Wide/surprised eyes:** not drawn. The reaction uses a gaze snap, a body jolt and the turn.
- **Turn inbetween drawing (front → 3/4):** not drawn. The turn is a straight sprite swap.
