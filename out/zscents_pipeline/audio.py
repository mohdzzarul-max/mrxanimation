"""Sound design + original music bed (synthesised here, no third-party audio), mixed under the untouched voice."""
import numpy as np, subprocess, os, wave
HERE = os.path.dirname(os.path.abspath(__file__))
SR = 44100
DUR = 21.633
N = int(SR * DUR)
rng = np.random.default_rng(3)
t_all = np.arange(N) / SR

def read_wav(p):
    with wave.open(p) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        return a.reshape(-1, w.getnchannels())
def write_wav(p, a):
    a = np.clip(a, -1, 1)
    with wave.open(p, 'w') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((a * 32767).astype(np.int16).tobytes())

def onepole_lp(x, fc):
    """time-varying one-pole lowpass; fc scalar or array (Hz)"""
    fc = np.broadcast_to(np.asarray(fc, np.float64), x.shape)
    a = 1 - np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x); s = 0.0
    for i in range(len(x)):
        s += a[i] * (x[i] - s); y[i] = s
    return y

def reverb_ir(sec=1.4, damp=3.2):
    n = int(SR * sec); tt = np.arange(n) / SR
    ir = rng.normal(0, 1, (n, 2)) * np.exp(-damp * tt)[:, None]
    ir[:, 0] = onepole_lp(ir[:, 0], 4000); ir[:, 1] = onepole_lp(ir[:, 1], 3600)
    return ir / np.sqrt((ir ** 2).sum(0))
IR = reverb_ir()
def fftconv(x, h):
    n = len(x) + len(h) - 1; nf = 1 << (n - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, nf) * np.fft.rfft(h, nf), nf)[:n]
def with_verb(mono, wet=0.35):
    st = np.stack([mono, mono], 1) * (1 - wet)
    for c in range(2):
        st[:, c] += wet * fftconv(mono, IR[:, c])[:len(mono)] * 3
    return st

def place(buf, sig, t0, gain=1.0):
    i0 = int(t0 * SR)
    if i0 < 0: sig = sig[-i0:]; i0 = 0
    n = min(len(sig), len(buf) - i0)
    if n > 0: buf[i0:i0 + n] += sig[:n] * gain

# ---------------------------------------------------------------- SFX
def impact(len_s=2.2):
    n = int(SR * len_s); tt = np.arange(n) / SR
    f = 40 + 75 * np.exp(-tt * 7)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 2.6)
    click = onepole_lp(rng.normal(0, 1, n), 2500) * np.exp(-tt * 90) * 2.5
    body = onepole_lp(rng.normal(0, 1, n), 900) * np.exp(-tt * 9) * 0.8
    m = sub * 0.9 + click + body
    return with_verb(m / np.abs(m).max(), 0.30)

def whoosh(dur=0.5, peak=0.62, up=True):
    n = int(SR * dur); tt = np.arange(n) / SR; p = tt / dur
    env = np.where(p < peak, (p / peak) ** 2.2, (1 - (p - peak) / (1 - peak)) ** 1.6)
    fc = (300 + 5200 * env) if up else (5500 - 4800 * p)
    x = onepole_lp(rng.normal(0, 1, n), fc)
    x = x - onepole_lp(x, 180)  # strip rumble
    m = x * env
    st = np.stack([m * (1 - 0.35 * p), m * (0.65 + 0.35 * p)], 1)  # slight L->R pan travel
    return st / np.abs(st).max()

def shimmer(len_s=1.6):
    n = int(SR * len_s); tt = np.arange(n) / SR
    m = np.zeros(n)
    for k in range(14):
        f = rng.uniform(2800, 9000); d = k * 0.018
        e = np.clip(tt - d, 0, None); on = (tt >= d)
        m += on * np.sin(2 * np.pi * f * e) * np.exp(-e * rng.uniform(3, 6)) * (0.6 + 0.4 * rng.random())
    m *= np.minimum(1, tt / 0.01)
    return with_verb(m / np.abs(m).max(), 0.5)

def thump(len_s=0.6):
    n = int(SR * len_s); tt = np.arange(n) / SR
    f = 55 + 60 * np.exp(-tt * 25)
    m = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9)
    m += onepole_lp(rng.normal(0, 1, n), 3000) * np.exp(-tt * 160) * 0.6
    return np.stack([m, m], 1) / np.abs(m).max()

sfx = np.zeros((N, 2))
place(sfx, impact(), 0.0, 0.85)
place(sfx, shimmer(), 0.17, 0.16)
for tc, g, up in [(1.77, .40, True), (2.70, .26, False), (6.73, .30, True), (7.43, .22, False),
                  (9.37, .30, True), (10.0, .22, False), (13.20, .38, True), (18.07, .24, False)]:
    w = whoosh(0.5); place(sfx, w, tc - 0.5 * 0.62, g)
