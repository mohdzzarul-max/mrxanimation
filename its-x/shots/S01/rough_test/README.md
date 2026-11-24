# S01 rough animation test v1

Output: `../OUTPUT/S01_ROUGH_ANIMATION_TEST_v1.mp4` (5 s, 1920x1080, 24 fps, song 35.74-40.74 s)

Rebuild:
```bash
python3 its-x/shots/S01/rough_test/build_rough.py   # 120 fg frames: keys + flow in-betweens + props + violet FX
python3 its-x/shots/S01/rough_test/comp_fast.py     # lab background + 2.5D camera (keys in comp.json) + flash + vignette
ffmpeg -framerate 24 -i its-x/shots/S01/rough_test/render/f_%04d.png -ss 35.74 -t 5 -i "its-x/ITS_X_CLAUDE_STARTER_PACK/00_MUSIC/Track Em Down X.mp3" \
  -map 0:v -map 1:a -c:v libx264 -crf 16 -pix_fmt yuv420p -c:a aac -shortest its-x/shots/S01/OUTPUT/S01_ROUGH_ANIMATION_TEST_v1.mp4
```

What is real and what is a stand-in:
- 6 drawn keys (K01-K06): real drawings.
- In-betweens: AUTOMATIC optical-flow interpolation between keys (not drawn). Fine for small moves;
  double images on big moves (lift f29-37, take f90-96). They are replaced by the drawn breakdowns from BREAKDOWN_BRIEF.md.
- Violet liquid, drop, ripple, bubbles, glow and flash: procedural FX layers (not character art).
- Camera: the same keys as comp.json; comp done in OpenCV (Blender EEVEE took ~22 s/frame on this CPU-only machine).
