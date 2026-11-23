# ZSCENTS — CLEARANCE HABIS-HABISAN! (21 s ad)

`ZSCENTS_Clearance_HabisHabisan_21s.mp4`: 1080×1920, 24 fps, 504 frames, 21.000 s, AAC 192 kbps.
Instrumental music and SFX only; no voice, narration or vocal samples.

## Files
| File | What it is |
|---|---|
| `ad.html` | Editable source: X-sheet (`XS`), shots, GSAP timeline for camera/text/FX. Open in Chrome to preview (`?t=10.5` holds a frame) |
| `sound.py` | Original music + frame-synced SFX → `music_sfx.wav` |
| `CONTACT_SHEET.png` | 24 frames from the encoded MP4 across all five scenes |
| `QC_REPORT.md` | Quality-control results |
| `../../../assets/characters/mrx/poses_draft/fixed/` | Every character drawing used (T01–T20 + blink variants) |
| `../../../assets/characters/mrx/poses_draft/headswap.json` + `tools/headswap_poses.py` | How each drawing gets its approved head |

## Render
```bash
python3 episodes/ep01/ad21/sound.py            # run inside episodes/ep01/ad21
node tools/render_video.js episodes/ep01/ad21/ad.html episodes/ep01/ad21/ZSCENTS_Clearance_HabisHabisan_21s.mp4 --audio episodes/ep01/ad21/music_sfx.wav
```

## Dependencies (all already in this environment)
- **Node 22** with **Playwright** (Chromium): frame-accurate capture via `window.seek(t)`.
- **GSAP 3.12.5** (vendored, `rig/vendor/gsap.min.js`): typography, camera and FX timeline.
- **FFmpeg**: H.264 + AAC encode and mux.
- **Python 3.13** with numpy, scipy and Pillow: soundtrack, sprite processing, head swaps, contact sheet.

Remotion and HyperFrames were not used: the existing seek-and-capture pipeline already gives frame-exact output, and adding them would change nothing in the picture.

## Product pipeline
1. `python3 tools/cut_product.py assets/products/source/zscents_golden_duke.jpg assets/products/zscents_bottle.png`
2. `python3 tools/place_product.py`: puts the real bottle into Mr X's hand drawings and writes `assets/characters/mrx/poses_draft/final/`.
3. Re-render the ad. The showcase and end card read `assets/products/zscents_bottle.png` directly.

To feature a different ZSCENTS product, replace the source photo and repeat steps 1–3.
