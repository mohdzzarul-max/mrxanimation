"""Extract the official brush 'X' marks (face + cap) from the X-BOT hero as white alpha sprites."""
from PIL import Image, ImageFilter; import numpy as np
Image.MAX_IMAGE_PIXELS=None
im=np.array(Image.open('up/ref_xbot_hero@4x.png').convert('RGB')).astype(float)
for name,(x0,y0,x1,y1) in {'markFace':(498,588,785,800),'markCap':(575,80,735,220)}.items():
    r=im[y0*4:y1*4,x0*4:x1*4]; lum=r.mean(2); sat=r.max(2)-r.min(2)
    a=np.clip((lum-60)/150,0,1)*(sat<60)
    b=6; a[:b]=0; a[-b:]=0; a[:,:b]=0; a[:,-b:]=0
    a=np.array(Image.fromarray((a*255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.8)))
    out=np.dstack([np.full(a.shape+(3,),248,np.uint8),a])
    img=Image.fromarray(out); img=img.resize((img.width//2,img.height//2),Image.LANCZOS); img.save(f'../public/characters/xbot/{name}.png'); print(name,img.size)
# remove the cap's gloss stripe that sits left of the X
p='../public/characters/xbot/markCap.png'; c=np.array(Image.open(p)); c[:,:70,3]=0; Image.fromarray(c).save(p)
