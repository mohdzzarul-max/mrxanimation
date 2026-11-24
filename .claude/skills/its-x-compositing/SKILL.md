---
name: its-x-compositing
description: 2D/2.5D compositing for IT'S X! in headless Blender - painted background layers with real parallax, drawn character sequences, keyframed camera moves (push-in, pan, shake), glow, and portal or perfume FX, rendered at 1920x1080 24 fps. Use when assembling approved animation with backgrounds, adding camera moves or light effects, or rendering a shot.
---

# 2D / 2.5D compositing (Blender 4.5, headless)

Tool: `its-x/tools/comp_scene.py` (tested). Blender is installed by the environment setup script (`/opt/blender`). It runs without a screen via `xvfb-run`.

## Inputs
- Background split into layers (far wall, mid props, near desk) as PNG with alpha. With only one painted background (e.g. `03_ENVIRONMENT/LAB_BACKGROUND_REFERENCE.png`), use it as the far layer and add the near desk as a separate cut-out layer for parallax.
- Character frames: approved, coloured drawings resolved through the X-sheet into one PNG per output frame (0001.png…), with alpha.

## Render
```bash
xvfb-run -a blender -b -noaudio --python its-x/tools/comp_scene.py -- its-x/shots/S01/comp.json
ffmpeg -framerate 24 -i its-x/shots/S01/render/f_%04d.png -ss 35.74 -i "its-x/ITS_X_CLAUDE_STARTER_PACK/00_MUSIC/Track Em Down X.mp3" \
  -c:v libx264 -crf 16 -pix_fmt yuv420p -c:a aac -shortest its-x/shots/S01/S01.mp4
python3 its-x/tools/qc.py its-x/shots/S01/S01.mp4 --expect-seconds 5
```
Use `"preview": 0.5` in the config for quick tests; set 1.0 for finals. Config fields are documented at the top of comp_scene.py.

## Camera language
- Depth values give parallax for free: near layers (depth 4-8) move more than far ones (25-40).
- Push-in for tension (focal 50→55 mm over 2-3 s, ease in/out). Pan along an action. Shake: 3-6 frames on ones, decaying, on impacts. Never shake on twos.
- Keep the character's eyes in the upper third; leave look-room in the direction of the gaze.

## FX
- Glow: `"glow": {"threshold": 0.85, "size": 7}` (fog glow on the brightest areas). Make FX elements bright (near white in the core) so only they bloom; flat character colours stay below the threshold.
- Perfume or portal FX in violet (#8a4dff core #e2c4ff), Mr X powers in blue. Animate FX as their own drawn or graphic layers (rings, sparks, swirl), timed on ones.
- Light the character with FX by adding a separate, blended colour layer above them. Never repaint the character's base colours.

## Colour fidelity
comp_scene.py uses the Standard view transform and emission-only materials, so cel colours render exactly as drawn. Don't switch to Filmic or AgX.
