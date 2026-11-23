"""Assemble the full soundtrack from timeline.py: dialogue (with per-cue tempo), music cues with
crossfades and dialogue ducking, SFX. Writes:
  audio/music_stem.wav, audio/sfx_stem.wav, audio/dialogue_stem.wav, audio/final_mix.wav (48 kHz stereo)
"""
import os, subprocess, sys, tempfile
import numpy as np, soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import timeline as TL  # noqa
import synth as S  # noqa

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "audio")
os.makedirs(OUT, exist_ok=True)
SR = S.SR


def db(x):
    return 10 ** (x / 20)


def load_voice(lid, tempo):
    p = os.path.join(ROOT, "voices", lid + ".wav")
    if abs(tempo - 1.0) > 1e-3:
        tmp = os.path.join(tempfile.gettempdir(), f"{lid}_{tempo}.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", p, "-af", f"rubberband=tempo={tempo}", "-ar", str(SR),
                        tmp], check=True)
        p = tmp
    w, sr = sf.read(p)
    if w.ndim > 1:
        w = w.mean(1)
    assert sr == SR
    return w


def main():
    starts, total_f = TL.scene_starts()
    N = int(total_f / TL.FPS * SR) + SR
    dia = np.zeros(N)
    sfx = np.zeros(N)
    mus = np.zeros(N)
    lib = S.build_sfx()
    # ---- dialogue + sfx
    for s in TL.SHOTS:
        t0 = starts[s["id"]] / TL.FPS
        for lid, f, tempo in s["lines"]:
            S.place(dia, load_voice(lid, tempo), t0 + f / TL.FPS, 1.0)
        for name, f, g in s["sfx"]:
            x = lib[name]
            x = x / (np.abs(x).max() + 1e-9) * 0.8
            S.place(sfx, x, t0 + f / TL.FPS, db(g))
    # ---- music: segments by state change
    segs = []
    for s in TL.SHOTS:
        if s["music"]:
            segs.append((starts[s["id"]] / TL.FPS, s["music"]))
    segs.append((total_f / TL.FPS, None))
    music_gain = {"hook": -4, "luxury": -6, "fantasy": -4, "transaction": -6, "suspicious": -5, "curious": -7,
                  "tension": -5, "drama": -3, "villain": -5, "sad": -6, "sad_stop": -6, "action": -5, "lesson": -8,
                  "punch_quiet": -8, "end": -3, "silence": 0}
    xf = int(0.12 * SR)
    for (ta, name), (tb, _) in zip(segs, segs[1:]):
        d = tb - ta + 0.15
        x = S.MUSIC[name](d)
        x = x / (np.abs(x).max() + 1e-9) * 0.7 * db(music_gain[name])
        if name == "sad_stop":   # hard stop (the joke needs dead air)
            x[-int(0.15 * SR):] = 0
        else:
            x[:xf] *= np.linspace(0, 1, xf)
            x[-xf:] *= np.linspace(1, 0, xf)
        S.place(mus, x, ta, 1.0)
    # ---- ducking: music dips under dialogue
    env = np.abs(dia)
    k = int(0.05 * SR)
    env = np.convolve(env, np.ones(k) / k, mode="same")
    env = np.convolve((env > 0.02).astype(float), np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
    mus *= 1 - 0.55 * np.clip(env, 0, 1)
    sfx_s = sfx * 0.9
    dia_s = dia * 1.0
    mix = dia_s + mus + sfx_s
    peak = np.abs(mix).max()
    mix = np.tanh(mix / max(peak, 1e-6) * 1.2) * 0.95
    # stereo: dialogue center, music slightly widened via Haas
    d = int(0.012 * SR)
    musL = mus
    musR = np.concatenate([np.zeros(d), mus[:-d]])
    L = dia_s + musL + sfx_s
    R = dia_s + musR + sfx_s
    st = np.stack([L, R], 1)
    st = np.tanh(st / (np.abs(st).max() + 1e-9) * 1.1) * 0.9
    n = int(total_f / TL.FPS * SR)
    sf.write(os.path.join(OUT, "dialogue_stem.wav"), dia[:n], SR)
    sf.write(os.path.join(OUT, "music_stem.wav"), mus[:n], SR)
    sf.write(os.path.join(OUT, "sfx_stem.wav"), sfx[:n], SR)
    raw = os.path.join(OUT, "_mix_raw.wav")
    sf.write(raw, st[:n], SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.0:LRA=11",
                    "-ar", str(SR), os.path.join(OUT, "final_mix.wav")], check=True)
    os.remove(raw)
    print("mix written", round(n / SR, 2), "s")


if __name__ == "__main__":
    main()
