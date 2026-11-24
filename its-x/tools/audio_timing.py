#!/usr/bin/env python3
"""Measure the music: beats (librosa) and sung words (faster-whisper word timestamps).

  python3 its-x/tools/audio_timing.py SONG.mp3 OUT_DIR [--fps 24] [--start S --end E]

Writes OUT_DIR/beats.csv, OUT_DIR/words.csv and OUT_DIR/TIMING.md.
With --start/--end, TIMING.md also maps each beat and word in that window to a frame number
(frame 1 = the first frame of the shot), ready for an exposure sheet.
"""
import argparse, csv, os
import numpy as np, librosa

ap = argparse.ArgumentParser()
ap.add_argument('song'); ap.add_argument('out')
ap.add_argument('--fps', type=int, default=24)
ap.add_argument('--start', type=float); ap.add_argument('--end', type=float)
ap.add_argument('--model', default='base', help='whisper model size (tiny/base/small)')
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)

y, sr = librosa.load(a.song, sr=22050)
dur = len(y) / sr
tempo, bf = librosa.beat.beat_track(y=y, sr=sr)
beats = librosa.frames_to_time(bf, sr=sr)
onset = librosa.onset.onset_strength(y=y, sr=sr)
strength = onset[np.clip(bf, 0, len(onset) - 1)]
downbeat = strength > np.percentile(strength, 70)  # strong hits, good for accents
with open(os.path.join(a.out, 'beats.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['time_s', 'strength', 'accent'])
    for t, s, d in zip(beats, strength, downbeat): w.writerow([f'{t:.3f}', f'{s:.2f}', int(d)])

from faster_whisper import WhisperModel
y16 = librosa.resample(y, orig_sr=sr, target_sr=16000)
segs, _ = WhisperModel(a.model, device='cpu', compute_type='int8').transcribe(y16, word_timestamps=True, language='en')
words, lines = [], []
for s in segs:
    lines.append((s.start, s.end, s.text.strip()))
    for wd in s.words: words.append((wd.start, wd.end, wd.word.strip()))
with open(os.path.join(a.out, 'words.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['start_s', 'end_s', 'word'])
    for s, e, t in words: w.writerow([f'{s:.2f}', f'{e:.2f}', t])

md = [f'# Music timing: {os.path.basename(a.song)}', '',
      f'- Duration {dur:.2f} s, tempo **{float(np.atleast_1d(tempo)[0]):.1f} BPM**, {len(beats)} beats, beat every ~{np.median(np.diff(beats)):.3f} s.',
      '- Words are from automatic transcription: check spelling against FINAL_LYRICS.txt; the TIMES are what matter.', '',
      '## Sung lines', '', '| start | end | line |', '|---|---|---|']
md += [f'| {s:.2f} | {e:.2f} | {t} |' for s, e, t in lines]
if a.start is not None and a.end is not None:
    fr = lambda t: int(round((t - a.start) * a.fps)) + 1
    md += ['', f'## Shot window {a.start:.2f}-{a.end:.2f} s at {a.fps} fps ({fr(a.end) - 1} frames)', '',
           '| frame | song s | cue |', '|---|---|---|']
    ev = [(t, 'BEAT' + (' (accent)' if d else '')) for t, d in zip(beats, downbeat) if a.start <= t < a.end - 0.5 / a.fps]
    ev += [(s, f'word "{t}"') for s, e, t in words if a.start <= s < a.end - 0.5 / a.fps]
    md += [f'| {fr(t)} | {t:.2f} | {c} |' for t, c in sorted(ev)]
open(os.path.join(a.out, 'TIMING.md'), 'w').write('\n'.join(md) + '\n')
print('wrote', a.out)
