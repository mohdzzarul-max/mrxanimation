import sys,json
from faster_whisper import WhisperModel
m=WhisperModel("small",device="cpu",compute_type="int8")
import numpy as np; a=np.fromfile("a.raw",dtype=np.float32); segs,info=m.transcribe(a,language="ms",word_timestamps=True,vad_filter=False,beam_size=5)
out=[]
for s in segs:
    print(f"[{s.start:.2f}-{s.end:.2f}] {s.text}")
    for w in s.words: out.append([round(w.start,2),round(w.end,2),w.word])
json.dump(out,open("words.json","w"),ensure_ascii=False)
