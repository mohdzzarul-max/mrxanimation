"""Original procedural music + sound effects (numpy). Everything here is synthesized from scratch,
so the soundtrack is fully original and free of third-party licensing."""
import numpy as np

SR = 48000
rng = np.random.default_rng(7)


# ---------------------------------------------------------------- primitives
def t_(d):
    return np.arange(int(d * SR)) / SR


def env_adsr(n, a=0.005, d=0.1, s=0.6, r=0.2, sus_len=None):
    a_, d_, r_ = int(a * SR), int(d * SR), int(r * SR)
    sl = max(0, n - a_ - d_ - r_) if sus_len is None else int(sus_len * SR)
    e = np.concatenate([np.linspace(0, 1, max(a_, 1)), np.linspace(1, s, max(d_, 1)), np.full(sl, s),
                        np.linspace(s, 0, max(r_, 1))])
    return np.pad(e, (0, max(0, n - len(e))))[:n]


def expdec(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


def lp(x, fc):
    """One-pole lowpass (fc may be array)."""
    fc = np.broadcast_to(np.asarray(fc, float), x.shape)
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a[i]) * x[i] + a[i] * acc
        y[i] = acc
    return y


def lp_fast(x, fc):
    from scipy.signal import butter, lfilter
    b, a = butter(2, min(fc, SR / 2 - 100) / (SR / 2))
    return lfilter(b, a, x)


def hp_fast(x, fc):
    from scipy.signal import butter, lfilter
    b, a = butter(2, fc / (SR / 2), "high")
    return lfilter(b, a, x)


def bp_fast(x, f1, f2):
    from scipy.signal import butter, lfilter
    b, a = butter(2, [f1 / (SR / 2), min(f2, SR / 2 - 100) / (SR / 2)], "band")
    return lfilter(b, a, x)


def noise(d):
    return rng.uniform(-1, 1, int(d * SR))


def saw(f, d, detune=0.0):
    t = t_(d)
    return 2 * ((t * f * (1 + detune)) % 1) - 1


def sine(f, d, ph=0):
    return np.sin(2 * np.pi * f * t_(d) + ph)


def mtof(m):
    return 440 * 2 ** ((m - 69) / 12)


