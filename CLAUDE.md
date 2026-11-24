# IT'S X! - production rules (mandatory)

Original 2D supernatural action-cartoon series. Quality target: the energy and polish of high-quality early-2000s western superhero TV animation. **Never copy existing characters, frames, backgrounds or sequences from any show.**

## Where things are
- Starter pack (references, music, lyrics, brief): `its-x/ITS_X_CLAUDE_STARTER_PACK/`
- Pre-cut model-sheet panels: `its-x/reference/scientist/`
- Pipeline tools (tested): `its-x/tools/` - `audio_timing.py`, `xsheet.py`, `ref_board.py`, `qc.py`, `comp_scene.py`
- Measured music timing: `its-x/timing/`
- Shots: `its-x/shots/<SHOT>/` (PLAN.md, drawings/, xsheet.csv, review/, render/)
- Skills: `.claude/skills/its-x-*` (model-lock, 2d-animation, acting, keyframe-planning, music-sync, qc, compositing). **Load the matching skill before the work.**

## Character model is LOCKED
- Scientist master: `SCIENTIST (PRE-MASK) - ANIMATION ASSET PACK` (`02_POSE_AND_EXPRESSION_REFERENCES/SCIENTIST_PREMASK_20_POSES.png`). Grey eyes, the approved face, the approved messy black hairstyle, white lab coat, black t-shirt, black cargo pants, black wristbands, black-and-white sneakers, original proportions, correct hands and anatomy.
- Mr X: the masked sections of `01_MASTER_CHARACTER_AND_LOGO/CHARACTER_ASSET_SHEET_APPROVED.png` plus the masked pose sheets. Black fused mask with white angular markings, BLUE eyes.
- X logo: use `LOGO_X_ORIGINAL.png` as is. Never redraw it or invent a generic X.
- No redesigns. When sheets disagree, the master sheet wins.

## Forbidden (rejected by the client)
- Characters drawn from SVG, CSS or canvas primitives, procedural geometry or code rigs.
- Puppet or cut-out animation, stretched limbs, static heads, warping or moving a single still image to fake acting.
- Reusing the old animatic clips (`04_OLD_ANIMATIC_TESTS_REFERENCE_ONLY`) or the rejected test in `its-x/scientist-test.html` as animation.

## Required method
1. Characters are illustrated artwork: drawn by an artist, or produced with an image tool using the master sheet as reference, then corrected to model.
2. Pose-to-pose: keys → breakdowns → in-betweens, timed on an X-sheet to the measured music. On twos by default, ones for fast action.
3. Every drawing is checked side by side against the model sheet (`ref_board.py compare`) before it is shown as on model.
4. **Approval gates.** Stop and get the user's approval after:
   (a) the key-pose contact sheet,
   (b) breakdowns,
   (c) the animatic with music.
   Only then in-between, composite and render. Never animate a whole scene before the keys are approved.
5. If the available tools cannot produce on-model illustrated frames, SAY SO. Do not substitute geometric or procedural art.

## Technical specs
1920×1080 · 24 fps · H.264 MP4 (yuv420p, CRF ≤ 18) with AAC audio · hand-drawn look: strong outlines, flat colours, one cel-shadow tone · Standard colour transform (no Filmic or AgX).
Every render passes `python3 its-x/tools/qc.py <file> --expect-seconds <n>` plus the manual art review in `its-x-qc`.

## Environment
Runs in the cloud session only (Linux container), not on the user's Windows PC. The environment setup script installs Blender 4.5 LTS (`/opt/blender`, Grease Pencil v3), Krita 5.2 (CLI), Potrace, FFmpeg and the Python image and audio libs. Use `xvfb-run -a` for Blender and Krita. OpenToonz is not available; use Blender Grease Pencil for X-sheet-style scene work.

## Communication
The user writes in Malay and English. Reply in the user's language, short and plain. Do not create or publish anything the user did not ask for. Ask before large or outward-facing actions.
