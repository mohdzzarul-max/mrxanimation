"""Original procedural score for PERFUME 101 (fully owned, no third-party samples).
120 BPM (1 beat = 15 frames @30fps, 1 bar = 2 s = 60 frames). Output: 60.0 s stereo 48 kHz WAV.
Structure follows config/timeline.ts:
  0.0-3.6  hook tension (sub hit, ticking hats, rising tone)       -> record scratch + dramatic pause 3.6-6.0
  6.0-40.0 main groove (half-time trap/lo-fi, jazzy Dm9-G13-Cmaj9-Am9)
  40-50    lift (pads open, pluck motif)
  50-58    full drop + stinger, tail to 60.0
Usage: python3 compose_music.py out.wav
"""
import sys, numpy as np, wave
SR=48000; DUR=60.0; N=int(SR*DUR); BPM=120; BEAT=60/BPM; BAR=4*BEAT
rng=np.random.default_rng(7)
L=np.zeros(N); R=np.zeros(N)
def t_(d): return np.arange(int(d*SR))/SR
def add(sig,start,pan=0.0,gain=1.0):
    i=int(start*SR); 
    if i>=N: return
    s=sig[:N-i]*gain
    L[i:i+len(s)]+=s*np.sqrt(0.5*(1-pan)); R[i:i+len(s)]+=s*np.sqrt(0.5*(1+pan))
def onepole_lp(x,fc):
    a=np.exp(-2*np.pi*fc/SR); y=np.zeros_like(x); acc=0.0
    for i in range(len(x)): acc=(1-a)*x[i]+a*acc; y[i]=acc
    return y
def lp_fast(x,fc):  # vectorised-ish via lfilter replacement
    from scipy.signal import lfilter
    a=np.exp(-2*np.pi*fc/SR); return lfilter([1-a],[1,-a],x)
def hp_fast(x,fc): return x-lp_fast(x,fc)
def bp(x,lo,hi): return hp_fast(lp_fast(x,hi),lo)
def env(n,a=0.005,d=0.2,curve=1.0):
    t=np.arange(n)/SR; e=np.minimum(1,t/max(a,1e-4))*np.exp(-np.maximum(0,t-a)/d); return e**curve
def kick(d=0.45,f0=140,f1=42):
    t=t_(d); f=f1+(f0-f1)*np.exp(-t/0.045); ph=2*np.pi*np.cumsum(f)/SR
    s=np.sin(ph)*env(len(t),0.002,0.22); click=hp_fast(rng.standard_normal(len(t)),3000)*env(len(t),0.0005,0.004)*0.3
    return np.tanh(1.6*(s+click))
def snare(d=0.3):
    t=t_(d); n=bp(rng.standard_normal(len(t)),900,7000)*env(len(t),0.001,0.09)
    tone=np.sin(2*np.pi*190*t)*env(len(t),0.001,0.05)
    return 0.8*n+0.5*tone
def clap(d=0.3):
    t=t_(d); n=bp(rng.standard_normal(len(t)),1000,5000); e=np.zeros(len(t))
    for k,o in enumerate([0,0.011,0.022]): i=int(o*SR); e[i:]+=env(len(t)-i,0.0005,0.012 if k<2 else 0.12)
    return n*e*0.7
def hat(d=0.06,open_=False):
    t=t_(0.3 if open_ else d); n=hp_fast(rng.standard_normal(len(t)),7000)
    return n*env(len(t),0.0005,0.12 if open_ else 0.018)*0.5
def midi(m): return 440*2**((m-69)/12)
def ep(note,d,vel=1.0):  # FM electric piano
    t=t_(d); f=midi(note); mod=np.sin(2*np.pi*f*2*t)*2.2*np.exp(-t/0.3)
    s=np.sin(2*np.pi*f*t+mod)*env(len(t),0.004,0.9)*vel
    return s*np.minimum(1,(d-t)/0.05+0)  # release
def pad(note,d):
    t=t_(d); f=midi(note); s=sum(np.sign(np.sin(2*np.pi*f*(1+dt)*t+p))*0.33 for dt,p in [(-0.004,0),(0.0,1.3),(0.005,2.1)])
    s=lp_fast(s,1400); a=np.minimum(1,t/0.4)*np.minimum(1,(d-t)/0.5); return s*a
def bass(note,d):
    t=t_(d); f=midi(note); s=np.sin(2*np.pi*f*t)+0.25*np.sin(2*np.pi*2*f*t)
    return np.tanh(1.4*s)*env(len(t),0.004,d*0.9)*np.minimum(1,(d-t)/0.03)
def pluck(note,d=0.25):
    t=t_(d); f=midi(note); s=(2*((f*t)%1)-1); s=lp_fast(s,2500)*env(len(t),0.002,0.11)
    return s
