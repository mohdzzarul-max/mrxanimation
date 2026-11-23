"""Scratch Malay dialogue with Meta's MMS-TTS Malay voice (facebook/mms-tts-zlm).
Needs: pip install torch transformers scipy. Writes audio/*.wav (16 kHz mono).
These are placeholders: drop real voice-actor takes in audio/ with the same names and
re-run mix.py; the lip-sync envelope follows whatever is there.
Brand words are spelled phonetically so the Malay voice reads them naturally."""
import numpy as np, torch, scipy.io.wavfile as w
from transformers import VitsModel, AutoTokenizer
m = VitsModel.from_pretrained("facebook/mms-tts-zlm"); tok = AutoTokenizer.from_pretrained("facebook/mms-tts-zlm")
SR = m.config.sampling_rate

def say(text, seed, rate=1.0):
    torch.manual_seed(seed); m.noise_scale = 0.5; m.speaking_rate = rate
    with torch.no_grad(): a = m(**tok(text, return_tensors="pt")).waveform[0].numpy()
    i = np.where(np.abs(a) > 0.02)[0]
    return a[max(0, i[0] - 160): i[-1] + 400]

gap = lambda s: np.zeros(int(SR * s), np.float32)
LINES = {
    # "Weh! ZSCENTS tengah CLEARANCE!"  ("Weh!" voiced on its own so it lands as an exclamation)
    "mrx_l1": np.concatenate([say("weh!", 3, 1.1), gap(0.15), say("zed sens tengah kliarens!", 21)]),
    # "Korang kena tengok offer kali ni!"
    "mrx_l2": say("korang kena tengok, offer kali ni!", 7),
    # "MR X!!"  (X-BOT; robot treatment is applied in mix.py)
    "xbot_l3": say("mister eks!", 7, 1.1),
}
for name, a in LINES.items():
    w.write(f"audio/{name}.wav", SR, a.astype(np.float32))
    print(name, round(len(a) / SR, 2), "s")
