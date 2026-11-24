---
name: its-x-keyframe-planning
description: Plan IT'S X! shots as key poses, breakdowns and in-betweens with an exposure sheet (X-sheet) timed to the music. Use when breaking a story beat into drawings, writing an animator brief, building or checking an X-sheet, or making a labelled contact sheet for approval.
---

# Keyframe planning and exposure sheets

## Naming
`K01, K02…` keys · `B01a…` breakdowns (between K01 and K02) · `I01a1…` in-betweens · PNG with alpha, 1920x1080 canvas or larger, same canvas size for every drawing in a shot.
Folder per shot: `its-x/shots/<SHOT>/drawings/`, `its-x/shots/<SHOT>/xsheet.csv`, `its-x/shots/<SHOT>/PLAN.md`.

## PLAN.md template
```
# SHOT <id> - <one line>
Music window: <start>-<end> s (from TIMING.md), <frames> frames @24
| Drawing | Frame | Pose / acting | Expression (D) | Eyes (E) | Hands (G) | Model ref |
| K01 | 1 | ... | FOKUS | FOCUS | GRAB | I:T13, B:3/4 FRONT |
Breakdowns needed: B01a (K01→K02, arc of the hand over the flask) ...
In-betweens: K01→B01a on twos, 2 inbetweens, slow-in to B01a ...
```
Always cite a model reference (sheet panel or pose number) for every key.

## Workflow (commands are tested)
```bash
# 1. measure the music for the window
python3 its-x/tools/audio_timing.py "its-x/ITS_X_CLAUDE_STARTER_PACK/00_MUSIC/Track Em Down X.mp3" its-x/timing --start 35.74 --end 40.74
# 2. blank X-sheet with beat and word cues pre-filled in "notes"
python3 its-x/tools/xsheet.py new its-x/shots/S01/xsheet.csv --seconds 5 --timing its-x/timing --start 35.74
# 3. fill "drawing" on the frames where a drawing changes (empty = hold); fill "action"
# 4. validate: every drawing exists, frame 1 exposed, long holds flagged
python3 its-x/tools/xsheet.py check its-x/shots/S01/xsheet.csv --drawings its-x/shots/S01/drawings
# 5. animatic with music
python3 its-x/tools/xsheet.py render its-x/shots/S01/xsheet.csv --drawings its-x/shots/S01/drawings \
  --out its-x/shots/S01/animatic.mp4 --audio "its-x/ITS_X_CLAUDE_STARTER_PACK/00_MUSIC/Track Em Down X.mp3" --start 35.74
```

## Approval contact sheet (before any video)
Show the keys in order, each labelled `K01 · frame 1 · Focus` with its model-ref panel beside it:
```bash
python3 its-x/tools/ref_board.py compare its-x/shots/S01/drawings/K01.png --panels I,D --out its-x/shots/S01/review/K01.png
```
Then STOP and ask for approval. No in-betweens until keys are approved; no video until the animatic is approved.

## Minimum key set for a reaction beat
anticipation · reach · grip · lift · pour (the accent) · notice · react (take extreme) · recover. Add breakdowns on every arc and every take.
