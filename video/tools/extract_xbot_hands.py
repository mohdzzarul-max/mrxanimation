"""Extract X-BOT glove sprites from the official X-BOT sheet 'Hands' layer assets (4x upscaled).
White glove pixels -> mask; dilate to rebuild the black ink outline + white sticker outline (hero style)."""
from PIL import Image, ImageFilter; import numpy as np
from scipy import ndimage as ndi
Image.MAX_IMAGE_PIXELS=None
im=np.array(Image.open('up/ref_xbot_sheet@4x.png').convert('RGB')).astype(int)
x0,y0,x1,y1=480*4,1458*4,625*4,1575*4
reg=im[y0:y1,x0:x1]; lum=reg.mean(2)
glove=lum>95
glove=ndi.binary_closing(glove,iterations=3); glove=ndi.binary_fill_holes(glove)
lab,n=ndi.label(glove); sz=ndi.sum(glove,lab,range(1,n+1))
objs=[(i+1,ndi.find_objects((lab==i+1).astype(np.int32))[0]) for i,s in enumerate(sz) if s>3000]
objs.sort(key=lambda o:(o[1][0].start//150,o[1][1].start))
res=[]
for k,(i,sl) in enumerate(objs):
    m=lab==i
    ink=ndi.binary_dilation(m,iterations=9); stick=ndi.binary_dilation(ink,iterations=9)
    ys,xs=np.where(stick); a0,a1,b0,b1=ys.min()-3,ys.max()+4,xs.min()-3,xs.max()+4
    out=np.zeros((a1-a0,b1-b0,4),np.uint8)
    sub=lambda arr: arr[a0:a1,b0:b1]
    out[sub(stick)]=[255,255,255,255]
    out[sub(ink)]=[8,8,10,255]
    # inside glove keep original pixels but restore line art (dark lines inside glove are original)
    g=sub(m); out[g,:3]=np.clip(sub(reg)[g],0,255); out[g,3]=255
    al=Image.fromarray(out[:,:,3]).filter(ImageFilter.GaussianBlur(1.2)); out[:,:,3]=np.array(al)
    Image.fromarray(out).save(f'cut/xbot_hand_{k}.png'); res.append((k,sl,out.shape))
print(res)
