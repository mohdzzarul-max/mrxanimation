# ZSCENTS — The Final Chapter

A cinematic brand documentary film (1080×1920, 30 fps, 108 s), built in Remotion.
The story runs from a father's advice to the end of ZSCENTS, and then to the birth of **EXPERIMENTAL PERFUMERY**.

## Deliverables (`out/`)

| File | What |
|---|---|
| `zscents-final-chapter.mp4` | Final master. H.264 High, yuv420p BT.709, CRF 15, AAC 320k, −14 LUFS / −1.5 dBTP |
| `zscents-final-chapter-preview.mp4` | Small 540×960 preview (~6 MB) for sharing |
| `zscents-final-chapter.ms.srt` / `.vtt` | Malay subtitles: narration plus all on-screen title cards |
| `qc-opening.mp4`, `qc-farewell.mp4`, `qc-rebirth.mp4` | Preview sections used for QC |

`out/` is git-ignored. Re-create the files with the commands below.

## Commands

```bash
npm install
npm run audio             # generate the sound stems (git-ignored, reproducible)
npm run dev               # Remotion Studio (live preview / timeline)
npm run prepare-assets    # rebuild derived image layers after replacing an image
npm run audio             # regenerate the original score + sound design (python3 + numpy)
npm run subtitles         # export .srt/.vtt from src/config/script.json
npm run render            # final MP4 -> out/zscents-final-chapter.mp4
npm run render:preview    # small preview from the final MP4
npm run preview:opening   # QC sections (also :farewell, :rebirth)
npm run stills -- 0 600 2750   # QC stills -> out/stills
```

Rendering uses the pre-installed Chromium headless shell (see `remotion.config.ts`). Set `REMOTION_BROWSER` to point it somewhere else.
Rendering never touches the network: fonts, images and audio are all local.

## Story structure (`src/config/timeline.json`)

| # | Scene | Time | Image | Treatment |
|---|---|---|---|---|
| 01 | Nasihat Ayah | 0:00–0:09 | 01 | Exposes out of black, slow push-in, drifting shadow |
| 02 | Termenung | 0:09–0:17 | 02 | Near-still hold, breathing sun, haze |
| 03 | Bilik Kayu | 0:17–0:27 | 03 | Dolly-in, documentary inserts, **RM100** typography |
| 04 | Tapak Pertama | 0:27–0:37 | 04a → 04b | Empty stall, then owner at work, practical-light flicker |
| 05 | Kenalkan Perfume | 0:37–0:45 | 05 | Macro on hands, continuous pull-back to the mosque |
| 06 | Booth Ramai | 0:45–0:54 | 06 | Faster cuts: branding, products, chalkboard, visitors |
| 07 | LIVE | 0:54–1:04 | 07 | Screenshot split into layers; comments and purchases animate in one by one |
| 08 | Koleksi Terakhir | 1:04–1:13 | 08 | Label close-ups, pull-back, colour drains, farewell typography |
| 09 | Kematian ZSCENTS | 1:13–1:27 | 09 logo | Gold dims; emblem disintegrates into ember → ash particles; silence; text |
| 10 | Kelahiran Semula | 1:27–1:48 | 10 logo | "INI PERMULAAN… YANG BARU."; silver light; the same particles regather into the X; exact logo revealed on impact; wordmark; statements; tagline |

`timeline.json` is the single source of truth for timing. The audio generator reads it too.
**After changing the timing, run `npm run audio` again** so the score stays in sync with the picture.

## Replacing things

### Images
1. Put the new file in `public/assets/` under the same name, or change `src`/`w`/`h` in `src/config/assets.ts`.
2. Run `npm run prepare-assets`.
3. If the new photo is framed differently, adjust the `focus` points (in image pixels) inside that scene's file in `src/scenes/`.

**Missing asset — action needed:** the full-resolution **wooden room photo (03)** was not among the uploads.
For now, `public/assets/03-wooden-room.jpg` is a low-resolution stand-in cut from the storyboard sheet, graded as a soft memory.
Drop the original in at that path (and delete `03-wooden-room.STANDIN.txt`), update `w`/`h` in `assets.ts`, then run `npm run prepare-assets && npm run render`.

### Words / captions / father's advice
Everything said on screen lives in **`src/config/script.json`**: narration lines (with frame timings per scene) and all title texts.

The father's lines are a **proposed draft, not a real quote**. To change them, edit the two `father` lines, then run `npm run subtitles` and `npm run render`.

### Voice-over
No recording was supplied, and no synthetic voice was used. Nothing in the film pretends to be the father's voice or the owner's voice.
To add a real voice-over:
1. Record it, then clean it (e.g. `ffmpeg -i raw.wav -af "highpass=f=80,afftdn,loudnorm=I=-16:TP=-2" public/audio/voiceover.wav`).
2. In `src/config/assets.ts`, set `voiceOver: { src: "audio/voiceover.wav", volume: 1 }`.
3. Re-time the `start`/`end` values in `script.json` to the recording. Lower `AUDIO.music.volume` (e.g. to 0.6) if the voice needs more room.

The narration lines in `script.json` double as the proposed VO script.

### Music
All audio is **original**. `scripts/generate_audio.py` synthesises every sound from scratch with numpy (piano, pads, strings, percussion, ambience, UI ticks, rumble, disintegration grains, reverse swell, impacts).
No samples or third-party tracks are used, so the soundtrack is safe for commercial use.

It renders as three stems in `public/audio/`: `stem-ambience.wav`, `stem-music.wav` and `stem-sfx.wav`.
To use licensed music instead, put the file in `public/audio/` and point `AUDIO.music.src` at it. Keep the ambience and SFX stems, or set their volume to 0.
The silence at 1:21.2–1:22.4 comes from the stems, so a replacement track should fade out by `events.musicGone` too.

## Honesty safeguards
- Images 06 and 07 are AI reconstructions, and the film labels them on screen as `VISUAL ILUSTRASI`.
  On 07 the label also says `BUKAN DATA JUALAN SEBENAR`, because the viewer counts, purchase notifications and comments come from the reconstruction and are not real data.
- The film adds no revenue figures, sales numbers or customer quotes of its own.
- Logos are never redrawn.
  - The ZSCENTS emblem is the supplied PNG.
  - The X emblem and the wordmark are pixel crops of the supplied file, screen-blended over black so they look identical to it.
  - The particle effects only *transition* into and out of the real artwork.

## Project layout
```
src/
  Film.tsx               main composition: scene slots, transitions, audio tracks
  Root.tsx               registers "ZscentsFinalChapter"
  config/                timeline.json, script.json, assets.ts (manifest), brand.ts
  components/            Photo (virtual camera), FilmTexture (grain, vignette, leaks),
                         Captions, particles (shared death/rebirth system), fonts, anim
  scenes/                S01 … S10
scripts/                 prepare_assets.py, generate_audio.py, export_subtitles.mjs, stills.mjs
public/assets            original uploads (+ storyboard reference)
public/derived           generated layers (blurred plates, live UI rows, logo splits, grain)
public/audio, fonts      generated stems; bundled OFL fonts (Cormorant Garamond, Cinzel, Inter)
```
