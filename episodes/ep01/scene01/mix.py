"""Scene 01 sound: places the dialogue, treats X-BOT's off-screen voice, synthesises a
restrained music bed and two soft SFX, then writes:
  out/scene01_mix.wav   48 kHz stereo master for the 12 s scene
Mr X wears a full mask, so there is no lip-sync; CUES only place the lines against the picture."""
import json, numpy as np, scipy.io.wavfile as w
from scipy.signal import resample_poly, butter, lfilter

SR, DUR, FPS = 48000, 12.0, 24
N = int(SR * DUR)
CUES = {"mrx_l1": 0.40, "mrx_l2": 3.50, "xbot_l3": 10.10}
rng = np.random.default_rng(1)
t = np.arange(N) / SR

def load(name):
    sr, a = w.read(f"audio/{name}.wav")
    a = a.astype(np.float32)
    if a.ndim > 1: a = a.mean(1)
    if np.abs(a).max() > 1.5: a /= 32768
    g = np.gcd(SR, sr)
    a = resample_poly(a, SR // g, sr // g)
    return a / (np.abs(a).max() + 1e-9)

def place(buf, a, at, gain=1.0, pan=0.0):  # pan -1 left .. +1 right (equal power)
    i = int(at * SR); a = a[: max(0, N - i)]
    th = (pan + 1) * np.pi / 4
    buf[i:i + len(a), 0] += a * gain * np.cos(th)
    buf[i:i + len(a), 1] += a * gain * np.sin(th)

def lp(a, hz, order=2): b, c = butter(order, hz / (SR / 2)); return lfilter(b, c, a)
def hp(a, hz, order=2): b, c = butter(order, hz / (SR / 2), "high"); return lfilter(b, c, a)

voice = np.zeros((N, 2)); music = np.zeros((N, 2)); sfx = np.zeros((N, 2))

# ---- dialogue ----
l1, l2 = load("mrx_l1"), load("mrx_l2")
place(voice, hp(l1, 90), CUES["mrx_l1"], 0.78, -0.05)
place(voice, hp(l2, 90), CUES["mrx_l2"], 0.78, -0.05)

# X-BOT: metallic comb + light ring-mod + saturation, slightly distant, panned off-screen right
x = load("xbot_l3"); tt = np.arange(len(x)) / SR
x = 0.55 * x + 0.45 * x * np.sin(2 * np.pi * 110 * tt)
d = int(0.0045 * SR); y = x.copy()
for i in range(d, len(y)): y[i] += 0.55 * y[i - d]
y = np.tanh(2.4 * hp(y, 250) / (np.abs(y).max() + 1e-9))
y = np.concatenate([y, np.zeros(int(0.5 * SR))])
for dl, g in [(0.07, 0.25), (0.15, 0.12)]:  # small-room slap: he's just out of frame
    k = int(dl * SR); y[k:] += g * y[:-k]
place(voice, y / np.abs(y).max(), CUES["xbot_l3"], 0.85, 0.75)

# ---- music bed: 100 bpm, C minor, soft pad + bass + brushed kit ----
bpm = 100; beat = 60 / bpm
chords = [[48, 51, 55, 58, 62], [44, 48, 51, 55, 60], [41, 44, 48, 51, 55], [43, 47, 50, 53, 55]]  # Cm9 Abmaj7 Fm9 G7
hz = lambda n: 440 * 2 ** ((n - 69) / 12)
pad = np.zeros(N); bass = np.zeros(N)
for bar in range(int(DUR / (4 * beat)) + 1):
    ch = chords[bar % 4]; s0 = bar * 4 * beat
    seg = (t >= s0) & (t < s0 + 4 * beat); ts = t[seg] - s0
    env = np.minimum(1, ts / 0.25) * np.minimum(1, (4 * beat - ts) / 0.2)
    for n in ch[1:]:
        f = hz(n + 12)
        pad[seg] += env * (np.sin(2 * np.pi * f * ts) + 0.3 * np.sin(2 * np.pi * 2 * f * ts + 0.4 * np.sin(2 * np.pi * 0.3 * ts)))
    for b8 in [0, 1.5, 2.5, 3]:  # syncopated bass plucks
        b0 = s0 + b8 * beat; bs = (t >= b0) & (t < b0 + 0.45); tb = t[bs] - b0
        bass[bs] += np.exp(-tb * 7) * np.tanh(2 * np.sin(2 * np.pi * hz(ch[0] - 12) * tb))
pad = lp(pad, 1800) * 0.06; bass = lp(bass, 600) * 0.35
kit = np.zeros(N)
for i in range(int(DUR / (beat / 2)) + 1):
    s0 = i * beat / 2; L = int(0.12 * SR); j = int(s0 * SR)
    if j >= N: break
    seg = slice(j, min(N, j + L)); tb = np.arange(seg.stop - seg.start) / SR
    kit[seg] += 0.08 * hp(rng.standard_normal(len(tb)), 7000) * np.exp(-tb * 60)          # hat
    if i % 4 == 0: kit[seg] += 0.5 * np.sin(2 * np.pi * (55 + 90 * np.exp(-tb * 30)) * tb) * np.exp(-tb * 18)  # kick
    if i % 4 == 2: kit[seg] += 0.12 * lp(rng.standard_normal(len(tb)), 3500) * np.exp(-tb * 25)  # brush
bed = pad + bass + kit
music[:, 0] = bed; music[:, 1] = bed
# gentle fade in; drop to a tense hush when X-BOT shouts (scene 02 picks it up)
mus_env = np.clip(t / 0.6, 0, 1) * np.where(t < 10.05, 1.0, np.interp(t, [10.05, 10.25], [1.0, 0.35]))
music *= mus_env[:, None]

# ---- SFX: cloth whoosh on the bottle lift, quick swish on the head turn, small stinger on the shout ----
def whoosh(at, dur, g, f0, f1, pan):
    L = int(dur * SR); tb = np.arange(L) / SR
    nz = rng.standard_normal(L); out = np.zeros(L)
    for k in range(0, L, 1024):  # sweeping band-pass, blockwise
        f = f0 + (f1 - f0) * k / L; b, a = butter(2, [f * 0.6 / (SR / 2), min(0.99, f * 1.6 / (SR / 2))], "band")
        out[k:k + 1024] = lfilter(b, a, nz[k:k + 1024])
    env = np.sin(np.pi * tb / dur) ** 2
    place(sfx, out * env / (np.abs(out).max() + 1e-9), at, g, pan)
whoosh(3.12, 0.5, 0.10, 600, 2600, -0.2)   # lift + cut into the close-up
# close-up graphics: CLEARANCE banner thump, glint shimmer
th = np.arange(int(0.25 * SR)) / SR
place(sfx, np.sin(2 * np.pi * (70 + 60 * np.exp(-th * 25)) * th) * np.exp(-th * 14), 4.04, 0.22, 0.0)
sh = np.zeros(int(0.6 * SR)); ts2 = np.arange(len(sh)) / SR
for f in [2637, 3136, 3951, 4699]: sh += np.sin(2 * np.pi * f * ts2) * np.exp(-((ts2 - 0.1 * (f / 2637 - 1) * 2) ** 2) / 0.004)
place(sfx, sh / np.abs(sh).max(), 4.47, 0.05, 0.3)
whoosh(10.28, 0.28, 0.12, 1200, 3500, 0.3)
st = np.zeros(int(0.9 * SR)); ts = np.arange(len(st)) / SR
for f in [hz(55), hz(62), hz(67)]: st += np.sin(2 * np.pi * f * ts) * np.exp(-ts * 4)
place(sfx, lp(st, 2500) / 3, 10.12, 0.16, 0.2)

# ---- duck music under dialogue ----
vabs = np.abs(voice).sum(1); win = int(0.12 * SR)
vlev = np.convolve(vabs, np.ones(win) / win, "same")
duck = 1 - 0.55 * np.clip(vlev / (vlev.max() * 0.25), 0, 1)
duck = np.convolve(duck, np.ones(int(0.15 * SR)) / int(0.15 * SR), "same")
mix = voice + music * duck[:, None] + sfx
mix *= 0.89 / np.abs(mix).max()
fade = np.clip((DUR - t) / 0.02, 0, 1)[:, None]
w.write("out/scene01_mix.wav", SR, (mix * fade * 32767).astype(np.int16))

print("mix ok", {k: round(v, 2) for k, v in CUES.items()})
