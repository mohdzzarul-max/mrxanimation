#!/usr/bin/env python3
"""
Original score + sound design for "ZSCENTS — The Final Chapter".

Everything here is synthesised from scratch with numpy (additive piano,
pads, filtered noise, synthetic reverb). No samples, no third-party music,
so the result is free of copyright claims and can be used commercially.

Outputs (48 kHz stereo WAV) into public/audio/:
    stem-ambience.wav   environment: wind, crickets, birds, room, market, crowd
    stem-music.wav      score: piano, pads, strings, bass, percussion
    stem-sfx.wav        design: UI ticks, rumble, disintegration, swell, impacts
    mix-reference.wav   the three stems summed (for listening / QC)

All three stems share one gain so they sum to about -14 LUFS.
Timing comes from src/config/timeline.json.

    python3 scripts/generate_audio.py
"""
import json
import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public" / "audio"
OUT.mkdir(parents=True, exist_ok=True)
TL = json.loads((ROOT / "src" / "config" / "timeline.json").read_text())
EV = TL["events"]
FPS = TL["fps"]
SC = {s["id"][:3]: s["from"] / FPS for s in TL["scenes"]}  # scene start (s)

SR = 48000
DUR = EV["end"] + 0.5
N = int(DUR * SR)
rng = np.random.default_rng(2024)


def buf():
    return np.zeros((N, 2), dtype=np.float64)


amb, mus, sfx = buf(), buf(), buf()
mus2 = buf()  # score AFTER the silence (scene 9 reveals + rebirth)


# ------------------------------------------------------------------ helpers
def t_axis(n):
    return np.arange(n) / SR


def place(dst, sig, at, gain=1.0, pan=0.0):
    """Add mono/stereo `sig` into `dst` at time `at` (s). pan -1..1."""
    i = int(at * SR)
    if i >= N:
        return
    if sig.ndim == 1:
        l = np.cos((pan + 1) * np.pi / 4)
        r = np.sin((pan + 1) * np.pi / 4)
        sig = np.stack([sig * l, sig * r], 1) * np.sqrt(2)
    if i < 0:
        sig = sig[-i:]
        i = 0
    n = min(len(sig), N - i)
    dst[i:i + n] += sig[:n] * gain


def env_curve(points, n=N):
    """Piecewise-linear automation from [(t, value), ...]."""
    ts = np.array([p[0] for p in points]) * SR
    vs = np.array([p[1] for p in points])
    return np.interp(np.arange(n), ts, vs)


def fft_filter(x, lo=None, hi=None, slope=1.0):
    """Zero-phase band filter in the frequency domain (soft edges)."""
    X = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(x.shape[0], 1 / SR)
    g = np.ones_like(f)
    if lo:
        g *= 1 / (1 + (lo / np.maximum(f, 1e-3)) ** (2 * slope))
    if hi:
        g *= 1 / (1 + (f / hi) ** (2 * slope))
    if x.ndim == 2:
        g = g[:, None]
    return np.fft.irfft(X * g, n=x.shape[0], axis=0)


def noise(n, stereo=True, color="white"):
    shape = (n, 2) if stereo else (n,)
    w = rng.standard_normal(shape)
    if color == "brown":
        w = np.cumsum(w, axis=0)
        w -= fft_filter(w, hi=5)  # remove DC drift
        w /= np.abs(w).max() + 1e-9
    elif color == "pink":
        X = np.fft.rfft(w, axis=0)
        f = np.fft.rfftfreq(n, 1 / SR)
        g = 1 / np.sqrt(np.maximum(f, 20))
        X *= g[:, None] if stereo else g
        w = np.fft.irfft(X, n=n, axis=0)
        w /= np.abs(w).max() + 1e-9
    return w


def smooth_rand(n, rate_hz, seed_scale=1.0):
    """Slow random modulation 0..1."""
    k = max(2, int(n / SR * rate_hz) + 2)
    pts = rng.random(k) * seed_scale
    return np.interp(np.linspace(0, k - 1, n), np.arange(k), pts)


