"""Original instrumental music + SFX for the 5 s drawn-animation test (no voices).
Electro-punk breakbeat, 140 bpm, synced to the X-sheet: whoosh on the push-off/smear (1.0 s),
impact on landing (1.42 s), grab Foley (2.50 s), hit on the bottle raise (2.92 s),
reaction sting (3.50 s), final accent (3.83 s). -> sound.wav (48 kHz stereo)"""
import numpy as np, scipy.io.wavfile as w
from scipy.signal import butter, lfilter
SR, DUR = 48000, 5.0; N = int(SR * DUR); t = np.arange(N) / SR; rng = np.random.default_rng(3)
L = np.zeros((N, 2))
def bp(a, lo, hi): b, c = butter(2, [lo / (SR / 2), min(.99, hi / (SR / 2))], "band"); return lfilter(b, c, a)
def lp(a, hz): b, c = butter(2, hz / (SR / 2)); return lfilter(b, c, a)
def hp(a, hz): b, c = butter(2, hz / (SR / 2), "high"); return lfilter(b, c, a)
def put(a, at, g=1, pan=0):
    i = int(at * SR); a = a[:max(0, N - i)]; th = (pan + 1) * np.pi / 4
    L[i:i + len(a), 0] += a * g * np.cos(th); L[i:i + len(a), 1] += a * g * np.sin(th)
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
beat = 60 / 140; s16 = beat / 4
def kick(): x = np.arange(int(.25 * SR)) / SR; return np.sin(2 * np.pi * (48 + 140 * np.exp(-x * 35)) * x) * np.exp(-x * 11)
def snare(): x = np.arange(int(.2 * SR)) / SR; return hp(rng.standard_normal(len(x)), 1800) * np.exp(-x * 20) * .6 + np.sin(2 * np.pi * 190 * x) * np.exp(-x * 30) * .4
def hat(): x = np.arange(int(.05 * SR)) / SR; return hp(rng.standard_normal(len(x)), 8000) * np.exp(-x * 90)
# music starts building at 0.6 s (anticipation), full groove from the landing (1.42 s)
start = 1.42
pat_k = [0, 6, 10]; pat_s = [4, 12]
for bar in range(4):
    for st in range(16):
        at = start + (bar * 16 + st) * s16
        if at >= DUR - .05: break
        if st in pat_k: put(kick(), at, .9)
        if st in pat_s: put(snare(), at, .55, .1)
        put(hat(), at, .18 if st % 2 else .28, -.3)
# bass: E minor punk riff, distorted saw
riff = [40, 40, 52, 40, 43, 40, 47, 45]
for i in range(32):
    at = start + i * 2 * s16
    if at >= DUR - .1: break
    x = np.arange(int(2 * s16 * SR * .9)) / SR; f = hz(riff[i % 8])
    saw = 2 * ((x * f) % 1) - 1
    put(lp(np.tanh(3 * saw), 900) * np.exp(-x * 4), at, .32)
# riser during the anticipation (0.4 -> 1.0 s)
x = np.arange(int(.6 * SR)) / SR
put(bp(rng.standard_normal(len(x)), 400, 3000) * (x / .6) ** 2 * .5 + np.sin(2 * np.pi * (200 + 600 * x / .6) * x) * (x / .6) * .15, .4, .5)
def whoosh(at, d, f0, f1, g, pan):
    n = int(d * SR); nz = rng.standard_normal(n); out = np.zeros(n)
    for k in range(0, n, 512):
        f = f0 + (f1 - f0) * k / n; out[k:k + 512] = bp(nz[k:k + 512], f * .6, f * 1.7)
    put(out * np.sin(np.pi * np.arange(n) / n) ** 2 / (abs(out).max() + 1e-9), at, g, pan)
whoosh(.98, .32, 500, 3500, .55, .3)     # push-off + smear
whoosh(2.30, .25, 900, 2800, .3, .4)     # reach
whoosh(2.66, .3, 700, 2400, .3, .4)      # lift
# landing impact: sub thump + crunch
x = np.arange(int(.5 * SR)) / SR
put(np.sin(2 * np.pi * (40 + 70 * np.exp(-x * 20)) * x) * np.exp(-x * 7) + lp(rng.standard_normal(len(x)), 2500) * np.exp(-x * 25) * .5, 1.42, .9)
# grab foley: cloth + glass tick
x = np.arange(int(.12 * SR)) / SR
put(bp(rng.standard_normal(len(x)), 1500, 6000) * np.exp(-x * 40) * .6 + np.sin(2 * np.pi * 3200 * x) * np.exp(-x * 60) * .4, 2.50, .4, .3)
# product hit: bright chord stab + shimmer
x = np.arange(int(.9 * SR)) / SR
stab = sum(np.sign(np.sin(2 * np.pi * hz(m) * x)) for m in [64, 67, 71, 76]) / 4
put(lp(stab, 3500) * np.exp(-x * 5) * .5 + sum(np.sin(2 * np.pi * f * x) * np.exp(-x * 6) for f in [2637, 3520, 4186]) * .08, 2.92, .6)
# reaction sting (cartoon boing-ish pitch pop) and final accent (bass drop + crash)
x = np.arange(int(.25 * SR)) / SR
put(np.sin(2 * np.pi * (500 + 900 * x / .25) * x) * np.exp(-x * 9) * .5, 3.50, .45, -.2)
x = np.arange(int(1.2 * SR)) / SR
put(np.sin(2 * np.pi * (36 + 60 * np.exp(-x * 9)) * x) * np.exp(-x * 2.5) + hp(rng.standard_normal(len(x)), 5000) * np.exp(-x * 3) * .25, 3.83, .8)
mix = L / np.abs(L).max() * .89
mix *= np.clip((DUR - t) / .15, 0, 1)[:, None]
w.write("sound.wav", SR, (mix * 32767).astype(np.int16)); print("sound ok")
