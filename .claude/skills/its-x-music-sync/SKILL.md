---
name: its-x-music-sync
description: Analyse the IT'S X! song (or any MP3) for beats, accents and sung words, pick shot windows, and build frame-accurate timing and lip-sync sheets at 24 fps. Use before timing any shot to music, choosing which part of the song a shot covers, or doing mouth sync.
---

# Music and lip-sync

Song: `its-x/ITS_X_CLAUDE_STARTER_PACK/00_MUSIC/Track Em Down X.mp3` (126.6 s, ~117.5 BPM, beat ≈ 0.49 s ≈ 12 frames at 24 fps). Lyrics: `05_PRODUCTION_BRIEF/FINAL_LYRICS.txt`.

## Measure, never guess
```bash
python3 its-x/tools/audio_timing.py "its-x/ITS_X_CLAUDE_STARTER_PACK/00_MUSIC/Track Em Down X.mp3" its-x/timing [--start S --end E]
```
Outputs `beats.csv` (time, strength, accent=strong hit), `words.csv` (word start/end) and `TIMING.md` (sung lines; with a window, a frame-numbered cue list).
Transcription mishears words ("Axe" = "X", "blow" = "glow"). Trust the TIMES and fix the words from FINAL_LYRICS.txt.

## Known anchors (measured)
| Song s | Cue |
|---|---|
| 0.0-22 | Intro "It's X!" calls (0.64, 5.16, 9.18, 13.20, 21.16) |
| 28.06 | Verse 1 "There was a scientist working late one night" |
| 35.92 | "One little **drop** (37.40) made the chemicals **glow** (39.46)" |
| 40.38 | "Then a crack in the air put on a freaky show" |
| 44.18 / 48.12 | Chorus "Gotta track 'em down, 'cause it's X!" |
| 57.14 | "The portal blew up in a flash of blue" |

## Picking a shot window
Start the window ON a beat (from beats.csv), so frame 1 is on the grid. Put the shot's main accent on an accented beat or a stressed word. Leave 6-12 frames after the last accent for the settle.

## Syncing action
- The contact or impact frame = the beat frame. Anticipation starts 4-8 frames earlier.
- Visual accents can lead the audio by 1-2 frames (reads as in sync on screen); never lag.
- Write the cues into the X-sheet with `xsheet.py new --timing`. The "notes" column then shows `BEAT!`, `beat` and `"word"` on the right frames.

## Lip-sync (when a character sings or speaks)
Map each word to mouth shapes from sheet F: A (ah), E (eh/ee), I (ih), O (oh), U (oo/w), IDLE (m/b/p closed), GRIT (s/t teeth), SHOUT (accents). Change shape on the vowel onset; hold each for at least 2 frames; close for m/b/p. Mr X has no visible mouth (mask): sync with eye shapes and head accents instead.

## Export with audio
`xsheet.py render ... --audio SONG --start S` cuts the song at S and muxes AAC. For a final, keep 24 fps and check with `qc.py` (audio and video lengths must match).