def make_ir(seconds=3.2, damp_hz=5500, predelay=0.018):
    n = int(seconds * SR)
    t = t_axis(n)
    ir = rng.standard_normal((n, 2)) * np.exp(-t * 6.9 / seconds)[:, None]
    ir = fft_filter(ir, lo=120, hi=damp_hz)
    pd = int(predelay * SR)
    ir = np.concatenate([np.zeros((pd, 2)), ir])
    return ir / np.sqrt((ir ** 2).sum(0)).max()


def convolve(x, ir):
    n = x.shape[0] + ir.shape[0]
    nfft = 1 << (n - 1).bit_length()
    X = np.fft.rfft(x, nfft, axis=0)
    H = np.fft.rfft(ir, nfft, axis=0)
    return np.fft.irfft(X * H, nfft, axis=0)[: x.shape[0]]


def hz(note):
    """'A4' / 'C#3' / 'Bb2' -> frequency."""
    names = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    s = names[note[0]]
    rest = note[1:]
    if rest[0] == "#":
        s += 1
        rest = rest[1:]
    elif rest[0] == "b":
        s -= 1
        rest = rest[1:]
    octave = int(rest)
    midi = 12 * (octave + 1) + s
    return 440 * 2 ** ((midi - 69) / 12)


# ------------------------------------------------------------- instruments
def piano(note, dur=4.5, vel=0.6, bright=1.0):
    f0 = hz(note)
    n = int(dur * SR)
    t = t_axis(n)
    out = np.zeros(n)
    B = 0.0004  # inharmonicity
    for k in range(1, 11):
        fk = f0 * k * np.sqrt(1 + B * k * k)
        if fk > 16000:
            break
        amp = (1 / k ** 1.25) * (bright ** (k - 1) if bright < 1 else 1)
        decay = (0.9 + 0.55 * k) * (f0 / 260) ** 0.35
        det = 1 + rng.normal(0, 0.0004)
        out += amp * np.sin(2 * np.pi * fk * det * t + rng.random() * 6) * np.exp(-t * decay)
    # two-stage decay (prompt + aftersound) and soft attack
    out *= 0.65 * np.exp(-t * 2.2) + 0.35
    att = np.minimum(1, t / 0.004)
    rel = np.clip((dur - t) / 0.35, 0, 1)
    hammer = rng.standard_normal(n) * np.exp(-t * 180) * 0.04
    hammer = fft_filter(hammer, lo=800, hi=5000)
    sig = (out * att * rel + hammer) * vel
    return sig * 0.35


def pad(notes, dur, attack=2.0, release=2.5, bright=0.45, detune=0.0025, vol=0.12):
    n = int(dur * SR)
    t = t_axis(n)
    out = np.zeros((n, 2))
    for note in notes:
        f0 = hz(note)
        for side, d in ((0, -detune), (1, detune)):
            for v in (-1, 1):
                ff = f0 * (1 + d * v)
                for k in range(1, 7):
                    if ff * k > 9000:
                        break
                    a = bright ** (k - 1) / k
                    out[:, side] += a * np.sin(2 * np.pi * ff * k * t + rng.random() * 6)
    e = np.minimum(1, t / attack) * np.clip((dur - t) / release, 0, 1)
    e *= 1 + 0.08 * np.sin(2 * np.pi * 0.21 * t)
    return out * e[:, None] * vol / max(1, len(notes))


def strings(notes, dur, vol=0.09):
    """Bowed-string-like: brighter pad with vibrato."""
    n = int(dur * SR)
    t = t_axis(n)
    out = np.zeros((n, 2))
    vib = 1 + 0.0035 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(1, t / 1.5)
    for note in notes:
        f0 = hz(note)
        for side in (0, 1):
            ph = 2 * np.pi * np.cumsum(f0 * vib * (1 + (side - 0.5) * 0.003)) / SR
            for k in range(1, 9):
                if f0 * k > 10000:
                    break
                out[:, side] += (0.62 ** (k - 1)) / k * np.sin(k * ph + rng.random() * 6)
    e = np.minimum(1, t / 1.6) ** 2 * np.clip((dur - t) / 1.8, 0, 1)
    return out * e[:, None] * vol / max(1, len(notes))


