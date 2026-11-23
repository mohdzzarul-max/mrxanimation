# ZSCENTS Clearance — Episode 01 / Scene 01 (rebuild v2)

12 s, vertical 1080×1920, 24 fps. Mr X is animated on twos (12 drawings per second); the camera and
motion graphics move on ones. Style: angular early-2000s TV action-cartoon construction, bold even outlines,
flat fills with one hard shadow tone, lavender rim light.

## Character rules (checked against the turnaround with `scene01.html?sheet=1`)

- Full black mask. **No mouth is ever drawn**, so there is no lip-sync. Dialogue plays over the eye acting and body acting.
- Skin-coloured eye openings, blue eyes under a heavy slanted upper lid, two thick white horns along the sides of the head,
  an inner flame spike above each eye, a cheek stripe under each eye, and a single blade-shaped tuft on top.
- The head is drawn in separate views: front, 3/4-right, and a shut-eye inbetween for the turn. Hands are separate drawings
  (fist, point, grip) swapped per pose.

## Shots

| Time | Shot | Action | Dialogue |
|---|---|---|---|
| 0.00–3.42 | A, medium, push-in | Settles in, cocks one brow (smug), then a snappy point at the bottle with follow-through. One blink at 2.6 s. Anticipation dip, then lifts the bottle toward camera | "Weh! ZSCENTS tengah CLEARANCE!" (0.40–2.52) |
| 3.42–7.00 | B, bottle close-up (cut on action) | Bottle rises into frame with an overshoot. ZSCENTS super drops in, CLEARANCE! banner slams, OFFER KALI NI! pops. Glint, sparkles, slow ray spin | "Korang kena tengok offer kali ni!" (3.50–5.53, over the insert) |
| 7.00–10.10 | C, medium | Brings the bottle down, head tilts, skeptical look (one eye squinted, one brow up), wrist turn, then a deadpan glance to camera and a pause | — |
| 10.10–12.0 | C | X-BOT off-screen right: eyes snap wide, anticipation, shut-eye inbetween, head turns to 3/4-right with overshoot, then holds | "MR X!!" (10.10–10.76, panned right) |

## Continuity lock (last frame = `out/scene01_final_frame.png`; Scene 02 starts here)

- **Camera:** medium shot, scale 1.07, offset (−26, +4) px about (540, 760). Static from 10.5 s.
- **Mr X:**
  - Body shifted 8 px to screen-right, leaning 1.6°.
  - Head in the 3/4-right view, tilted +4°, eyes wide (openness 1.3), gaze screen-right.
  - Bottle in his right hand (screen-left) at chest height, rotated 1°.
  - Free arm hanging, with a fist.
- **X-BOT:** never shown. He enters from screen-right.
- **Set:** purple-blue studio, arched panel, unlabelled shelf bottles left and right, display counter across the bottom (`out/bg_plate.png`).
- **Sound:** the music drops to about 35% at the shout, so Scene 02 can bring it back up.

## Files

| File | What it is |
|---|---|
| `out/scene01.mp4` | The scene, with sound |
| `out/scene01_final_frame.png` | The exact last frame |
| `out/bg_plate.png` | The empty set at the final camera position |
| `out/scene01_mix.wav` | Sound mix |
| `scene01.html` | Character, set, close-up and timeline (`window.seek(t)`); `?sheet=1` model sheet, `?t=` still, `?bg=1` empty set |
| `tts.py` → `audio/*.wav` | Scratch Malay voice (Meta MMS-TTS Malay) |
| `mix.py` | Dialogue placement, X-BOT voice treatment, music bed, SFX |
| `render.js` | Renders the MP4, final frame and background plate; `--stills 0,4.5,11.99` for checks |
| `assets/fonts/Bangers.woff2` | Display font for the supers (SIL Open Font License) |

Rebuild with `python3 mix.py && node render.js`.

## Open items

- **Real product:** no ZSCENTS product photo has been supplied. The bottle is the design from the Mr X character sheet
  (black glass, gold collar, white X), with no label text invented. "ZSCENTS" appears only as on-screen ad lettering.
  To use the real product, drop a transparent cut-out at `assets/zscents-bottle.png`. It replaces the drawn bottle in
  every shot, including the close-up. Then re-render.
- **Voice:** the dialogue is a synthetic scratch track. Replace the three files in `audio/` (same names) with real takes
  and re-run `python3 mix.py && node render.js`.
