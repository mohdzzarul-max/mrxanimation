# MR X — Episode 01: KENA GAME!

3D animated comedy short, Bahasa Melayu Malaysia, 9:16 vertical (1080×1920, 30 fps, H.264 + AAC).
About 2 min 31 s (4,534 frames). The brief targeted 2:15; it runs longer so the dialogue keeps its natural pace and the comic pauses aren't cut.

Everything here is produced from code in this folder: models, rigs, animation, lighting, renders, motion
graphics, music, sound effects, voices and subtitles. Nothing is a slideshow of stills: every shot is a
keyframed 3D scene rendered in Blender's Cycles engine.

## Pipeline

| Stage | Tool | Where |
|---|---|---|
| Character models + rigs | Blender 5.3 (`bpy`), procedural modelling, armatures with rigid-bound parts | `source/blender/characters.py` |
| Textures (mask markings, labels, packaging) | PIL | `source/blender/textures.py` → `textures/` |
| Environments + props | Blender | `source/blender/envs.py` |
| Shot animation (cameras, acting, lighting cues) | Blender keyframes + F-curve noise layers | `source/blender/shots_a.py` (Sc 1–4), `shots_b.py` (Sc 5–9), helpers in `shotkit.py` |
| Edit decision list (timing, dialogue, SFX, FX cues) | Python | `source/timeline.py` |
| Rendering | Cycles CPU + OpenImageDenoise | `source/blender/render_shot.py`, `worker.sh` → `renders/<shot>/` |
| Editable scene files | `.blend` per shot | `scenes/<shot>.blend` |
| Voices | Meta MMS-TTS Malay (`facebook/mms-tts-zlm`) + per-character processing | `source/audio/tts.py` → `voices/` |
| Music + SFX (original, synthesized) | numpy | `source/audio/synth.py` |
| Mix (ducking, loudness −14 LUFS) | numpy + ffmpeg | `source/audio/mix.py` → `audio/` |
| Compositing, grade, typography, VFX, subtitles | PIL/numpy (After Effects-style stage) | `source/post/composite.py` → `renders/_comp/` |
| Final encode | ffmpeg | `source/post/assemble.sh` → `exports/` |
| Subtitles file | SRT | `subtitles/MRX_EP01_ms.srt` |

## Rebuild

```bash
pip install bpy==5.3.0 torch transformers soundfile scipy pillow numpy
python3 source/blender/textures.py
python3 source/audio/tts.py            # voices
python3 source/audio/mix.py            # soundtrack
cd source/blender && ./worker.sh 4 sh01 sh02a ...   # render shots (resumable)
python3 source/post/composite.py       # comp all shots
source/post/assemble.sh                # → exports/MRX_EP01_KENA_GAME.mp4
```

Preview one shot quickly: `python3 render_shot.py sh05d --preview 3`.
To revise a shot, edit its function in `shots_a.py`/`shots_b.py`, delete `renders/<shot>/`, re-render it,
re-comp it (`composite.py <shot>`) and re-run `assemble.sh`. To retime, edit `timeline.py`.

## Honest limitations

- **Hardware:** rendered on 4 CPU cores, no GPU. Cycles runs at 360×640 (early shots at 432×768) with 6–8 samples plus
  denoising, then gets upscaled to 1080×1920 in compositing. Rendering `scenes/*.blend` at 1080×1920 with
  128+ samples on a GPU will give much sharper images, with no other changes needed.
- **Characters** are built procedurally from primitives to match the turnaround sheets in `references/`. The
  silhouettes, colours, mask markings and props follow the sheets, but they are simpler than hand-sculpted production
  models. The rig is FK with rigidly bound parts (vinyl-toy style) plus facial controls (eyelids, gaze, eye
  scale, brows, jaw, moustache); there is no IK or deforming skin.
- **Voices** are synthetic: one Malay TTS model, with each character differentiated by pitch, formant, pace and
  processing. They are not acted voice performances. For release, re-record the lines in `voices/` with
  voice actors (the file names match `source/script_data.py`) and re-run `mix.py`.
- **The reference video** is AI-generated Pixar-style footage. This film follows its lighting language (warm
  orange key against cool blue fill, shallow depth of field, punchy close-ups) but is not at that level of
  rendering fidelity.
