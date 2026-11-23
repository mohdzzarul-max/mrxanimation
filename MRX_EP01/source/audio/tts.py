"""Generate all dialogue with Meta MMS-TTS (Malay, facebook/mms-tts-zlm) and
shape a distinct voice per character with ffmpeg (rubberband pitch/formant,
EQ, compression; X-BOT gets a light robotic layer that keeps words clear).

Output: MRX_EP01/voices/<id>.wav (48 kHz mono) + voices/durations.json
Usage:  python3 tts.py [line_id ...]
"""
import json, os, subprocess, sys
import numpy as np, soundfile as sf, torch
from transformers import VitsModel, AutoTokenizer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from script_data import LINES, VOICES  # noqa

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "voices")
RAW = os.path.join(OUT, "raw")
os.makedirs(RAW, exist_ok=True)

FX = {
    # warm, bright young voice
    "MRX": "highpass=f=90,equalizer=f=3000:t=q:w=1:g=3,acompressor=threshold=-20dB:ratio=3:attack=5:release=80",
    # chesty older salesman: more low-mid, slight grit via mild saturation-like EQ
    "UNCLE": "highpass=f=70,equalizer=f=180:t=q:w=1:g=4,equalizer=f=2500:t=q:w=1.2:g=2,"
             "acompressor=threshold=-22dB:ratio=4:attack=5:release=120",
    # bottle sidekick: bright, slightly metallic, short comb + subtle chorus
    "XBOT": "highpass=f=150,equalizer=f=1800:t=q:w=0.8:g=4,"
            "flanger=delay=1.2:depth=1.5:regen=25:width=60:speed=0.6,"
            "aecho=0.9:0.6:9:0.25,acompressor=threshold=-20dB:ratio=4:attack=3:release=60",
}


def main(only):
    name = "facebook/mms-tts-zlm"
    model = VitsModel.from_pretrained(name)
    tok = AutoTokenizer.from_pretrained(name)
    sr = model.config.sampling_rate
    dur_path = os.path.join(OUT, "durations.json")
    durs = json.load(open(dur_path)) if os.path.exists(dur_path) else {}
    for lid, who, sub, text in LINES:
        if only and lid not in only:
            continue
        v = VOICES[who]
        model.speaking_rate = v["speaking_rate"]
        model.noise_scale = v["noise_scale"]
        torch.manual_seed(v["seed"])
        with torch.no_grad():
            w = model(**tok(text, return_tensors="pt")).waveform[0].numpy()
        w = w / (np.abs(w).max() + 1e-6) * 0.9
        raw = os.path.join(RAW, lid + ".wav")
        sf.write(raw, w, sr)
        semis = v["pitch"]
        rb = f"rubberband=pitch={2 ** (semis / 12):.4f}" + (":formant=preserved" if v["formant"] else "")
        af = f"aresample=48000,{rb},{FX[who]},silenceremove=start_periods=1:start_threshold=-45dB," \
             f"areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,loudnorm=I=-16:TP=-1.5"
        out = os.path.join(OUT, lid + ".wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", af, "-ar", "48000", "-ac", "1", out],
                       check=True)
        d = sf.info(out).duration
        durs[lid] = round(d, 3)
        print(f"{lid:20s} {who:6s} {d:5.2f}s  {sub}")
    json.dump(durs, open(dur_path, "w"), indent=1)


if __name__ == "__main__":
    main(set(sys.argv[1:]))
