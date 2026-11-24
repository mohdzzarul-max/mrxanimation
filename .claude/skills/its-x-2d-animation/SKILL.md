---
name: its-x-2d-animation
description: Traditional 2D animation method for IT'S X! - pose-to-pose with drawn keys, breakdowns and in-betweens, timing on twos/ones, spacing charts, arcs, squash and stretch, anticipation, follow-through and overlap, in an energetic early-2000s TV action-cartoon style. Use when planning or directing any character animation, or turning approved drawings into a moving shot.
---

# Traditional 2D animation (IT'S X!)

## Pipeline (each step needs approval before the next)
1. **Plan**: thumbnails and beat list from the music (`its-x-music-sync`) and story (`its-x-keyframe-planning`).
2. **Keys**: illustrated key poses, each checked with `its-x-model-lock`. **STOP for approval** (contact sheet).
3. **Breakdowns**: the drawing that decides HOW you get between two keys (arc, overlap, the "favour"). STOP for approval.
4. **In-betweens**: spaced per the chart on the key.
5. **X-sheet timing**: `its-x/tools/xsheet.py` → animatic → review with music.
6. **Clean-up / colour**: same line weight, one cel-shadow tone, palette from the sheet.
7. **Composite and render** (`its-x-compositing`), then **QC** (`its-x-qc`).

Never skip to the full scene before the key drawings are approved.

## Timing rules (24 fps)
- Default **on twos** (each drawing held 2 frames) for acting. Use **ones** for fast action, takes, impacts, and any fast pan where twos would strobe.
- Snappy style: fast into a pose (2-4 frames), then a **moving hold** of 6-12 frames (tiny drift, blink, breath, hair settle), never a dead hold over 12 frames. `xsheet.py check` and `qc.py` both flag long holds.
- A **take** (surprise): anticipation squash (2-4 fr) → extreme stretch (2 fr) → overshoot pose (2 fr) → settle (4-8 fr on twos).
- Accents land ON the beat frame from the timing sheet; the anticipation starts 4-8 frames before it.

## Spacing and arcs
- Write a spacing chart on each key: slow-out/slow-in = drawings bunched near the keys. Fast snap = 1-2 in-betweens.
- Heads, hands and hair tips travel on ARCS, never straight lines. Draw the arc on the breakdown.
- Squash and stretch on hair, coat and faces for takes. Volume stays constant; the skull never squashes.

## Overlap and follow-through (this cast)
- Hair locks and the coat tails trail 2-4 frames behind the body and overshoot when it stops.
- Sleeves and wristbands lag the forearm by 1-2 frames on fast moves.
- Pipette or bottle liquid sloshes after the hand stops.

## Style energy (early-2000s action cartoon; originals only)
- Strong, readable silhouettes. Exaggerated extremes on takes. Graphic speed lines and smears (one smear frame) on very fast moves.
- Glow FX in the effect colour (violet for perfume or portal, blue for Mr X powers), added in compositing, not painted into the character.
- Do not copy frames, characters, sequences or backgrounds from any existing show.

## What NOT to do (rejected)
- Rigid puppet or cut-out motion, stretching limbs, rotating a still head, image warping, procedural characters.