def sub_bass(note, dur, vol=0.22):
    n = int(dur * SR)
    t = t_axis(n)
    f = hz(note)
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
    e = np.minimum(1, t / 0.08) * np.clip((dur - t) / 0.6, 0, 1)
    return s * e * vol


def kick(vol=0.5, low=46, high=120, decay=6.0):
    n = int(0.9 * SR)
    t = t_axis(n)
    f = low + (high - low) * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * decay)
    click = fft_filter(rng.standard_normal(n) * np.exp(-t * 400), lo=1500) * 0.08
    return (s + click) * vol


def shaker(vol=0.05):
    n = int(0.09 * SR)
    t = t_axis(n)
    s = fft_filter(rng.standard_normal(n), lo=5000, hi=12000)
    e = np.minimum(1, t / 0.012) * np.exp(-t * 55)
    return s * e * vol


def snap(vol=0.12):
    n = int(0.35 * SR)
    t = t_axis(n)
    s = fft_filter(rng.standard_normal(n), lo=900, hi=6000) * np.exp(-t * 22)
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * 0.4
    return (s + body) * vol


def taiko(vol=0.5):
    n = int(2.0 * SR)
    t = t_axis(n)
    f = 55 + 60 * np.exp(-t * 14)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2)
    skin = fft_filter(rng.standard_normal(n) * np.exp(-t * 40), lo=200, hi=2500) * 0.25
    return (s + skin) * vol


# ======================================================== MUSIC  (D minor)
BEAT = 60 / 72
BAR = 4 * BEAT
PROG = [  # (bass, chord tones) — i  VI  III  VII
    ("D2", ["D3", "F3", "A3"]),
    ("Bb1", ["Bb2", "D3", "F3"]),
    ("F2", ["F3", "A3", "C4"]),
    ("C2", ["C3", "E3", "G3"]),
]
ARP = {  # right-hand arpeggio tones per chord
    0: ["D4", "F4", "A4", "D5"],
    1: ["Bb3", "D4", "F4", "Bb4"],
    2: ["F4", "A4", "C5", "F5"],
    3: ["C4", "E4", "G4", "C5"],
}
MELODY = [  # (beat offset within 4-bar phrase, note)
    (0, "A4"), (2, "F4"), (3, "E4"), (4, "D4"), (6, "F4"),
    (8, "C5"), (10, "A4"), (11, "G4"), (12, "E4"), (14, "G4"),
]

s1, s2, s3, s4, s5, s6, s7, s8, s9, s10 = (SC[f"s{i:02d}"] for i in range(1, 11))

# --- Opening drone (darkness -> father): low D + A, very soft
place(mus, pad(["D2", "A2"], s3 - 0.5, attack=4.0, release=3.0, bright=0.35, vol=0.16), 0.6)

# --- Sparse piano, scenes 1-2
for i, (tt, nt, v) in enumerate([
    (3.2, "A4", .45), (4.9, "F4", .35), (6.5, "D4", .4), (8.4, "E4", .3),
    (10.0, "A4", .45), (11.2, "D5", .35), (12.6, "C5", .32), (13.9, "A4", .3),
    (15.4, "F4", .35), (16.4, "G4", .28),
]):
    place(mus, piano(nt, 5.0, v), tt, pan=-0.15 + 0.1 * (i % 3))
for tt, nt in [(10.0, "D2"), (13.3, "Bb1"), (16.6, "F2")]:
    place(mus, piano(nt, 5.5, 0.35, bright=0.6), tt, pan=-0.3)


