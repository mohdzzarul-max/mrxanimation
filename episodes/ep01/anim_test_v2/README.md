# 5-second drawn-animation test (v2)

`mrx_drawn_test_5s.mp4`: 120 frames, 24 fps, 1080×1920, music + SFX only (no voices).
`contact_sheet.png`: every drawing with its type and exposure.

**How it's built**
- **One drawing per frame.** Each frame shows exactly one drawing from `assets/characters/mrx/poses_draft/fixed/`, exposed per `xsheet.json`:
  holds, twos, and ones for the push-off and smear.
- **Drawings:** the bodies are the user's draft pose drawings; every head is an approved rig head (tool: `tools/headswap_poses.py`).
- **Layered on top:** root travel along the jump, camera (low angle → medium, landing shake, push on the bottle), speed lines, landing dust and impact ring, contact shadow.
- **Sound:** `sound.py` writes the original electro-punk breakbeat and SFX, synced to the X-sheet.

Preview: open `test.html` in Chrome (loops). Add `?t=1.45` to hold a frame.

**Known limitations**
- **Bottle:** a draft placeholder, labelled on screen. The real ZSCENTS product has not been supplied.
- **Line quality:** body lines are soft, because the drafts were enlarged ~6× from a small panel. The heads are crisper than the bodies.
- **T17 reaction:** no wide-eye drawing exists, so the take is carried by the pose and FX.
- **T05:** one smear frame shows a small leftover tuft smudge.
- **Crouch framing:** in T03 the back fist touches the left frame edge.
