---
name: its-x-model-lock
description: Keep IT'S X! characters on model. Use before drawing, reviewing or approving ANY artwork of the scientist (pre-mask) or masked Mr X - keyframes, breakdowns, expressions, turnarounds, thumbnails. Lists the locked design, the master sheets, and the side-by-side check every drawing must pass.
---

# Character model lock

## Master references (absolute; never redesign)
| Character | Master sheet | Supporting |
|---|---|---|
| Scientist (pre-mask) | `its-x/ITS_X_CLAUDE_STARTER_PACK/02_POSE_AND_EXPRESSION_REFERENCES/SCIENTIST_PREMASK_20_POSES.png` ("SCIENTIST (PRE-MASK) - ANIMATION ASSET PACK") | `01_MASTER_CHARACTER_AND_LOGO/CHARACTER_ASSET_SHEET_APPROVED.png` (B, D, F, H, K) |
| Mr X (masked) | `01_MASTER_CHARACTER_AND_LOGO/CHARACTER_ASSET_SHEET_APPROVED.png` sections C, E, G, I, L | `02_.../MR_X_MASKED_20_ACTION_POSES.png`, `MR_X_MASKED_MODULAR_PARTS.png` |
| X logo | `01_MASTER_CHARACTER_AND_LOGO/LOGO_X_ORIGINAL.png` - use the file, never redraw | |

If sheets disagree, the master sheet wins. Example: the origin sheet's hair is neater; the asset pack's messier hair is LOCKED.
Panels of the scientist master are pre-cut in `its-x/reference/scientist/` (`python3 its-x/tools/ref_board.py crops` to regenerate):
P_portrait, A_turnaround, B_head_angles, C_details, D_expressions, E_eye_layers, F_mouth_layers, G_hands, H_props, I_poses.

## Locked traits - scientist
- **Face**: young male, angular jaw, pointed chin, small straight nose, light warm skin. Same proportions every frame.
- **Eyes**: GREY irises, sharp angular upper lid with heavy black line, small highlight. Never blue (blue = Mr X only).
- **Brows**: thick, angular, black.
- **Hair**: black, messy, layered spikes falling over the forehead and sides, volume at the back. Match the A/B panels' silhouette from every angle.
- **Outfit**: white lab coat (open, knee length, chest pocket with pens + ID), black t-shirt, black baggy cargo pants with side pockets, black wristbands on BOTH wrists, black-and-white sneakers.
- **Body**: lean, about 7 heads tall (see A_turnaround). Hands: 4 fingers + thumb, sized as G_hands.
- **Forbidden in pre-mask shots**: mask, blue eyes, powers, X-BOT.

## Locked traits - Mr X
- Black full-face mask, permanently fused, with white angular markings exactly as sheet E; BLUE eyes; same hair silhouette as the scientist; black t-shirt, black cargo pants, wristbands.

## Hard rules
1. Characters are ILLUSTRATED artwork (drawn by an artist, or generated with the master sheet as reference and then corrected). Never build a character from code primitives, SVG/CSS geometry or a procedural rig: that was rejected (see `its-x/QUALITY_CHECK.md`).
2. No warping or puppeting a single still to fake acting. Each key pose is its own drawing.
3. Every new drawing gets a side-by-side board before it is shown as "on model":
   ```bash
   python3 its-x/tools/ref_board.py compare path/to/K01.png --panels B,D,E --out its-x/review/K01_vs_model.png
   ```
   Pick the panels that matter: B for head angle, D for expression, E for eyes, G for hands, A for body.
4. Review the board (open the image) against the checklist below. Write each failure down. Do not call a drawing on model with any ❌.

## Per-drawing checklist
- [ ] Hair silhouette matches the B panel for this head angle (spike count and direction, forehead locks)
- [ ] Eyes grey, upper-lid shape matches E, both eyes at the same height relative to the head angle
- [ ] Brow shape and thickness match C/D
- [ ] Jaw, chin and nose match B at this angle; the head is not too round or too big
- [ ] Coat, t-shirt, cargo pants, both wristbands, shoes as A/C
- [ ] Hands: 4 fingers + thumb, correct size, the grip makes physical sense
- [ ] Arms: elbow bends one way, forearm length matches the upper arm, wrist not broken
- [ ] Line weight and cel shading match the sheet (one hard shadow tone)