def phrase(start, bars, arp="quarter", melody=True, vel=0.32, bass=True, pad_vol=0.11,
           strings_vol=0.0, bass_sub=0.0):
    """Lay out `bars` bars of the progression starting at `start`."""
    for b in range(bars):
        ci = b % 4
        bs, chord = PROG[ci]
        bt = start + b * BAR
        if bass:
            place(mus, piano(bs, BAR + 1.5, vel * 1.1, bright=0.6), bt, pan=-0.25)
        if pad_vol:
            place(mus, pad(chord, BAR + 2.0, attack=1.2, release=2.0, vol=pad_vol), bt - 0.3)
        if strings_vol:
            place(mus, strings([chord[0].replace("3", "4").replace("2", "3")] + chord[1:],
                               BAR + 1.8, vol=strings_vol), bt - 0.2)
        if bass_sub:
            place(mus, sub_bass(bs.replace("1", "2") if bs.endswith("1") else bs, BAR, bass_sub), bt)
        tones = ARP[ci]
        if arp == "quarter":
            for k in range(4):
                place(mus, piano(tones[k], 3.0, vel * 0.7), bt + k * BEAT, pan=0.2)
        elif arp == "eighth":
            for k in range(8):
                place(mus, piano(tones[(k * 3) % 4 if k % 2 else k // 2 % 4], 2.2, vel * 0.55),
                      bt + k * BEAT / 2, pan=0.25 - 0.1 * (k % 2))
        elif arp == "sixteenth":
            for k in range(16):
                nt = tones[k % 4]
                nt = nt[:-1] + str(int(nt[-1]) + 1)
                place(mus, piano(nt, 1.4, vel * 0.32 * (1.15 if k % 4 == 0 else 1)),
                      bt + k * BEAT / 4, pan=0.35 * np.sin(k))
    if melody:
        for rep in range((bars + 3) // 4):
            for off, nt in MELODY:
                beat = rep * 16 + off
                if beat < bars * 4:
                    place(mus, piano(nt, 3.5, vel * 1.15), start + beat * BEAT, pan=0.05)


# --- Scene 3: humble beginning — progression begins, quarter arps
phrase(s3, 3, arp="quarter", melody=False, vel=0.3, pad_vol=0.08)
# --- Scene 4: struggle — eighth arps, heartbeat pulse
p4 = s4
phrase(p4, 3, arp="eighth", melody=True, vel=0.3, pad_vol=0.09, strings_vol=0.05)
for k in range(int((s5 - (s4 + 1.5)) / BEAT)):
    bt = s4 + 1.5 + k * BEAT
    if k % 2 == 0:
        place(mus, kick(0.28, decay=7), bt)
        place(mus, kick(0.14, decay=9), bt + 0.22)
# --- Scene 5: reaching people — tender, quarter arps only
p5 = s5
# (p5 is ~ scene 5 start) keep it soft
phrase(p5, 2, arp="quarter", melody=False, vel=0.28, pad_vol=0.09, strings_vol=0.06)
place(mus, pad(["D3", "F3", "A3"], 4.0, attack=0.8, release=2.5, vol=0.07), p5 + 2 * BAR - 0.3)
# --- Scene 6: growth — lift
p6 = s6
phrase(p6, 3, arp="eighth", melody=False, vel=0.34, pad_vol=0.1, strings_vol=0.07, bass_sub=0.12)
for k in range(int(3 * BAR / BEAT)):
    bt = p6 + k * BEAT
    place(mus, kick(0.34), bt)
    for j in range(2):
        place(mus, shaker(0.045 if j else 0.06), bt + j * BEAT / 2, pan=0.35)
# --- Scene 7: digital breakthrough — emotional peak of growth
p7 = p6 + 3 * BAR
phrase(p7, 3, arp="sixteenth", melody=True, vel=0.38, pad_vol=0.12, strings_vol=0.1, bass_sub=0.16)
for k in range(int(3 * BAR / BEAT)):
    bt = p7 + k * BEAT
    place(mus, kick(0.4), bt)
    if k % 2 == 1:
        place(mus, snap(0.11), bt, pan=0.05)
    for j in range(4):
        place(mus, shaker(0.03 + 0.02 * (j == 2)), bt + j * BEAT / 4, pan=0.4)
place(mus, taiko(0.35), p7)
# --- Scene 8: final collection — percussion out, piano alone, decaying
p8 = p7 + 3 * BAR  # ~ scene 8 start + 1 s
for i, (off, nt, v) in enumerate([
    (0.0, "A4", .42), (1.0, "F4", .36), (2.0, "D4", .34), (3.6, "E4", .3),
    (5.0, "C5", .3), (6.4, "A4", .26), (7.8, "G4", .22), (9.4, "F4", .2),
    (11.6, "E4", .16), (14.0, "D4", .14),
]):
    place(mus, piano(nt, 6.0, v), p8 + off, pan=0.05 * i % 0.3)
for off, nt, v in [(0.0, "D2", .3), (3.6, "Bb1", .26), (7.8, "F2", .2), (11.6, "A1", .16)]:
    place(mus, piano(nt, 6.5, v, bright=0.55), p8 + off, pan=-0.3)
place(mus, pad(["D3", "F3", "A3"], 8.0, attack=0.5, release=6.5, vol=0.09), p8)
# fade the whole score to nothing by "musicGone"
music_env = env_curve([(0, 1), (EV["musicGone"] - 6.0, 1), (EV["musicGone"], 0), (DUR, 0)])

# --- Scene 9 reveals: single low notes in the silence
place(mus2, piano("D2", 7.0, 0.32, bright=0.5), EV["tapiReveal"], pan=-0.1)
place(mus2, piano("A2", 7.0, 0.22, bright=0.5), EV["namaReveal"], pan=0.1)
# "INI PERMULAAN... YANG BARU." — first hint of the major key
place(mus2, piano("D3", 6.0, 0.2, bright=0.6), EV["permulaanReveal"], pan=-0.1)
place(mus2, piano("A3", 6.0, 0.16, bright=0.6), EV["permulaanReveal"] + 0.05, pan=0.1)
place(mus2, piano("F#4", 6.0, 0.2), EV["baruReveal"], pan=0.05)

# --- Scene 10: rebirth — uplifting climax after impact
imp = EV["impact"]
place(mus2, sub_bass("D2", EV["end"] - imp, 0.2), imp)
place(mus2, sub_bass("D1", EV["end"] - imp, 0.12), imp)
RB = [("Bb1", ["Bb2", "D3", "F3", "Bb3"]), ("C2", ["C3", "E3", "G3", "C4"]),
      ("D2", ["D3", "F#3", "A3", "D4"])]
rb_t = imp + 0.4
for i, (bs, chord) in enumerate(RB):
    d = 2 * BAR if i < 2 else EV["end"] - (rb_t + 2 * 2 * BAR) + 1
    t0 = rb_t + i * 2 * BAR
    place(mus2, pad(chord, d + 1.5, attack=1.5, release=3.0, bright=0.5, vol=0.16), t0)
    place(mus2, strings(chord[1:] + [chord[1][:-1] + "5"], d + 1.2, vol=0.11), t0)
    place(mus2, piano(bs, 5.0, 0.4, bright=0.6), t0, pan=-0.2)
    for k in range(8 if i < 2 else 6):
        nt = chord[k % 4]
        nt = nt[:-1] + str(int(nt[-1]) + 2)
        place(mus2, piano(nt, 2.5, 0.22), t0 + k * BEAT / 2 + BEAT, pan=0.3 * np.sin(k))
final_env = env_curve([(0, 1), (EV["fadeOutStart"], 1), (EV["end"], 0), (DUR, 0)])

# ========================================================= AMBIENCE
# Evening wind (scenes 1-3)
w = fft_filter(noise(N, color="pink"), lo=180, hi=1400)
w *= (0.35 + 0.65 * smooth_rand(N, 0.25))[:, None]
place(amb, w * env_curve([(0, 0), (0.8, 0), (3, .09), (s3, .11), (s3 + 2, .03), (s4, 0), (DUR, 0)])[:, None], 0)

# Crickets — evening kampung
def crickets(dur, base=4700):
    n = int(dur * SR)
    t = t_axis(n)
    carrier = np.sin(2 * np.pi * base * t)
    pulse = (np.sin(2 * np.pi * 32 * t) > 0.2).astype(float)
    gate = (np.sin(2 * np.pi * 1.6 * t + rng.random() * 6) > 0.1).astype(float)
    sm = np.convolve(pulse * gate, np.ones(60) / 60, "same")
    return carrier * sm


for base, pan in ((4650, -0.6), (5100, 0.55), (4400, 0.1)):
    c = crickets(s3 + 1, base)
    c *= env_curve([(0, 0), (1.5, 0), (4, .012), (s3 - 1.5, .012), (s3 + 1, 0)], len(c))
    place(amb, c, 0, pan=pan)


def bird(at, pan):
    n = int(0.18 * SR)
    t = t_axis(n)
    f = 3200 + 1600 * np.sin(np.pi * t / 0.18) + 300 * np.sin(2 * np.pi * 40 * t)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.18) ** 2
    place(amb, s * 0.025, at, pan=pan)


for at in np.sort(rng.uniform(s2 + 0.5, s3 + 1, 9)):
    p = rng.uniform(-0.8, 0.8)
    for j in range(rng.integers(1, 4)):
        bird(at + j * 0.22, p)

# Wooden room tone
rt = fft_filter(noise(N, color="brown"), lo=40, hi=400)
place(amb, rt * env_curve([(0, 0), (s3 - 0.5, 0), (s3 + 1, .05), (s4 - 0.5, .05), (s4 + .5, 0), (DUR, 0)])[:, None], 0)
# small wood creaks in the room
for at in (s3 + 2.3, s3 + 6.8):
    n = int(0.5 * SR)
    t = t_axis(n)
    f = 180 + 70 * np.sin(2 * np.pi * 1.3 * t)
    cr = np.sin(2 * np.pi * np.cumsum(f) / SR) * (np.sin(2 * np.pi * 23 * t) > 0) * np.sin(np.pi * t / 0.5)
    place(amb, fft_filter(cr, lo=150, hi=2500) * 0.02, at, pan=0.4)


# Market / crowd walla (scenes 4 + 6)
def walla(dur, voices=14):
    n = int(dur * SR)
    out = np.zeros((n, 2))
    for v in range(voices):
        src = fft_filter(rng.standard_normal(n), lo=rng.uniform(250, 450), hi=rng.uniform(1800, 3200))
        syl = smooth_rand(n, rng.uniform(3.5, 6.5)) ** 2
        phr = (smooth_rand(n, 0.4) > 0.45).astype(float)
        phr = np.convolve(phr, np.ones(4800) / 4800, "same")
        p = rng.uniform(-0.9, 0.9)
        sig = src * syl * phr
        out[:, 0] += sig * np.cos((p + 1) * np.pi / 4)
        out[:, 1] += sig * np.sin((p + 1) * np.pi / 4)
    out = fft_filter(out, hi=2600)
    return out / (np.abs(out).max() + 1e-9)


m4 = walla(s5 - s4 + 1, 10)
m4 *= env_curve([(0, 0), (1.0, .05), (s5 - s4 - 1, .06), (s5 - s4 + 1, 0)], len(m4))[:, None]
place(amb, m4, s4)
hum = np.sin(2 * np.pi * 100 * t_axis(int((s5 - s4) * SR))) * 0.004
place(amb, hum, s4)
for at in np.sort(rng.uniform(s4 + 1, s5 - 1, 7)):  # glass clinks
    n = int(0.6 * SR)
    t = t_axis(n)
    cl = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, d in ((2730, 14), (4410, 20), (6120, 30)))
    place(amb, cl * 0.012, at, pan=rng.uniform(-0.6, 0.6))

# Scene 5: open-air evening, distant soft voices
ev5 = fft_filter(noise(int((s6 - s5 + 1) * SR), color="pink"), lo=200, hi=900)
ev5 *= env_curve([(0, 0), (1, .03), (s6 - s5 - .5, .03), (s6 - s5 + 1, 0)], len(ev5))[:, None]
place(amb, ev5, s5)
w5 = walla(s6 - s5 + 1, 5)
w5 *= env_curve([(0, 0), (1.5, .025), (s6 - s5, .025), (s6 - s5 + 1, 0)], len(w5))[:, None]
place(amb, fft_filter(w5, hi=1200), s5)

m6 = walla(s7 - s6 + 1, 18)
m6 *= env_curve([(0, 0), (0.6, .075), (s7 - s6 - 0.8, .08), (s7 - s6 + 1, 0)], len(m6))[:, None]
place(amb, m6, s6)

# Scene 8: quiet room, a breath of air
q8 = fft_filter(noise(int((s9 - s8 + 3) * SR), color="pink"), lo=100, hi=700)
q8 *= env_curve([(0, 0), (1, .025), (s9 - s8, .02), (s9 - s8 + 3, 0)], len(q8))[:, None]
place(amb, q8, s8)

# ============================================================== SFX
# Livestream UI ticks — timed to the purchase/comment layer animation
# (mirrors src/scenes/S07Live.tsx: notifications every 16 frames from 3.0 s)
for i in range(10):
    at = s7 + 3.0 + i * 16 / FPS
    n = int(0.09 * SR)
    t = t_axis(n)
    f = 1750 - 600 * t / 0.09
    tk = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 60)
    place(sfx, tk * 0.05, at, pan=0.5)
