# Mr X — animation asset audit (Phase 1)

Source of truth: `source/mrx_turnaround.png` (1774×887) and `source/mrx_character_sheet.png` (1536×1024).
Every sprite in `sprites/` is a crop of that approved artwork. Nothing is redrawn or generated from code geometry.

- **Cut:** each cut follows Mr X's own lavender sticker outline where it is closed (the turnaround figures).
  On the sheet panels the cut drops the purple panel colour instead.
- **Upscale:** `sprites_4x/` is the same art enlarged 4× with a line-art upscaler (Real-ESRGAN x4plus anime 6B).
  The sheets are small, so this keeps the ink lines crisp at 1080×1920 without changing the design.

Tools: `tools/extract_sprites.py` (crop boxes in `crops.json`), `tools/upscale_sprites.py`.
`ASSET_SHEET.png` shows every sprite with its source and upscaled sizes.

## 1. Extracted from approved art

| Asset | Source | Native px | Status | Notes |
|---|---|---|---|---|
| `body_front` | Turnaround DEPAN | 335×764 | ✅ Ready | Full body. Used in still 1. |
| `body_34_left` | Turnaround 3/4 DEPAN | 320×774 | ✅ Ready | Faces screen-left. **Mirrored for screen-right** (the design is symmetrical). Used in still 3. |
| `body_side_left` | Turnaround SISI | 250×764 | ✅ Ready | Faces screen-left. Mirror for screen-right. |
| `body_back` | Turnaround BELAKANG | 317×764 | ✅ Ready | |
| `pose_hold_bottle` | Sheet action pose | 251×343 | ✅ Ready (bust only) | 3/4 bust holding the **sheet's X bottle**. Flat cut at the chest (panel edge), which must sit behind a foreground object. Used in still 2. |
| `head_normal` | Expression NORMAL | 117×133 | ⚠️ Small | About 470 px tall after upscale. Fine for medium shots, soft in close-ups. |
| `head_skeptikal` | Expression SKEPTIKAL | 121×133 | ⚠️ Small | Same as above. |
| `head_marah`, `head_bengang` | MARAH / BENGANG | ~125×137 | ⚠️ Small, effects baked in | The anger mark and the steam puff are part of the drawing. |
| `head_fikir` | FIKIR | 115×138 | ⚠️ Small, hand baked in | Hand on chin is part of the drawing. |
| `head_godam` | GODAM | 126×136 | ⚠️ Small | Sunglasses version. |
| `head_senyum` | SENYUM | 122×133 | ❌ Conflicts with mask rule | Shows teeth through the mask. |
| `head_terkejut` | TERKEJUT | 110×134 | ❌ Conflicts with mask rule | Open mouth. |
| `head_gelak` | GELAK | 115×143 | ❌ Conflicts with mask rule | Open laughing mouth. |
| `bust_arms_crossed` | Sheet hero bust | 370×545 | ⚠️ Needs cleanup | Sheet title lettering touches it at the top left. |
| `pose_punch` | Sheet punch close-up | 412×304 | ⚠️ Needs cleanup | Panel background is fused with the art. |
| `pose_run`, `pose_crouch` | Sheet action poses | ~270×335 | ⚠️ Needs cleanup | Dust and speed lines are baked in. |

## 2. Not in the approved art: new illustration needed

The sheets show the character but are not split into animation layers. These cannot be cut out,
and per the brief they must not be faked with code geometry:

| # | Asset needed | Why | Spec |
|---|---|---|---|
| 1 | **Headless body**: front, 3/4-left, side-left | A head-angle swap needs a body with no head drawn on it. The neck and collar behind the chin were never drawn. | Same scale as the turnaround, neck stub up to the jaw line, transparent PNG |
| 2 | **Separate heads**: front, 3/4, side, drawn at body scale | The heads on the bodies can be cut off, but the turn needs them as matched layers with one shared neck pivot. | One PNG per view, pivot at the base of the neck, ≥1000 px wide |
| 3 | **Eye layers** for front and 3/4 | Blinks and eye movement. The eyes are baked into the heads, and the only closed-eye drawing (GELAK) also has a mouth. | Per eye: open, half-lid, closed, wide-surprise. Iris as its own layer with the lids above it. |
| 4 | **Mask-safe surprise and smile expressions** | TERKEJUT, SENYUM and GELAK show a mouth. | Same poses with the mask closed: emotion carried by eyes and brows only. |
| 5 | **Separate arms**: upper arm, forearm, wristband, for front and 3/4 | A controlled arm move. The shirt behind the arms is not drawn on the sheets. | Joints overlap at shoulder, elbow and wrist. Torso includes the shirt behind the arms. |
| 6 | **Hand set** | Only fists (turnaround) and one grip (3/4 bust) exist. | Relaxed fist, point, open palm, bottle grip (front), bottle grip (3/4) |
| 7 | **Front / medium bottle-holding pose** | Only the 3/4 bust version exists. | Arm raised with the bottle at chest height, front and 3/4 |
| 8 | **Reaction pose** | Body reaction to X-BOT's shout. | 3/4 facing screen-right, shoulders up, eyes wide, no mouth |
| 9 | **Real ZSCENTS bottle** | No product photo or cut-out has been supplied. | Transparent PNG of the real bottle, ≥1500 px tall, front-on, label legible |
| 10 | Higher-resolution masters (optional) | The sheet art is 100–770 px. Upscaling helps but has limits for close-ups. | The original high-resolution files of the sheets, if they exist |

Assets 1–3 are the minimum for the Phase 4 test: idle, eye movement, one arm move and a head turn by sprite swap.
Without them the only option would be moving whole-body images, which the brief rules out.

Drop new art into `assets/characters/mrx/source/` (or straight into `sprites/` as transparent PNGs)
and it plugs into `rig/stage.html`.

## 3. Pipeline (reusable for Scenes 02–04)

- `tools/extract_sprites.py`: cuts sprites from the sheets (crop boxes in `crops.json`).
- `tools/upscale_sprites.py`: 4× line-art upscale.
- `tools/export_studio.js`: exports the studio set as `studio_back.png` plus `studio_counter.png`, a transparent foreground layer.
- `rig/stage.html` + `tools/render_stills.js`: composite sprites from a shot JSON into a 1080×1920 PNG.
  Phase 4 adds GSAP timing and sprite swaps on top of this stage.
- `episodes/ep01/approval/*.json|png`: the three approval stills.
