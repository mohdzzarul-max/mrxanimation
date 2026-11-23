"""ZSCENTS 21 s ad: original instrumental music + SFX (no voices, no vocal samples).
Electro-punk / funky breakbeat, 140 bpm, E minor. All events are placed on the ad's frame times (24 fps).
-> music_sfx.wav (48 kHz stereo, peak ~-1 dBFS)"""
import numpy as np, scipy.io.wavfile as w
from scipy.signal import butter, lfilter
SR, DUR = 48000, 21.0; N = int(SR * DUR); t = np.arange(N) / SR; rng = np.random.default_rng(7)
MUS = np.zeros((N, 2)); SFX = np.zeros((N, 2))
F = lambda fr: fr / 24
def filt(a, kind, hz): b, c = butter(2, np.array(hz) / (SR / 2), kind); return lfilter(b, c, a)
def put(buf, a, at, g=1, pan=0):
    i = int(at * SR)
    if i >= N: return
    a = a[:N - i]; th = (pan + 1) * np.pi / 4
    buf[i:i + len(a), 0] += a * g * np.cos(th); buf[i:i + len(a), 1] += a * g * np.sin(th)
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
T_ = lambda d: np.arange(int(d * SR)) / SR
beat = 60 / 140; s16 = beat / 4
def kick(): x = T_(.28); return np.sin(2 * np.pi * (46 + 150 * np.exp(-x * 34)) * x) * np.exp(-x * 10)
def snare(): x = T_(.22); return filt(rng.standard_normal(len(x)), 'high', 1700) * np.exp(-x * 18) * .65 + np.sin(2 * np.pi * 185 * x) * np.exp(-x * 28) * .4
def hat(o=False): x = T_(.16 if o else .05); return filt(rng.standard_normal(len(x)), 'high', 8000) * np.exp(-x * (18 if o else 90))
def clap(): x = T_(.2); n = filt(rng.standard_normal(len(x)), 'band', [900, 3500]); env = sum(np.exp(-np.maximum(x - d, 0) * 60) * (x >= d) for d in (0, .012, .024)); return n * env * .5
def saw(f, d): x = T_(d); return 2 * ((x * f) % 1) - 1
def sq(f, d): x = T_(d); return np.sign(np.sin(2 * np.pi * f * x))

# ---------- arrangement ----------
# sections in seconds: intro hook 0–1.42 | groove A 1.42–8.0 | build 8.0–10.42 | DROP 10.42–13.0 | groove B 13.0–17.0 | build 17.0–18.5 | finale 18.5–20.4 | tail
def drums(t0, t1, pattern='A', g=1.0):
    k = {'A': [0, 6, 10], 'B': [0, 3, 6, 10, 14], 'drop': [0, 4, 8, 11, 14]}[pattern]
    s = [4, 12]
    n = 0
    while True:
        at = t0 + n * s16
        if at >= t1 - .02: break
        st = n % 16
        if st in k: put(MUS, kick(), at, .95 * g)
        if st in s: put(MUS, snare(), at, .6 * g, .1); put(MUS, clap(), at, .35 * g, -.1)
        put(MUS, hat(st % 4 == 2), at, (.16 if st % 2 else .24) * g, -.35)
        n += 1
riff = [40, 40, 52, 40, 43, 40, 47, 45, 40, 40, 52, 40, 50, 48, 47, 43]   # E-minor punk bass
def bass(t0, t1, g=1.0, cutoff=900):
    n = 0
    while True:
        at = t0 + n * 2 * s16
        if at >= t1 - .05: break
        d = 2 * s16 * .9; x = T_(d)
        put(MUS, filt(np.tanh(3.2 * saw(hz(riff[n % 16]), d)), 'low', cutoff) * np.exp(-x * 3.5), at, .34 * g)
        n += 1