for i in range(6):
    at = s7 + 2.2 + i * 22 / FPS
    n = int(0.12 * SR)
    t = t_axis(n)
    bub = np.sin(2 * np.pi * (600 + 900 * t / 0.12) * t) * np.sin(np.pi * t / 0.12)
    place(sfx, bub * 0.03, at, pan=-0.5)

# Whoosh into scene 6 (light flash)
def whoosh(dur=0.9, rev=False, vol=0.12, lo=300, hi=5000):
    n = int(dur * SR)
    t = t_axis(n)
    s = fft_filter(noise(n, color="pink"), lo=lo, hi=hi)
    e = (t / dur) ** 2 * np.exp(-(t / dur) * 2.5) if not rev else np.sin(np.pi * t / dur) ** 2
    return s * e[:, None] / (np.abs(e).max() + 1e-9) * vol


place(sfx, whoosh(0.8, True, 0.09), s6 - 0.45)
place(sfx, whoosh(1.2, True, 0.06, hi=2500), s8 - 0.6)

# Scene 9: low rumble under the dimming + disintegration
r9 = fft_filter(noise(int(12 * SR), color="brown"), lo=25, hi=110)
r9 *= env_curve([(0, 0), (3, .16), (7.5, .22), (9.5, 0), (12, 0)], len(r9))[:, None]
place(sfx, r9, s9 + 0.5)
# disintegration — dense micro-grains of sand/ash with an air whoosh
d0, d1 = s9 + 4.5, s9 + 8.0
for _ in range(1400):
    at = rng.uniform(d0, d1 + 0.4)
    n = int(rng.uniform(0.008, 0.03) * SR)
    t = t_axis(n)
    gr = np.sin(2 * np.pi * rng.uniform(3000, 9000) * t) * np.hanning(n)
    prog = (at - d0) / (d1 - d0)
    place(sfx, gr * 0.012 * np.sin(np.pi * np.clip(prog, 0, 1)) ** 0.5, at, pan=rng.uniform(-0.9, 0.9))
