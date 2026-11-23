# Asset manifest — PERFUME 101 motion comic

## Official references (uploaded, source of truth) — `assets-src/`
| File | Contents | Used for |
|---|---|---|
| `ref_mrx_turnaround.png` | Mr X front / ¾ / side / back | Mr X cut-out rig (front) + ¾ / side / back sprites |
| `ref_combined_sheet.png` | Brand sheet: Mr X pose, 6 expressions, X-BOT, logo | Thumb-chin pose, EXPERIMENTAL PERFUMERY wordmark |
| `ref_xbot_hero.png` | X-BOT thumbs-up hero (RGBA) | X-BOT silhouette/proportions, gloves, sneakers, brush-X marks |
| `ref_xbot_sheet.png` | X-BOT expressions, turnaround, poses, layer assets | Glove sprites (point, point-up, open palm), eye-expression designs |
| `ref_mrx_poses.png` | Mr X official expression poses (thumbs-up wink, shocked, angry, love, thinking) | Full-body expression poses (`tools/extract_mrx_poses.py`) |

All references were upscaled 4× with Real-ESRGAN x4plus anime 6B (BSD-3, `tools/models/`, `tools/upscale.py`) before cutting, so characters stay sharp at 1080×1920.

## Prepared character assets — `public/characters/`
| Path | Source | Notes |
|---|---|---|
| `mrx/head.png, body.png, armL.png, armR.png, sleeveL.png, sleeveR.png` | front turnaround | Cut-out rig. Pivots, eye sockets, head circle in `mrx/rig.json` (`tools/build_mrx_rig.py`) |
| `mrx/eyeMask.png` + `rig.json.eyeClip` | front turnaround | Blink lids (vector clip) |
| `mrx/mrx_34.png, mrx_side.png, mrx_back.png` | turnaround | Turn / travel sprites |
| `mrx/poses/{gembira,terkejut,marah,malu,fikir}.png` + `poses.json` | ref_mrx_poses.png | Full-body expression poses, auto-scaled so the head matches the rig head (replaced the old low-res cropped heads) |
| `mrx/poses/thumb_chin.png` | combined sheet main pose | End-card pose |
| `xbot/shoeL.png, shoeR.png, handFist.png, handThumb.png` | X-BOT hero | Official sneakers & gloves |
| `xbot/xbot_hand_0…5.png` | X-BOT sheet "Hands" layer assets | 0 = point, 4 = point-up, 5 = open (others spare) |
| `xbot/markFace.png, markCap.png` | X-BOT hero | Official brush-X marks |
| X-BOT bottle, cap, gold neck, eyes | **vector** in `src/characters/XBot.tsx` | Traced from the hero render (same silhouette, chamfers, gold rims, sticker outline). Eye shapes follow the official expression sheet |
| Mr X shirt X emblem | `markFace.png` scaled | Matches combined-sheet front view (X on chest) |

## Brand — `public/brand/`
| `experimental_wordmark.png` | combined sheet header | White wordmark on alpha |

## MISSING official assets (temporary, editable fallbacks)
| Asset | Status | Fallback |
|---|---|---|
| **E-book cover** | **Not supplied** | `EbookCover` in `src/components/Props.tsx` (brand type + official characters only). Drop the real cover at `public/ebook/cover.png` and set `A.ebookCover = staticFile('ebook/cover.png')` in `src/config/assets.ts` |
| E-book inner pages | Not supplied | Not shown (no pages invented) |
| Voice recordings | Not produced (no commercially licensed Malay TTS available in this environment) | Timed VO slots + `deliverables/DIALOGUE_SCRIPT.md`; on-screen speech bubbles carry every line |

## Audio — `public/audio/`
| Path | Origin | Licence |
|---|---|---|
| `music/perfume101_score.wav` | Original procedural score, `tools/compose_music.py` (120 BPM) | Owned — commercial use OK |
| `sfx/*.wav` (paper_rip, record_scratch, page_flip, bot_chirp_1-3, servo, ka_ching, stamp, marker, tick, boing, rumble, spray, whip) | Synthesized, `tools/synth_sfx.py` | Owned — commercial use OK |
| `sfx/*.mp3` | Pixabay sound effects (bundled with the media-use skill) | Pixabay Content License — commercial use OK, no attribution required (`sfx/PIXABAY_CREDITS.md`) |

## Fonts — `public/fonts/` (SIL Open Font License)
Montserrat (variable), Bangers, Permanent Marker.

## Textures — `public/textures/`
`paper_dark.jpg`, `paper_cream.jpg`, `grain.png` — procedural, `tools/make_textures.py`.
