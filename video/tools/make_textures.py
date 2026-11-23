"""Procedural print textures (owned): dark comic paper, cream paper, grain overlay. Deterministic."""
import numpy as np
from PIL import Image, ImageFilter
rng=np.random.default_rng(11); W,H=1080,1920
def fbm(w,h,oct=5,base=8):
    out=np.zeros((h,w))
    for o in range(oct):
        s=base*2**o; n=rng.random((h//s+2,w//s+2))
        im=Image.fromarray((n*255).astype('uint8')).resize((w+ (s), h+(s)),Image.BICUBIC).crop((0,0,w,h))
        out+=np.array(im)/255/(2**o)
    return out/out.max()
n=fbm(W,H,6,4); fib=np.array(Image.fromarray((rng.random((H,W))*255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.6)))/255
# dark paper
d=20+n*14+fib*6; dark=np.dstack([d,d*0.97,d*1.04]); Image.fromarray(np.clip(dark,0,255).astype('uint8')).save('public/textures/paper_dark.jpg',quality=92)
# cream paper
c=np.dstack([239-n*22-fib*10,230-n*24-fib*10,212-n*28-fib*10]); Image.fromarray(np.clip(c,0,255).astype('uint8')).save('public/textures/paper_cream.jpg',quality=92)
# grain overlay (transparent, for multiply-ish over everything)
g=rng.normal(0,1,(H//2,W//2)); g=(g-g.min())/(g.max()-g.min())
a=(np.abs(g-0.5)*2)**2*70
Image.fromarray(np.dstack([np.full_like(g,0)+(g>0.5)*255,(g>0.5)*255,(g>0.5)*255,a]).astype('uint8')).resize((W,H)).save('public/textures/grain.png')
print('ok')