place(sfx, whoosh(4.0, True, 0.07, lo=500, hi=7000), d0)

# Scene 10: silver light tone
sl = EV["silverLight"]
n = int(4.5 * SR)
t = t_axis(n)
glass = sum(np.sin(2 * np.pi * f * t) / k for k, f in enumerate((1568.0, 2349.3, 3136.0), 1))
glass *= np.minimum(1, t / 1.5) * np.clip((4.5 - t) / 1.5, 0, 1) * 0.02
place(sfx, glass, sl, pan=0.0)

# Reverse swell into the impact
sw_len = imp - (sl + 0.4)
n = int(sw_len * SR)
t = t_axis(n)
hit = np.zeros((int(5 * SR), 2))
hit[: int(0.3 * SR)] = noise(int(0.3 * SR))
for nt in ("D3", "A3", "D4", "F4"):
    p = piano(nt, 3.0, 0.8)
    hit[: len(p)] += np.stack([p, p], 1)
wet = convolve(hit, make_ir(4.5, 7000))
rev = wet[::-1][-n:]
rev = rev / (np.abs(rev).max() + 1e-9)
rise = np.sin(2 * np.pi * np.cumsum(220 + 660 * (t / sw_len) ** 2) / SR) * (t / sw_len) ** 3 * 0.25
swell = (rev * 0.6 + np.stack([rise, rise], 1)) * ((t / sw_len) ** 2)[:, None]
place(sfx, swell * 0.32, imp - sw_len)

