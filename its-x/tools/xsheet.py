#!/usr/bin/env python3
"""Exposure sheet (X-sheet) tools.

Format: CSV with columns frame,drawing,action,notes. frame starts at 1. "drawing" is a file name
in the drawings folder (e.g. K03.png, B03a.png); an empty cell HOLDS the previous drawing.
Name drawings K## (key), B## (breakdown), I## (in-between) so the sheet reads like a real one.

  python3 its-x/tools/xsheet.py new OUT.csv --seconds 5 [--fps 24] [--timing TIMING_DIR --start S]
      blank sheet; beat/word cues from audio_timing.py are written into "notes"
  python3 its-x/tools/xsheet.py check SHEET.csv --drawings DIR
      every referenced drawing exists, frame 1 has a drawing, holds longer than 12 frames flagged
  python3 its-x/tools/xsheet.py render SHEET.csv --drawings DIR --out OUT.mp4 [--audio A --start S] [--fps 24]
      lays the drawings out per the sheet at 1920x1080 (letterboxed, never stretched) and muxes audio
"""
import argparse, csv, os, subprocess, sys, tempfile, shutil

def load(p):
    with open(p) as f: return list(csv.DictReader(f))

def cmd_new(a):
    n = round(a.seconds * a.fps); notes = {}
    if a.timing:
        for row in csv.DictReader(open(os.path.join(a.timing, 'beats.csv'))):
            t = float(row['time_s']); fr = round((t - a.start) * a.fps) + 1
            if 1 <= fr <= n: notes.setdefault(fr, []).append('BEAT!' if row['accent'] == '1' else 'beat')
        for row in csv.DictReader(open(os.path.join(a.timing, 'words.csv'))):
            t = float(row['start_s']); fr = round((t - a.start) * a.fps) + 1
            if 1 <= fr <= n: notes.setdefault(fr, []).append(f'"{row["word"]}"')
    with open(a.out, 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['frame', 'drawing', 'action', 'notes'])
        for i in range(1, n + 1): w.writerow([i, '', '', ' '.join(notes.get(i, []))])
    print(f'wrote {a.out}: {n} frames')

def resolve(rows):
    cur, out = None, []
    for r in rows:
        if r['drawing'].strip(): cur = r['drawing'].strip()
        out.append(cur)
    return out

def cmd_check(a):
    rows = load(a.sheet); seq = resolve(rows); bad = 0
    if not rows or not rows[0]['drawing'].strip(): print('ERROR frame 1 has no drawing'); bad += 1
    for d in sorted({s for s in seq if s}):
        if not os.path.exists(os.path.join(a.drawings, d)): print('ERROR missing drawing', d); bad += 1
    run, prev = 0, None
    for i, s in enumerate(seq, 1):
        run = run + 1 if s == prev else 1; prev = s
        if run == 13: print(f'WARN long hold: {s} held past frame {i} (moving holds keep it alive)')
    keys = sum(1 for r in rows if r['drawing'].strip())
    print(f'{len(rows)} frames, {keys} exposures, {len(set(seq) - {None})} unique drawings, errors={bad}')
    sys.exit(1 if bad else 0)

def cmd_render(a):
    seq = resolve(load(a.sheet)); tmp = tempfile.mkdtemp()
    try:
        for i, d in enumerate(seq, 1):
            os.symlink(os.path.abspath(os.path.join(a.drawings, d)), os.path.join(tmp, f'{i:05d}.png'))
        vf = 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x0b0818,format=yuv420p'
        cmd = ['ffmpeg', '-v', 'error', '-y', '-framerate', str(a.fps), '-i', os.path.join(tmp, '%05d.png')]
        if a.audio: cmd += ['-ss', str(a.start or 0), '-i', a.audio]
        cmd += ['-vf', vf, '-c:v', 'libx264', '-crf', '16', '-r', str(a.fps)]
        if a.audio: cmd += ['-c:a', 'aac', '-b:a', '192k', '-shortest']
        subprocess.run(cmd + ['-movflags', '+faststart', a.out], check=True)
        print('wrote', a.out, f'{len(seq)} frames')
    finally: shutil.rmtree(tmp)

ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='cmd', required=True)
p = sub.add_parser('new'); p.add_argument('out'); p.add_argument('--seconds', type=float, required=True)
p.add_argument('--fps', type=int, default=24); p.add_argument('--timing'); p.add_argument('--start', type=float, default=0)
p = sub.add_parser('check'); p.add_argument('sheet'); p.add_argument('--drawings', required=True)
p = sub.add_parser('render'); p.add_argument('sheet'); p.add_argument('--drawings', required=True); p.add_argument('--out', required=True)
p.add_argument('--audio'); p.add_argument('--start', type=float); p.add_argument('--fps', type=int, default=24)
a = ap.parse_args(); {'new': cmd_new, 'check': cmd_check, 'render': cmd_render}[a.cmd](a)