for ta in (3.62, 7.92, 11.90):          # accent typography pops
    place(sfx, thump(), ta, 0.30)
place(sfx, whoosh(0.55), 19.0 - 0.55 * 0.62, 0.36)
place(sfx, impact(), 19.0, 0.55)
place(sfx, shimmer(), 19.4, 0.18)

# ---------------------------------------------------------------- music bed (original)
BEAT = 19.0 / 30                       # beat grid lands on the end-card hit at 19.0 s
def note(f, dur, amp=1.0, det=0.004):
    n = int(SR * dur); tt = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * (1 + d) * tt + ph) for d, ph in ((-det, 0), (0, 1.3), (det, 2.1)))
    s += 0.35 * sum(np.sin(2 * np.pi * 2 * f * (1 + d) * tt) for d in (-det, det))
    env = np.minimum(1, tt / 0.9) * np.minimum(1, (dur - tt) / 0.9)
    return s * env * amp
pad = np.zeros(N)
chords = [(73.42, 146.83, 174.61, 220.0, 261.63), (58.27, 116.54, 146.83, 174.61, 220.0),
          (65.41, 130.81, 164.81, 196.0, 246.94), (55.0, 110.0, 138.59, 164.81, 220.0)]  # Dm7 Bbmaj7 C(add) A
bar = BEAT * 4 * 2
k = 0; tcur = 0.0
while tcur < DUR:
    for i, f in enumerate(chords[k % 4]):
        place(pad, note(f, bar + 1.0, 0.5 if i == 0 else 0.22), tcur)
    tcur += bar; k += 1
pad = onepole_lp(pad, 1400)
pulse = np.zeros(N)
nb = int(DUR / BEAT) + 1
for b in range(nb):
    tb = b * BEAT
    n = int(SR * 0.45); tt = np.arange(n) / SR
    root = chords[int(tb // bar) % 4][0]
    kick = np.sin(2 * np.pi * np.cumsum(root * (1 + 1.5 * np.exp(-tt * 30))) / SR) * np.exp(-tt * 7)
    place(pulse, kick, tb, 0.9)
    hat = rng.normal(0, 1, int(SR * 0.04)); hat = (hat - onepole_lp(hat, 7000)) * np.exp(-np.arange(len(hat)) / SR * 120)
    place(pulse, hat, tb + BEAT / 2, 0.10)
music = np.stack([pad * 0.9 + pulse, pad * 0.9 + pulse], 1)
music[:, 1] = np.roll(music[:, 1], int(SR * 0.012))  # width
music /= np.abs(music).max()
# arrangement: hit on frame 1, settle, lift into end card, ring out
arr = np.interp(t_all, [0, 0.4, 2.0, 2.9, 18.2, 19.0, 20.5, DUR], [1.0, 0.85, 0.85, 0.55, 0.55, 1.0, 0.95, 0.0])
music *= arr[:, None]

# ---------------------------------------------------------------- voice + ducking
voice = read_wav(os.path.join(HERE, 'voice_proc.wav'))[:N]
if len(voice) < N: voice = np.pad(voice, ((0, N - len(voice)), (0, 0)))
vm = np.abs(voice).mean(1)
env = np.sqrt(np.convolve(vm ** 2, np.ones(2205) / 2205, 'same'))
act = (env > 10 ** (-38 / 20)).astype(float)
act = np.convolve(act, np.ones(8820) / 8820, 'same')  # 200 ms smoothing = attack/release
act = np.clip(act * 1.5, 0, 1)
duck = 1 - 0.62 * act

def rms(x): return np.sqrt((x ** 2).mean())
speech_rms = rms(voice[act > 0.9]) if (act > 0.9).any() else rms(voice)
voice *= (10 ** (-18 / 20)) / speech_rms
music *= (10 ** (-27 / 20)) / rms(music[t_all < 3]) * duck[:, None]
sfx *= 10 ** (-7 / 20) / np.abs(sfx).max()
mix = voice + music + sfx
mix /= max(1.0, np.abs(mix).max() / 0.95)
write_wav(os.path.join(HERE, 'mix.wav'), mix)
print('mix written', mix.shape)
db = lambda x: 20 * np.log10(rms(x) + 1e-9)
sp = act > 0.9
print('speech: voice %.1f dB, music %.1f dB, sfx %.1f dB' % (db(voice[sp]), db(music[sp]), db(sfx[sp])))
gap = (t_all > 1.2) & (t_all < 2.8)
print('gap 1.2-2.8: music %.1f dB, sfx %.1f dB' % (db(music[gap]), db(sfx[gap])))
