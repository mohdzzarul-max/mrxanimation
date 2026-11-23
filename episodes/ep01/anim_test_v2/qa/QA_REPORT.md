# QA: 20-pose draft pack vs the approved Mr X turnaround

Evidence:
- `qa_all_poses_vs_turnaround.png`: all 20 poses next to the approved turnaround.
- `headswap_demo_T01_T03_T16.png`: draft vs corrected (approved head) for three poses.

## Verdict: no drawing passes unchanged

All 20 drawings share one consistent draft design. The **head is off model** in every one of them.

| | Approved turnaround | Draft pack |
|---|---|---|
| Head shape | Angular shield, V chin | Round egg |
| Tuft | Short, spiky | Long curled antenna |
| Markings | Two horns rising from the sides + inner flame spikes + **vertical cheek stripes** | Simplified lightning bolts, no cheek stripes |
| Eyes | Large, heavy black upper lid, skin-coloured opening | Smaller, thin lids |
| Outline | Lavender sticker outline round the figure | None |

The **bodies are close to the model**: slim build, black tee, black cargo pants with pockets, black wristbands,
black-and-white shoes, plausible proportions. **The bodies are the usable part.**

### Technical checks

| Check | Result |
|---|---|
| Scale between drawings | ✅ Consistent (shoe widths match within ~10%) |
| Ground line | ❌ Row 1 (T01–T05) at y=1848, rows 2–4 at 1722/1728, manifest says 1760 → **fixed** by a per-row vertical shift |
| Line quality | ⚠️ Soft: the poses were enlarged ~6.3× from a 1536×1024 panel. Acceptable at medium-shot size, soft in close-ups |
| Generic bottle (T14–T20) | ❌ Must be the real ZSCENTS product, and **no product file has been supplied yet** |

## Per-drawing

| # | Body pose | Head | Other | Status |
|---|---|---|---|---|
| T01 ready stance | ✅ | swap → approved 3/4-right | | **Corrected (demo)** |
| T02 sink | ✅ | swap | | correctable |
| T03 deep crouch | ✅ | swap, at a larger scale for the foreshortening | | **Corrected (demo)** |
| T04 push-off | ✅ | swap | | correctable |
| T05 smear | ✅ as a 1-frame smear | swap | | correctable |
| T06 airborne peak | ✅ | swap | | correctable |
| T07 descending | ✅ | swap | | correctable |
| T08 landing contact | ✅ | swap | Impact marks baked in (usable as FX) | correctable |
| T09 landing squash | ✅ | swap | | correctable |
| T10 recovery | ✅ | swap → approved front | Motion arcs baked in | correctable |
| T11 notices bottle | ✅ | swap → front, eyes right | "Notice" marks baked in | correctable |
| T12 reach anticipation | ✅ | swap | | correctable |
| T13 reach, open hand | ✅ | swap | | correctable |
| T14 grip | ✅ | swap | Generic bottle | blocked on the real bottle |
| T15 lift | ✅ | swap | **Diagram arrow baked in, must be erased**; generic bottle | blocked on the real bottle |
| T16 bottle raised | ✅ | swap | Sparkles baked in; generic bottle | **Corrected head (demo)**; bottle blocked |
| T17 surprise | ✅ pose | ❌ **open mouth + goggle eyes (breaks the mask rule)** | Generic bottle | body usable, closed-mask approved head; no drawn "wide eyes" exists |
| T18 overshoot | ✅ pose | ❌ goggle eyes, off model | Generic bottle | body usable with an approved head |
| T19 final pose | ✅ | swap | Generic bottle | blocked on the real bottle |
| T20 close-up CTA | n/a (crop, not full body) | | Not part of the test | not used |

## Proposed correction

Keep the draft **body** drawings and replace every head with an **approved rig head**:
- **Views and states:** front or 3/4, mirrored to face right, using the pre-rendered eye states. This fixes T17/T18 with a closed mask.
- **Placement:** each head is set on the draft neck, scaled to the turnaround's head-to-body ratio and rotated only. No morphing.
- **Ground line:** fixed with a per-row vertical shift.
- **Arrow:** the one baked in T15 is erased.

Tool: `tools/headswap_poses.py`, with per-drawing settings in `assets/characters/mrx/poses_draft/headswap.json`.