# The impact
place(sfx, kick(0.95, low=34, high=95, decay=1.6), imp)
place(sfx, taiko(0.55), imp)
bst = fft_filter(noise(int(1.2 * SR)), lo=60, hi=3500) * np.exp(-t_axis(int(1.2 * SR)) * 5)[:, None]
place(sfx, bst * 0.22, imp)

# Metallic light sweep after the X resolves
for at, vol in ((imp + 1.0, 0.05), (EV["wordmarkReveal"], 0.04)):
    n = int(1.6 * SR)
    t = t_axis(n)
    f = 2500 + 4500 * (t / 1.6)
    s = sum(np.sin(2 * np.pi * np.cumsum(f * r) / SR) / r for r in (1, 1.5, 2.01))
    s *= np.sin(np.pi * t / 1.6) ** 2 * vol
    place(sfx, s, at, pan=0)
    place(sfx, whoosh(1.4, True, 0.03, lo=2000, hi=9000), at)

# Statement hits
for key, v in (("statement1", 0.32), ("statement2", 0.36), ("statement3", 0.44)):
    place(sfx, taiko(v), EV[key])
    place(sfx, kick(v * 0.8, low=40, decay=3), EV[key])
place(sfx, whoosh(1.0, True, 0.03, lo=1500, hi=8000), EV["tagline"] - 0.3)