# chord voicings (MIDI)
CH=[('D',[50,57,60,64,65],38),('G',[55,59,62,65,69],43),('C',[48,55,59,62,64],36),('A',[45,55,60,64,67],33)]
def bar_t(b): return b*BAR
# ---------- HOOK 0-3.6 ----------
add(kick(0.9,90,32),0.0,gain=1.0)                                    # slam sub hit
for i in range(14): add(hat(),0.25*i+0.1,pan=0.3*((-1)**i),gain=0.25+0.03*i)   # nervous ticking
t=t_(3.4); rise=np.sin(2*np.pi*np.cumsum(220+500*(t/3.4)**2)/SR)*np.minimum(1,t/2)*0.12
add(lp_fast(rise,3000),0.15)
add(kick(),1.5,gain=0.7); add(kick(),2.25,gain=0.7); add(clap(),2.5,gain=0.5); add(kick(),3.0,gain=0.8)
# ---------- MAIN GROOVE 6-40 (+ variations) ----------
def groove(b, density=1.0, lift=False, drop=False):
    t0=bar_t(b); name,ch,root=CH[b%4]
    # drums half-time: kick 1, (and of 2), snare on 3
    add(kick(),t0,gain=0.9); add(kick(),t0+1.5*BEAT,gain=0.6)
    if b%2==1: add(kick(),t0+2.75*BEAT,gain=0.5)
    add(snare(),t0+2*BEAT,gain=0.55); add(clap(),t0+2*BEAT,gain=0.45)
    for k in range(8):
        if density<1 and k%2: continue
        add(hat(),t0+k*BEAT/2,pan=0.25,gain=0.18 if k%2 else 0.26)
    if drop:
        for k in range(16): add(hat(),t0+k*BEAT/4,pan=-0.25,gain=0.08)
        add(hat(open_=True),t0+3.5*BEAT,gain=0.15)
    # bass
    add(bass(root,BEAT*1.4),t0,gain=0.55); add(bass(root,BEAT*0.4),t0+1.5*BEAT,gain=0.45)
    add(bass(root+7 if b%2 else root+12,BEAT*0.9),t0+3*BEAT,gain=0.4)
    # keys
    for j,n in enumerate(ch): add(ep(n,BEAT*1.8,0.55),t0+0.01*j,pan=(j-2)*0.15,gain=0.10)
    for j,n in enumerate(ch[1:]): add(ep(n,BEAT*0.5,0.4),t0+2.5*BEAT+0.008*j,pan=(j-2)*0.15,gain=0.07)
    if lift or drop:
        for n in ch[1:]: add(pad(n+12,BAR),t0,gain=0.035)
for b in range(3,20): groove(b, density=0.6 if b<4 else 1.0)
# playful pluck motif bars 7.5-20 (factors/claims), sparse
motif=[(0,72),(0.5,74),(1.0,76),(1.75,79),(2.5,76),(3.0,74)]
for b in [8,10,12,14,16,18]:
    for off,n in motif: add(pluck(n),bar_t(b)+off*BEAT,pan=0.35,gain=0.10)
# ---------- LIFT 40-50 ----------
for b in range(20,25): groove(b,lift=True)
for b in [21,23]:
    for off,n in motif: add(pluck(n+12),bar_t(b)+off*BEAT,pan=-0.35,gain=0.08)
t=t_(2.0); sw=hp_fast(rng.standard_normal(len(t)),800)*(t/2.0)**2*0.15; add(lp_fast(sw,6000),48.0)  # riser into CTA
# ---------- DROP 50-58 ----------
add(kick(0.9,100,34),50.0,gain=1.0)
for b in range(25,29): groove(b,drop=True)
# final stinger 58.0 + tail
add(kick(0.9,100,30),58.0,gain=1.0)
for j,n in enumerate([50,57,62,65,69,72]): add(ep(n,2.0,0.7),58.0+0.015*j,pan=(j-3)*0.12,gain=0.12)
for n in [62,69,74]: add(pad(n,2.0),58.0,gain=0.05)
# ---------- master ----------
mix=np.stack([L,R],1)
# kick-style sidechain pump on keys/pads approx: gentle global pump on beats from 6s
pump=np.ones(N); 
for b in np.arange(6.0,58.0,BEAT):
    i=int(b*SR); n=int(0.18*SR); pump[i:i+n]*=1-0.25*np.exp(-np.arange(n)/SR/0.06)[:N-i]
mix*=pump[:,None]
# silence the dramatic pause (3.75-5.9) except tail decay
fade=np.ones(N); a=int(3.7*SR); b_=int(3.85*SR); fade[a:b_]=np.linspace(1,0,b_-a); fade[b_:int(5.95*SR)]=0
mix*=fade[:,None]
mix=np.tanh(mix*1.2)/np.tanh(1.2)
peak=np.abs(mix).max(); mix=mix/peak*0.89
# end fade last 0.4s
n=int(0.4*SR); mix[-n:]*=np.linspace(1,0,n)[:,None]
out=(mix*32767).astype(np.int16)
with wave.open(sys.argv[1],'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
print('wrote',sys.argv[1],len(out)/SR,'s')