lead = [(0, 64, 2), (2, 67, 2), (4, 71, 1), (5, 69, 1), (6, 67, 2), (8, 64, 2), (10, 62, 2), (12, 64, 4)]  # catchy 8th-note motif (16ths)
def lead_phrase(at0, g=1.0, oct=0):
    for st, m, ln in lead:
        d = ln * s16 * .95; x = T_(d)
        tone = sq(hz(m + 12 + oct), d) * .5 + saw(hz(m + 12 + oct) * 1.005, d) * .5
        put(MUS, filt(tone, 'low', 3800) * np.minimum(1, x / .005) * np.exp(-x * 3), at0 + st * s16, .13 * g, .25)
def stab(at, chord=(64, 67, 71), g=1.0, d=.5):
    x = T_(d); s = sum(sq(hz(m), d) for m in chord) / len(chord)
    put(MUS, filt(s, 'low', 4200) * np.exp(-x * 6), at, .3 * g)
def riser(t0, t1, g=1.0):
    d = t1 - t0; x = T_(d); k = x / d
    nz = filt(rng.standard_normal(len(x)), 'band', [500, 6000]) * k ** 2
    tone = np.sin(2 * np.pi * (180 * x + 700 * x * k)) * k
    put(MUS, nz * .35 + tone * .15, t0, g)
def snare_roll(t0, t1):
    n = 0
    while t0 + n * s16 / 2 < t1:
        k = n * s16 / 2 / (t1 - t0); put(MUS, snare(), t0 + n * s16 / 2, .15 + .35 * k); n += 1

# intro hook: stab + kick on frame 0, lead phrase straight away (first-second hook)
put(MUS, kick(), 0, 1.0); stab(0, g=1.3, d=.6); lead_phrase(0.02, 1.1)
riser(.40, 1.0, .9)
drums(1.42, 8.0, 'A'); bass(1.42, 8.0)
for k in range(3): lead_phrase(1.42 + k * 16 * s16 + 8 * s16, .9)
# build into the price reveal
bass(8.0, 10.40, .7, 500); drums(8.0, 9.2, 'A', .55); snare_roll(9.2, 10.4); riser(9.25, 10.40, 1.2)
# DROP on "SEMUA BAWAH RM55!" (frame 246/250 → 10.42 s)
drums(10.42, 13.0, 'drop', 1.1); bass(10.42, 13.0, 1.2, 1300)
stab(10.42, (52, 59, 64, 67), 1.6, .9); lead_phrase(10.42 + 8 * s16, 1.2, 12); lead_phrase(10.42 + 24 * s16, 1.2, 12)
# groove B (limited stock)
drums(13.0, 17.0, 'B', .95); bass(13.0, 17.0, 1.0, 1000)
for k in range(2): lead_phrase(13.0 + k * 16 * s16 + 4 * s16, .85)
# short build, finale, ending chord
drums(17.0, 18.0, 'A', .8); bass(17.0, 18.5, .8, 700); snare_roll(18.0, 18.62); riser(17.6, 18.62, 1.0)
drums(18.62, 20.3, 'drop', 1.0); bass(18.62, 20.3, 1.0, 1100); lead_phrase(18.62 + 4 * s16, 1.0, 12)
x = T_(1.0); put(MUS, kick(), 20.32, 1.1); stab(20.32, (52, 59, 64, 67, 71), 1.8, 1.0)
put(MUS, filt(rng.standard_normal(len(x)), 'high', 5000) * np.exp(-x * 3) * .25, 20.32)

# ---------- SFX (frame-synced) ----------
def whoosh(at, d, f0, f1, g, pan=0):
    n = int(d * SR); nz = rng.standard_normal(n); out = np.zeros(n)
    for k in range(0, n, 512):
        f = f0 + (f1 - f0) * k / n; out[k:k + 512] = filt(nz[k:k + 512], 'band', [f * .6, min(f * 1.7, 20000)])
    put(SFX, out * np.sin(np.pi * np.arange(n) / n) ** 2 / (abs(out).max() + 1e-9), at, g, pan)