def ks(f, d, decay=0.996, bright=0.5):
    """Karplus-Strong plucked string."""
    n = int(d * SR)
    p = max(2, int(SR / f))
    buf = rng.uniform(-1, 1, p) * bright + (1 - bright) * np.sin(np.linspace(0, 2 * np.pi, p))
    out = np.empty(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = decay * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    return out


def fm(f, d, ratio=2.0, index=2.0, tau=0.6):
    t = t_(d)
    e = expdec(len(t), tau)
    return np.sin(2 * np.pi * f * t + index * e * np.sin(2 * np.pi * f * ratio * t)) * e


def epiano(f, d):
    return 0.6 * fm(f, d, 1.0, 1.4, 0.9) + 0.25 * fm(f * 2, d, 3.5, 1.0, 0.25)


def bell(f, d):
    return fm(f, d, 3.5, 3.0, 0.8) * 0.6


def pad(freqs, d, cutoff=1800, det=0.006):
    x = sum(saw(f, d, det) + saw(f, d, -det) for f in freqs) / (2 * len(freqs))
    x = lp_fast(x, cutoff)
    return x * env_adsr(len(x), 0.4, 0.3, 0.85, 0.6)


def kick(d=0.4):
    t = t_(d)
    f = 45 + 110 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * expdec(len(t), 0.12)


def snare(d=0.25):
    x = add(0.6 * hp_fast(noise(d), 1500), 0.4 * sine(190, d))
    return x * expdec(len(x), 0.06)


def hat(d=0.06, open_=False):
    return hp_fast(noise(d), 7000) * expdec(int(d * SR), 0.12 if open_ else 0.018)


def add(*xs):
    n = max(len(x) for x in xs)
    out = np.zeros(n)
    for x in xs:
        out[:len(x)] += x
    return out


def place(buf, x, t, gain=1.0):
    i = int(t * SR)
    if i >= len(buf):
        return
    x = x[:len(buf) - i]
    buf[i:i + len(x)] += x * gain


def chord_notes(root, kind):
    iv = {"maj7": [0, 4, 7, 11], "min9": [0, 3, 7, 10, 14], "min7": [0, 3, 7, 10], "dom7": [0, 4, 7, 10],
          "maj": [0, 4, 7], "min": [0, 3, 7], "sus": [0, 5, 7]}[kind]
    return [root + i for i in iv]


# ---------------------------------------------------------------- music cues
def music_luxury(d, bpm=96):
    out = np.zeros(int(d * SR))
    beat = 60 / bpm
    prog = [(57, "min9"), (53, "maj7"), (50, "min9"), (52, "dom7")]
    for bar in range(int(d / (4 * beat)) + 1):
        t0 = bar * 4 * beat
        r, k = prog[bar % 4]
        for i, nn in enumerate(chord_notes(r, k)):
            place(out, epiano(mtof(nn), 4 * beat) * 0.12, t0 + i * 0.012)
            place(out, epiano(mtof(nn), 2 * beat) * 0.07, t0 + 2.5 * beat)
        place(out, ks(mtof(r - 24), 2 * beat, 0.997, 0.2) * 0.35, t0)
        place(out, ks(mtof(r - 17), beat, 0.997, 0.2) * 0.25, t0 + 2.5 * beat)
        for b in range(4):
            place(out, kick() * 0.35, t0 + b * beat) if b in (0, 2) else None
            place(out, snare() * 0.12, t0 + b * beat) if b in (1, 3) else None
            for h in range(2):
                place(out, hat() * (0.08 if h else 0.05), t0 + b * beat + h * beat / 2)
        # sparkle on the top
        place(out, bell(mtof(r + 24 + [0, 7, 12, 7][bar % 4]), 1.2) * 0.04, t0 + 3.5 * beat)
    return out


def music_fantasy(d):
    out = np.zeros(int(d * SR))
    beat = 60 / 120
    prog = [(57, "min9"), (53, "maj7"), (48, "maj7"), (55, "sus")]
    for bar in range(int(d / (4 * beat)) + 1):
        t0 = bar * 4 * beat
        r, k = prog[bar % 4]
        place(out, pad([mtof(n) for n in chord_notes(r, k)], 4 * beat + 0.5, 2600) * 0.22, t0)
        for s in range(8):
            nn = chord_notes(r + 12, k)[s % len(chord_notes(r, k))]
            place(out, bell(mtof(nn + 12), 0.5) * 0.05, t0 + s * beat / 2)
        for b in range(4):
            place(out, kick() * 0.4, t0 + b * beat)
            place(out, hat(open_=True) * 0.06, t0 + b * beat + beat / 2)
        place(out, snare() * 0.18, t0 + beat)
        place(out, snare() * 0.18, t0 + 3 * beat)
    return out


def music_transaction(d):
    out = np.zeros(int(d * SR))
    beat = 60 / 112
    mel = [72, 76, 79, 76, 74, 77, 81, 77, 72, 76, 79, 84, 83, 79, 76, 74]
    for i in range(int(d / (beat / 2))):
        nn = mel[i % len(mel)]
        place(out, ks(mtof(nn), 0.3, 0.99, 0.7) * 0.18, i * beat / 2)
        if i % 4 == 0:
            place(out, ks(mtof(nn - 24), 0.4, 0.993, 0.3) * 0.3, i * beat / 2)
    return out


def music_suspicious(d):
    out = np.zeros(int(d * SR))
    out += pad([mtof(38), mtof(45), mtof(51)], d, 700) * 0.18
    beat = 60 / 80
    mel = [62, 61, 60, 59, 58, 57]
    for i in range(int(d / beat)):
        place(out, ks(mtof(mel[i % 6]), 0.25, 0.985, 0.6) * 0.18, i * beat)
        place(out, hp_fast(noise(0.02), 4000) * expdec(960, 0.01) * 0.1, i * beat + beat / 2)
    return out


def music_curious(d):
    out = np.zeros(int(d * SR))
    beat = 60 / 90
    mot = [69, 72, 76, None, 74, 72, None, 71]
    for i in range(int(d / (beat / 2))):
        nn = mot[i % len(mot)]
        if nn:
            place(out, epiano(mtof(nn), 0.6) * 0.1, i * beat / 2)
    out += pad([mtof(45), mtof(52), mtof(57)], d, 900) * 0.08
    return out


def music_tension(d):
    out = np.zeros(int(d * SR))
    n = len(out)
    out += pad([mtof(40), mtof(46)], d, 600) * 0.2 * np.linspace(0.6, 1.2, n)
    t, k = 0.0, 0
    while t < d:
        place(out, hp_fast(noise(0.02), 3000) * expdec(960, 0.008) * 0.25, t)
        place(out, sine(1200 if k % 2 else 900, 0.03) * expdec(1440, 0.01) * 0.1, t)
        t += max(0.12, 0.5 * (1 - t / d) + 0.1)
        k += 1
    return out


def music_drama(d):
    out = np.zeros(int(d * SR))
    trem = (np.sin(2 * np.pi * 12 * t_(d)) * 0.5 + 0.5)
    out += pad([mtof(40), mtof(47), mtof(52), mtof(55)], d, 1400) * 0.22 * trem
    return out


def music_villain(d):
    out = np.zeros(int(d * SR))
    beat = 60 / 104
    bass = [38, None, 45, None, 38, None, 45, 44, 43, None, 50, None, 43, None, 41, 40]
    mel = [62, 65, 69, 68, 67, None, 65, 62, 61, None, 64, None, 62, None, None, None]
    for i in range(int(d / (beat / 2))):
        tt = i * beat / 2
        b = bass[i % 16]
        if b:
            tuba = (saw(mtof(b), 0.22) * 0.5 + sine(mtof(b), 0.22)) * env_adsr(int(0.22 * SR), 0.01, 0.05, 0.6, 0.08)
            place(out, lp_fast(tuba, 900) * 0.28, tt)
        mm = mel[i % 16]
        if mm:
            place(out, ks(mtof(mm), 0.25, 0.985, 0.7) * 0.16, tt)
        if i % 4 == 2:
            place(out, snare(0.12) * 0.06, tt)
    for k in range(int(d / (8 * beat))):
        place(out, bell(mtof(74), 1.0) * 0.05, k * 8 * beat + 7 * beat)
    return out


def music_sad(d):
    out = np.zeros(int(d * SR))
    beat = 60 / 68
    prog = [(57, "min"), (53, "maj"), (48, "maj"), (55, "maj")]
    for bar in range(int(d / (4 * beat)) + 1):
        r, k = prog[bar % 4]
        t0 = bar * 4 * beat
        for i, nn in enumerate(chord_notes(r, k) + [r + 12]):
            place(out, epiano(mtof(nn), 2.5) * 0.08, t0 + i * beat * 0.5)
        place(out, ks(mtof(r - 12), 3.0, 0.998, 0.2) * 0.18, t0)
    return out


def music_action(d):
    out = np.zeros(int(d * SR))
    beat = 60 / 140
    prog = [45, 45, 48, 50]
    for bar in range(int(d / (4 * beat)) + 1):
        t0 = bar * 4 * beat
        r = prog[bar % 4]
        for e in range(8):
            place(out, lp_fast(saw(mtof(r - 12), 0.15), 1200) * expdec(int(0.15 * SR), 0.08) * 0.3, t0 + e * beat / 2)
        for b in range(4):
            place(out, kick() * 0.45, t0 + b * beat)
            place(out, hat() * 0.08, t0 + b * beat + beat / 2)
        place(out, snare() * 0.3, t0 + beat)
        place(out, snare() * 0.3, t0 + 3 * beat)
        stab = pad([mtof(n) for n in chord_notes(r + 12, "min")], 0.3, 3000)
        place(out, stab * 0.3, t0)
        place(out, stab * 0.22, t0 + 2.5 * beat)
    return out


def music_lesson(d):
    out = np.zeros(int(d * SR))
    beat = 60 / 100
    prog = [(60, "maj"), (55, "maj"), (57, "min"), (53, "maj")]
    for bar in range(int(d / (4 * beat)) + 1):
        r, k = prog[bar % 4]
        t0 = bar * 4 * beat
        notes = chord_notes(r + 12, k)
        for s in range(8):
            nn = notes[(s * 2) % len(notes)] + (12 if s % 4 == 3 else 0)
            mar = (sine(mtof(nn), 0.4) + 0.3 * sine(mtof(nn) * 4, 0.4)) * expdec(int(0.4 * SR), 0.12)
            place(out, mar * 0.12, t0 + s * beat / 2)
        place(out, ks(mtof(r - 12), 1.5, 0.996, 0.2) * 0.2, t0)
    return out


def music_quiet(d):
    return pad([mtof(57), mtof(64), mtof(69)], d, 900) * 0.07


def music_hook(d):
    out = np.zeros(int(d * SR))
    out += pad([mtof(33), mtof(40), mtof(45)], d, 700) * 0.22
    place(out, orch_hit() * 0.6, 0.27)
    return out


def music_end(d):
    out = np.zeros(int(d * SR))
    place(out, pad([mtof(n) for n in (57, 64, 69, 72, 76)], 4.5, 2200) * 0.25, 0.3)
    place(out, bell(mtof(81), 2.5) * 0.12, 0.3)
    place(out, bell(mtof(88), 2.5) * 0.07, 0.55)
    return out


MUSIC = {"hook": music_hook, "luxury": music_luxury, "fantasy": music_fantasy, "transaction": music_transaction,
         "suspicious": music_suspicious, "curious": music_curious, "tension": music_tension, "drama": music_drama,
         "villain": music_villain, "sad": music_sad, "sad_stop": music_sad, "action": music_action,
         "lesson": music_lesson, "punch_quiet": music_quiet, "end": music_end,
         "silence": lambda d: np.zeros(int(d * SR))}


# ---------------------------------------------------------------- sound effects
def orch_hit(d=1.6):
    n = int(d * SR)
    x = sum(saw(mtof(m), d, 0.004) for m in (40, 47, 52, 55, 59, 64)) / 6
    x = lp_fast(x, 3500) * expdec(len(x), 0.35)
    x = add(x, kick(d) * 0.8, lp_fast(noise(d), 2000) * expdec(int(d * SR), 0.08) * 0.6)
    return x


def whoosh(d=0.6, f0=300, f1=3000):
    n = int(d * SR)
    x = noise(d)
    from scipy.signal import butter, lfilter
    out = np.zeros(n)
    seg = 960
    for i in range(0, n, seg):
        fc = f0 + (f1 - f0) * np.sin(np.pi * i / n)
        b, a = butter(2, [max(50, fc * 0.6) / (SR / 2), min(fc * 1.6, SR / 2 - 200) / (SR / 2)], "band")
        out[i:i + seg] = lfilter(b, a, x[i:i + seg])
    return out * np.sin(np.linspace(0, np.pi, n)) ** 2 * 1.5


def sfx_spray():
    d = 0.7
    x = hp_fast(noise(d), 3500) * env_adsr(int(d * SR), 0.01, 0.1, 0.7, 0.35)
    return np.concatenate([bp_fast(noise(0.03), 800, 3000) * 0.6, x * 0.8])


def sfx_record_scratch(d=0.45):
    t = t_(d)
    f = 400 + 900 * np.sin(2 * np.pi * 5 * t) ** 2
    x = add(bp_fast(noise(d), 300, 3000) * 0.6, 0.4 * np.sin(2 * np.pi * np.cumsum(f) / SR))[:len(t)]
    return x * env_adsr(len(t), 0.005, 0.1, 0.8, 0.1)


def sfx_kaching():
    x = add(bell(mtof(88), 1.4) * 0.7, bell(mtof(93), 1.2) * 0.5)
    coins = np.zeros(int(0.8 * SR))
    for k in range(10):
        place(coins, bp_fast(noise(0.03), 4000, 9000) * expdec(1440, 0.008), 0.05 * k + rng.uniform(0, 0.03))
    place(x, coins * 0.5, 0.0)
    click = np.zeros(int(0.1 * SR))
    click[:200] = rng.uniform(-1, 1, 200) * np.linspace(1, 0, 200)
    return np.concatenate([click * 0.6, x])


def sfx_impact(d=0.8, big=1.0):
    n = int(d * SR)
    return add(kick(d) * 1.0, lp_fast(noise(d), 1500 * big) * expdec(n, 0.06 * big) * 0.7) * 0.9


def sfx_boom():
    d = 2.0
    n = int(d * SR)
    t = t_(d)
    sub = np.sin(2 * np.pi * np.cumsum(30 + 80 * np.exp(-t * 6)) / SR) * expdec(n, 0.7)
    return add(sub, lp_fast(noise(d), 900) * expdec(n, 0.4) * 0.8, whoosh(d, 200, 1200) * 0.2)


def sfx_sparkle():
    out = np.zeros(int(1.0 * SR))
    for k in range(7):
        place(out, bell(mtof(96 + rng.integers(0, 10)), 0.4) * 0.3, k * 0.07)
    return out


def sfx_shimmer():
    out = np.zeros(int(1.6 * SR))
    for k, nn in enumerate((84, 88, 91, 96, 100)):
        place(out, bell(mtof(nn), 1.0) * 0.25, k * 0.08)
    return out


def sfx_riser(d=1.8):
    t = t_(d)
    f = 200 * 2 ** (t * 2)
    return add(np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3, hp_fast(noise(d), 2000) * 0.3)[:len(t)] * (t / d) ** 2


def sfx_sniff():
    d = 0.32
    x = bp_fast(noise(d), 1500, 6000)
    e = np.concatenate([np.linspace(0, 1, int(0.12 * SR)), np.linspace(1, 0, int(0.2 * SR))])
    return x[:len(e)] * e * 0.8


def sfx_footsteps(n=8, gap=0.27):
    out = np.zeros(int((n * gap + 0.3) * SR))
    for k in range(n):
        st = add(lp_fast(noise(0.08), 1800) * expdec(int(0.08 * SR), 0.02), kick(0.08) * 0.3)
        place(out, st * (0.8 + 0.2 * rng.random()), k * gap)
    return out


def sfx_ambience(d=2.3):
    x = lp_fast(noise(d), 500) * 0.25
    for k in range(6):
        place(x, sine(rng.uniform(300, 900), 0.4) * expdec(int(0.4 * SR), 0.1) * 0.03, rng.uniform(0, d - 0.4))
    return x


def sfx_crowd(d=3.5):
    x = bp_fast(noise(d), 400, 3000)
    mod = 0.5 + 0.5 * lp_fast(rng.uniform(0, 1, int(d * SR)), 4)
    return x * mod * env_adsr(int(d * SR), 0.6, 0.4, 0.8, 1.0) * 0.6


def sfx_flash():
    x = np.zeros(int(0.5 * SR))
    x[:240] = rng.uniform(-1, 1, 240)
    t = t_(0.5)
    return add(x * 0.8, np.sin(2 * np.pi * np.cumsum(3000 + 4000 * t) / SR) * expdec(len(t), 0.1) * 0.1)


def sfx_door_creak(d=1.4):
    t = t_(d)
    f = 180 + 120 * np.sin(2 * np.pi * 1.3 * t) + 40 * rng.standard_normal(len(t)).cumsum() / 300
    x = saw(1, d) * 0
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.3
    return bp_fast(x, 300, 2500) * env_adsr(len(t), 0.1, 0.2, 0.8, 0.3)


def sfx_money(d=2.6):
    out = np.zeros(int(d * SR))
    t = 0.0
    while t < d - 0.1:
        place(out, bp_fast(noise(0.04), 2500, 9000) * expdec(1920, 0.01) * 0.7, t)
        t += rng.uniform(0.07, 0.11)
    return out


def sfx_pour(d=0.9):
    x = bp_fast(noise(d), 300, 1500)
    am = 0.5 + 0.5 * np.sin(2 * np.pi * 9 * t_(d) + rng.uniform(0, 6))
    return x * am * env_adsr(len(x), 0.05, 0.1, 0.8, 0.2)


def sfx_boing():
    d = 0.6
    t = t_(d)
    f = 300 + 150 * np.sin(2 * np.pi * 14 * t) * np.exp(-t * 4)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * expdec(len(t), 0.25) * 0.6


def sfx_question():
    d = 0.4
    t = t_(d)
    return np.sin(2 * np.pi * np.cumsum(400 + 600 * t / d) / SR) * env_adsr(len(t), 0.01, 0.1, 0.6, 0.1) * 0.4


def sfx_cricket(d=2.5):
    out = np.zeros(int(d * SR))
    for k in range(int(d / 0.6)):
        for j in range(3):
            place(out, sine(4400, 0.025) * 0.2 * np.hanning(1200), k * 0.6 + j * 0.05)
    return out


def sfx_ting():
    return add(bell(mtof(88), 1.2) * 0.8, np.concatenate([np.zeros(int(0.12 * SR)), bell(mtof(95), 1.0) * 0.6]))


def sfx_bass_drop():
    d = 1.6
    t = t_(d)
    sub = np.sin(2 * np.pi * np.cumsum(90 * np.exp(-t * 2) + 28) / SR) * expdec(len(t), 0.8)
    return add(sub * 1.2, sfx_impact(d) * 0.6)


def sfx_slam():
    return add(sfx_impact(1.0, 1.3) * 1.1, bp_fast(noise(0.3), 1500, 6000) * expdec(int(0.3 * SR), 0.05) * 0.4)


def sfx_steam(d=1.4):
    return hp_fast(noise(d), 2500) * env_adsr(int(d * SR), 0.05, 0.2, 0.6, 0.5) * 0.5


def sfx_rumble(d=2.5):
    return lp_fast(noise(d), 120) * 2.5 * env_adsr(int(d * SR), 0.3, 0.3, 0.8, 0.6)


def sfx_holo_on():
    d = 0.7
    t = t_(d)
    return add(np.sin(2 * np.pi * np.cumsum(300 + 1500 * t / d) / SR) * env_adsr(len(t), 0.01, 0.2, 0.4, 0.3) * 0.35,
               sfx_shimmer() * 0.4)


def sfx_glitch():
    out = np.zeros(int(0.4 * SR))
    for k in range(8):
        place(out, np.sign(sine(rng.uniform(300, 2000), 0.03)) * 0.2, k * 0.045)
    return out


def sfx_tap(hollow=False):
    d = 0.3
    x = add(sine(140 if hollow else 90, d) * expdec(int(d * SR), 0.08), bp_fast(noise(d), 200, 1200) * expdec(int(d * SR), 0.03))
    return x


def sfx_glint():
    return add(bell(mtof(100), 0.8) * 0.5, sine(mtof(107), 0.5) * expdec(int(0.5 * SR), 0.1) * 0.2)


def sfx_sting_low():
    return pad([mtof(38), mtof(41), mtof(44)], 2.5, 600) * 0.6


def sfx_cap_click():
    x = np.zeros(int(0.15 * SR))
    x[:120] = rng.uniform(-1, 1, 120)
    return bp_fast(x, 1500, 8000) * 2.0


def sfx_rustle(d=0.6):
    return bp_fast(noise(d), 1500, 7000) * (0.4 + 0.6 * np.abs(lp_fast(rng.uniform(-1, 1, int(d * SR)), 30))) * 0.6


def sfx_thunder():
    return add(sfx_rumble(2.0) * 0.8, sfx_impact(1.2) * 0.4)


def sfx_facepalm():
    return add(bp_fast(noise(0.12), 500, 4000) * expdec(int(0.12 * SR), 0.02) * 1.2, sfx_tap() * 0.3)


def build_sfx():
    return {
        "spray": sfx_spray(), "impact_hit": sfx_impact(), "whoosh_fast": whoosh(0.35, 500, 5000),
        "whoosh": whoosh(0.7), "record_scratch": sfx_record_scratch(), "record_scratch_short": sfx_record_scratch(0.25),
        "mall_ambience": sfx_ambience(), "shimmer": sfx_shimmer(), "promo_hit": add(sfx_impact(0.6) * 0.8, sfx_glint() * 0.3),
        "sparkle": sfx_sparkle(), "ding": bell(mtof(91), 1.0), "riser": sfx_riser(), "chest_tap": sfx_tap() * 0.8,
        "glint": sfx_glint(), "crowd_cheer": sfx_crowd(), "camera_flash": sfx_flash(), "impact_small": sfx_impact(0.4, 0.7),
        "slowmo_whoosh": whoosh(1.6, 120, 900), "kaching": sfx_kaching(), "sting_low": sfx_sting_low(),
        "room_tone": lp_fast(noise(2.4), 300) * 0.12, "box_place": sfx_tap() * 0.7, "rustle": sfx_rustle(),
        "cap_click": sfx_cap_click(), "sniff": sfx_sniff(), "orch_hit": orch_hit(), "anger_rumble": sfx_rumble(),
        "steam": sfx_steam(), "slam": sfx_slam(), "door_creak": sfx_door_creak(), "money_count": sfx_money(),
        "reveal_sting": add(orch_hit(2.0) * 0.6, sfx_sting_low() * 0.5), "drum_tap": sfx_tap(True),
        "pour": sfx_pour(), "boom": sfx_boom(), "land_thud": sfx_impact(0.9, 1.2), "boing": sfx_boing(),
        "question": sfx_question(), "fall_whoosh": whoosh(0.6, 800, 200), "bed_thud": sfx_impact(0.5, 0.5) * 0.8,
        "facepalm": sfx_facepalm(), "cricket": sfx_cricket(), "holo_on": sfx_holo_on(), "holo_swap": sfx_glitch(),
        "ting": sfx_ting(), "bass_drop": sfx_bass_drop(), "footsteps": sfx_footsteps(),
        "thunder_comic": sfx_thunder(),
    }
