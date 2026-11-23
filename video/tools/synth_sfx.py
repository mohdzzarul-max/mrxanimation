"""Original synthesized SFX (owned). python3 synth_sfx.py <outdir> [music.wav for scratch source]"""
import sys, numpy as np, wave, os
from scipy.signal import lfilter
SR=48000; rng=np.random.default_rng(3); OUT=sys.argv[1]
def lp(x,fc): a=np.exp(-2*np.pi*fc/SR); return lfilter([1-a],[1,-a],x)
def hp(x,fc): return x-lp(x,fc)
def t_(d): return np.arange(int(d*SR))/SR
def save(name,x,st=False):
    x=np.asarray(x,float); x=x/(np.abs(x).max()+1e-9)*0.9
    if x.ndim==1: x=np.stack([x,x],1)
    with wave.open(os.path.join(OUT,name+'.wav'),'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x*32767).astype(np.int16).tobytes())
# paper rip: crackly bandpassed noise with jagged AM, rising brightness
t=t_(0.55); n=rng.standard_normal(len(t)); am=(rng.random(len(t))<0.08).astype(float); am=lp(am,180)*6
br=hp(lp(n,5000),500)*(0.5+t/0.55); e=np.minimum(1,t/0.02)*np.exp(-np.maximum(0,t-0.35)/0.06)
save('paper_rip',br*(0.4+am)*e)
# page flip: swish with flutter
t=t_(0.4); n=rng.standard_normal(len(t)); fl=0.6+0.4*np.sin(2*np.pi*(18+30*t)*t)
e=np.sin(np.pi*np.minimum(1,t/0.4))**2; save('page_flip',hp(lp(n,4500),700)*fl*e)
# record scratch: backwards-forwards pitched noise + tone sweep
t=t_(0.6); rate=np.sin(2*np.pi*3.2*t)*np.exp(-t/0.5); ph=np.cumsum(300+900*rate)/SR
s=np.sign(np.sin(2*np.pi*ph))*0.4+lp(rng.standard_normal(len(t)),3000)*np.abs(rate)
save('record_scratch',hp(lp(s,5000),200)*np.minimum(1,t/0.01)*np.exp(-np.maximum(0,t-0.45)/0.05))
# bot chirps (X-BOT voice-ish beeps), 3 variants
for k,(f0,f1,d) in enumerate([(900,1500,0.12),(1400,700,0.14),(800,1200,0.09)]):
    t=t_(d*3); seg=np.zeros(len(t)); i=0
    for j in range(3):
        tt=t_(d); f=f0+(f1-f0)*(tt/d)*(1 if j%2==0 else -0.5); ph=2*np.pi*np.cumsum(f)/SR
        s=np.sign(np.sin(ph))*0.3+np.sin(ph)*0.7; s*=np.sin(np.pi*tt/d)**0.5
        seg[i:i+len(s)]+=s[:len(seg)-i]; i+=int(d*SR*0.85)
    save(f'bot_chirp_{k+1}',lp(seg,6000))
# servo: buzzy short motor whirr
t=t_(0.25); f=180+120*np.sin(np.pi*t/0.25); s=np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))*np.sin(np.pi*t/0.25)
save('servo',lp(s,2500)*0.6)
# cash register "ka-ching": click + bell partials
t=t_(1.2); bell=sum(a*np.sin(2*np.pi*f*t)*np.exp(-t/dc) for f,a,dc in [(2093,1,0.5),(2637,0.6,0.4),(3136,0.5,0.35),(4186,0.3,0.25),(5274,0.2,0.2)])
clk=hp(rng.standard_normal(len(t)),2000)*np.exp(-t/0.01); s=np.zeros(len(t)); s+=clk*0.6
i=int(0.07*SR); s[i:]+=bell[:len(t)-i]*0.5; save('ka_ching',s)
# stamp thud
t=t_(0.35); f=120*np.exp(-t/0.05)+60; s=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/0.09)+lp(rng.standard_normal(len(t)),1500)*np.exp(-t/0.02)*0.6
save('stamp',np.tanh(2*s))
# marker squeak/swipe (for red marks)
t=t_(0.28); f=1800+600*np.sin(2*np.pi*7*t); s=np.sin(2*np.pi*np.cumsum(f)/SR)*0.25+hp(lp(rng.standard_normal(len(t)),6000),1500)*0.5
save('marker',s*np.sin(np.pi*t/0.28))
# soft tick (UI)
t=t_(0.06); save('tick',np.sin(2*np.pi*2400*t)*np.exp(-t/0.008)+hp(rng.standard_normal(len(t)),4000)*np.exp(-t/0.003)*0.4)
# boing (anticipation/bounce)
t=t_(0.4); f=220+260*np.exp(-t/0.12)*np.sin(2*np.pi*14*t)**2+80; save('boing',np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/0.15))
# camera-shake rumble
t=t_(0.6); save('rumble',lp(rng.standard_normal(len(t)),120)*np.exp(-t/0.2))
# spray mist
t=t_(0.7); s=hp(lp(rng.standard_normal(len(t)),9000),2500)*np.minimum(1,t/0.03)*np.exp(-np.maximum(0,t-0.3)/0.15); save('spray',s)
# gasp/pop-in "whip" (fast whoosh up)
t=t_(0.25); s=hp(lp(rng.standard_normal(len(t)),7000),300)*(0.3+(t/0.25)**2)*np.sin(np.pi*t/0.25)**2; save('whip',s)
print('ok')
