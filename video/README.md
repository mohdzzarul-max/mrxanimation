# EXPERIMENTAL PERFUMERY — PERFUME 101: "PERFUME MAHAL MESTI TAHAN LAMA?!"

60-second 9:16 motion-comic ad (1080×1920, 30 fps, 1,800 frames) built in **Remotion + React + TypeScript**.
Every frame is a pure function of the frame number (no timers / rAF), so renders are deterministic.

## Quick start
```bash
cd video
npm install
npm run studio            # live preview / scrub timeline
npm run render            # final  -> out/Perfume101_final.mp4
npm run render:preview    # half-res preview -> out/Perfume101_preview.mp4
```
In sandboxes without access to remotion.media, `remotion.config.ts` automatically uses a locally installed Chrome Headless Shell.

## Change text, price, branding
| What | Where |
|---|---|
| Price (RM10.90), hook price (RM800), cheap price, CTA, slogans, e-book title, benefits list | `src/config/brand.ts` → `BRAND` |
| Colours & fonts | `src/config/brand.ts` → `C`, `FONT` |
| Dialogue text & timing (drives speech bubbles, SRT, VO slots) | `src/config/script.ts` → `LINES` then `python3 tools/make_srt.py` |
| Scene timing | `src/config/timeline.ts` |
| Official e-book cover | put file in `public/ebook/cover.png`, set `A.ebookCover` in `src/config/assets.ts` |
| Voice-over | record lines from `deliverables/DIALOGUE_SCRIPT.md` into `public/audio/vo/`, set `VO_ENABLED = true` |
| SFX cues / volumes | `src/audio/Soundtrack.tsx` → `SFX` |
| Music | `python3 tools/compose_music.py public/audio/music/perfume101_score.wav` (or replace the WAV) |

Note: the hook headline, the "HARGA ≠ KETAHANAN" card, the factor titles and the claims list are written directly in their scene files (`src/scenes/*.tsx`).

## Structure
```
src/
  Root.tsx                     compositions (Perfume101, RigTest)
  compositions/Perfume101.tsx  6 scenes + audio
  scenes/                      Hook, Myth, Factors, Claims, EbookReveal, FinalCTA
  characters/MrX.tsx           layered cut-out rig: head/torso/arms/sleeves, blink lids, expression swaps, views
  characters/XBot.tsx          living perfume bottle: vector body + official gloves/shoes/X marks, rubber-hose limbs, 8 eye expressions
  components/                  ComicPanel engine, KineticText, SpeechBubble, Backgrounds (paper, halftone, speed lines, bursts, rays),
                               Transition (camera, bar wipe, ink iris, page flip, flash), Props (bottles, price tag, stamp, e-book 3D)
  audio/                       Soundtrack (music + SFX cue sheet), Dialogue (VO slots)
  config/                      timeline, brand, script, assets
  lib/anim.ts                  easing curves, keyframes, springs, deterministic noise/shake/blink/talk
tools/                         asset pipeline (upscale, rig builders, sprite extraction), audio synthesis, SRT, stills
assets-src/                    the four official reference sheets
deliverables/                  SRT subtitles, dialogue/VO script
```
See `ASSET_MANIFEST.md` for every asset's origin and licence.