# ========================================================== MIX / OUTPUT
IR = make_ir(3.4, 6000)
mus = (mus * 0.72 + convolve(mus, IR) * 0.5) * music_env[:, None]
mus2 = (mus2 * 0.72 + convolve(mus2, IR) * 0.5) * final_env[:, None]
mus = mus + mus2
amb = amb * 0.8 + convolve(amb, make_ir(1.6, 5000)) * 0.25
sfx = sfx * 0.8 + convolve(sfx, make_ir(3.0, 8000)) * 0.35
sfx *= final_env[:, None]
amb *= final_env[:, None]


def limiter(x, ceiling=0.84, block=96, look=3, release_blocks=40):
    """Look-ahead peak limiter. Returns the per-sample gain curve."""
    n = x.shape[0] // block * block
    pk = np.abs(x[:n]).max(1).reshape(-1, block).max(1)
    pk = np.concatenate([pk, np.zeros(look)])
    ahead = np.max(np.stack([pk[i:i + len(pk) - look] for i in range(look + 1)]), 0)
    g_t = np.minimum(1, ceiling / np.maximum(ahead, 1e-9))
    g = np.empty_like(g_t)
    cur = 1.0
    rel = 1 - np.exp(-1 / release_blocks)
    for i, v in enumerate(g_t):
        cur = v if v < cur else cur + (v - cur) * rel
        g[i] = cur
    gs = np.repeat(g, block)
    return np.concatenate([gs, np.full(x.shape[0] - n, gs[-1])])


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    pcm = (x * 32767).astype("<i2")
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())


# Hard silence window between the end of the score and the first reveal
sil = np.ones(N)
a, b = int(EV["musicGone"] * SR), int((EV["tapiReveal"] - 0.05) * SR)
sil[a:b] = 0
for x in (amb, sfx):
    x *= sil[:, None]
mus *= sil[:, None]

mix = amb + mus + sfx
peak = np.abs(mix).max()
pre = 0.5 / peak
write_wav(OUT / "_premix.wav", mix * pre)
meas = subprocess.run(
    ["ffmpeg", "-hide_banner", "-nostats", "-i", str(OUT / "_premix.wav"),
     "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
    capture_output=True, text=True).stderr
js = json.loads(meas[meas.rfind("{"):meas.rfind("}") + 1])
lufs = float(js["input_i"])
tp = float(js["input_tp"])
gain_db = -14 - lufs
g = pre * 10 ** (gain_db / 20)
lim_g = limiter(mix * g)[:, None]
print(f"premix {lufs:.1f} LUFS (TP {tp:.1f}) -> gain {gain_db:+.1f} dB, "
      f"limiter max reduction {20 * np.log10(lim_g.min()):.1f} dB")
(OUT / "_premix.wav").unlink()

write_wav(OUT / "stem-ambience.wav", amb * g * lim_g)
write_wav(OUT / "stem-music.wav", mus * g * lim_g)
write_wav(OUT / "stem-sfx.wav", sfx * g * lim_g)
write_wav(OUT / "mix-reference.wav", mix * g * lim_g)
print("wrote", *(p.name for p in sorted(OUT.glob("*.wav"))))