def impact(at, g=1.0):
    x = T_(.5); put(SFX, np.sin(2 * np.pi * (40 + 80 * np.exp(-x * 20)) * x) * np.exp(-x * 7) + filt(rng.standard_normal(len(x)), 'low', 2600) * np.exp(-x * 24) * .5, at, g)
def popfx(at, f0=600, g=.3, pan=0):
    x = T_(.15); put(SFX, np.sin(2 * np.pi * (f0 + 1100 * np.exp(-x * 35)) * x) * np.exp(-x * 24), at, g, pan)
def sparkle(at, g=.12):
    x = T_(.6)
    put(SFX, sum(np.sin(2 * np.pi * f * x) * np.exp(-((x - d) ** 2) / .002) for f, d in [(2637, .0), (3136, .07), (3951, .14), (4699, .21)]), at, g, .3)
def grab(at, g=.4):
    x = T_(.12); put(SFX, filt(rng.standard_normal(len(x)), 'band', [1500, 6000]) * np.exp(-x * 40) * .6 + np.sin(2 * np.pi * 3200 * x) * np.exp(-x * 60) * .4, at, g, .3)
def click(at, g=.25): x = T_(.03); put(SFX, filt(rng.standard_normal(len(x)), 'high', 3000) * np.exp(-x * 200), at, g, -.2)
# shot 1 (approved test timings)
impact(0, .7); popfx(F(3), 520, .3); popfx(F(12), 700, .25)
whoosh(.98, .32, 500, 3500, .55, .3); impact(1.42, .9); whoosh(2.30, .25, 900, 2800, .3, .4)
grab(2.50); whoosh(2.66, .3, 700, 2400, .3, .4); sparkle(2.92, .14)
x = T_(.25); put(SFX, np.sin(2 * np.pi * (500 + 900 * x / .25) * x) * np.exp(-x * 9) * .5, 3.50, .4, -.2)
# shot 2: presentation swoosh into the cut, text impacts, sparkle
whoosh(F(118), .25, 600, 3800, .55, -.2); impact(F(124), .8)
impact(F(134), .55); popfx(F(146), 560, .32); popfx(F(152), 760, .3); sparkle(F(158), .14)
# shot 3: transition, 55 ML pop, glint, the big hit
whoosh(F(188), .35, 400, 4200, .5); popfx(F(220), 480, .35)
impact(F(250), 1.3); sparkle(F(272), .16)
# shot 4: cut, notice click, gesture swipe, text pops, grab, lift
whoosh(F(310), .2, 900, 3000, .35); click(F(318)); click(F(321))
whoosh(F(330), .28, 700, 3200, .4, .3); popfx(F(340), 560, .32); grab(F(364)); whoosh(F(370), .25, 800, 2600, .3, .3); popfx(F(374), 720, .3)
# shot 5: take sting, final-pose accent, flash whoosh, end-card impact + pops
x = T_(.25); put(SFX, np.sin(2 * np.pi * (520 + 900 * x / .25) * x) * np.exp(-x * 9) * .5, F(408), .38, -.2)
sparkle(F(416), .12); whoosh(F(432), .3, 500, 4500, .45); impact(F(448), .9)
popfx(F(452), 600, .28); popfx(F(460), 760, .3); popfx(F(472), 900, .25)

# ---------- mix ----------
mix = MUS * .8 + SFX * .9
mix = np.tanh(mix * 1.1) / np.tanh(1.1 * np.abs(mix).max() * 1.0)   # gentle limiter
mix = mix / np.abs(mix).max() * .89                                  # ~-1 dBFS
mix *= np.clip((DUR - t) / .05, 0, 1)[:, None]
w.write("music_sfx.wav", SR, (mix * 32767).astype(np.int16))
print("ok", round(20 * np.log10(np.abs(mix).max()), 2), "dBFS peak")
