# 5-second real-animation test: drawing list and timing (X-sheet)

24 fps output. "1s/2s" = each drawing held 1 or 2 frames. All drawings must match the approved turnaround
(`assets/characters/mrx/source/mrx_turnaround.png`): same head shape with the single tuft, skin-coloured eye openings,
white horn and cheek markings, closed mask with no mouth, slim proportions, black tee, black cargo pants, wristbands,
black-and-white shoes.

**Format:** transparent PNG, full figure, about 1600 px tall (same scale for every drawing). Ground line and feet registration must be
consistent, and the figure placed on the same canvas size for every drawing. Clean line plus flat colour; one shadow tone is fine.
Name the files `T##_<label>.png`.

| # | Time (s) | Frames | Drawing | Type | Notes |
|---|---|---|---|---|---|
| T01 | 0.00–0.50 | 12 (hold) | Ready stance, 3/4 facing screen-right, weight on back foot | KEY | Eyes: confident half-lid |
| T02 | 0.50–0.67 | 4 (2s) | Starts to sink: knees bend, shoulders drop, arms draw back | BREAKDOWN | |
| T03 | 0.67–1.00 | 8 (hold) | Deep anticipation crouch, arms cocked back, head down, eyes narrowed | KEY | Strongest squash |
| T04 | 1.00–1.08 | 2 (1s) | Push-off: legs extending, body stretched forward | BREAKDOWN | On ones |
| T05 | 1.08–1.13 | 1 | **Smear**: body stretched across the jump arc | SMEAR | One frame |
| T06 | 1.13–1.33 | 5 (1s+2s) | Airborne peak: tucked legs, arms forward | KEY | |
| T07 | 1.33–1.42 | 2 | Descending: legs reaching down | BREAKDOWN | |
| T08 | 1.42–1.50 | 2 | Landing contact: one foot down, arms out for balance | KEY | Dust FX starts |
| T09 | 1.50–1.67 | 4 (2s) | Landing squash: knees bent, torso low | BREAKDOWN | |
| T10 | 1.67–2.00 | 8 (2s) | Recover to upright, weight settling | KEY | Overshoot, slightly too tall, then settle |
| T11 | 2.00–2.17 | 4 (2s) | Notices the bottle (off-screen left): head turns, eyes look left | KEY | Eye acting |
| T12 | 2.17–2.33 | 4 (2s) | Reach anticipation: shoulder pulls back, hand closed | BREAKDOWN | |
| T13 | 2.33–2.50 | 4 (2s) | Arm extends to the bottle, **hand open** | KEY | |
| T14 | 2.50–2.67 | 4 (2s) | **Hand closes on the bottle** (grip) | KEY | Bottle in hand from here |
| T15 | 2.67–2.92 | 6 (2s) | Lift breakdown: elbow bends, bottle travels up | BREAKDOWN | |
| T16 | 2.92–3.50 | 14 (hold) | Bottle raised beside his face, toward camera | KEY | Bottle label readable (real product) |
| T17 | 3.50–3.67 | 4 (2s) | Reaction take: eyes widen, shoulders pop up | KEY | Mask-safe surprise |
| T18 | 3.67–3.83 | 4 (2s) | Overshoot: leans back slightly | BREAKDOWN | |
| T19 | 3.83–5.00 | 28 (hold) | Confident final pose: bottle presented, free hand on hip | KEY | One blink (eye layer) during the hold |

**Total: 19 character drawings** (11 keys, 7 breakdowns, 1 smear), plus:

- **Eye layers:** a blink on the T19 head, and wide eyes for T17.
- **FX drawings:** landing dust puff (4 drawings), speed lines (2 drawings), sparkle on the bottle (3 drawings).
- **Real ZSCENTS bottle:** product photo or cut-out, used for the hand-held bottle and the label.

## How these drawings get assembled (what I build)

- **Exposure:** each drawing sits on the frames in the table, at 24 fps. Fast actions are on ones, the rest on twos, and holds as listed.
- **Bottle:** the real bottle is placed into the hand drawings from T14 onward, so the label stays accurate.
- **Motion on top of the drawings:** camera framing on ones, FX, and a small amount of tweened secondary motion during holds (breathing, eye blinks).
  The drawings carry the motion; nothing is slid or rotated as a whole.
- **Sound:** original instrumental music and SFX (whoosh on T05, impact on T08, grab Foley on T14, hit on T16, accent on T19).
- **Output:** MP4 plus a contact sheet of every drawing and its timing, for review.
