"""X-BOT rig from the official hero render (4x upscaled). Output at 2x native scale.
Layers: cap (cap+gold neck), body (bottle, eyes removed -> vector eyes in React), shoeL/shoeR, handFist/handThumb.
Arms & legs are drawn as rubber-hose vector tubes in React (matches the design's black tube limbs)."""
from PIL import Image, ImageFilter; import numpy as np, json, cv2
from scipy import ndimage as ndi
Image.MAX_IMAGE_PIXELS=None
im=np.array(Image.open('up/ref_xbot_hero@4x.png').convert('RGBA')); H,W=im.shape[:2]
rgb=im[:,:,:3].copy(); A=im[:,:,3]
F=4  # native->4x
# silhouette at native res: white sticker outline (closed over small gaps) -> flood from border -> fill
na=np.array(Image.open('ref_xbot_hero.png')).astype(int); nrgb=na[:,:,:3]; nA=na[:,:,3]
nmn=nrgb.min(2); nmx=nrgb.max(2)
nwhite=(nmn>150)&((nmx-nmn)<60)&(nA>110)
nwhite=ndi.binary_closing(nwhite,structure=ndi.generate_binary_structure(2,2),iterations=6)
lab,n=ndi.label(~nwhite)
border=np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]]))
nfig=~np.isin(lab,border); l2,n2=ndi.label(nfig); sz=ndi.sum(nfig,l2,range(1,n2+1)); nfig=ndi.binary_fill_holes(l2==(np.argmax(sz)+1))
fig=np.array(Image.fromarray((nfig*255).astype('uint8')).resize((W,H),Image.BILINEAR).filter(ImageFilter.GaussianBlur(2)))>127
yy,xx=np.mgrid[0:H,0:W]
def P(pts):
    from PIL import ImageDraw
    m=Image.new('L',(W,H),0); ImageDraw.Draw(m).polygon([(x*F,y*F) for x,y in pts],fill=255); return np.array(m)>127
# arm regions (native coords)
armL=P([(150,515),(350,515),(352,575),(372,690),(372,880),(150,900)])
armR=P([(880,420),(1140,400),(1140,760),(985,760),(975,735),(885,735)])
# exact glove/arm pixels: within region & fig & not body. body edge columns: left ~352, right ~985
armLm=armL&fig; armRm=armR&fig
# --- repair body edges by vertical smear (columns), using rows just above the glove
def smear(x0,x1,ystop):
    for x in range(x0*F,x1*F):
        col=armRm[:,x]|armLm[:,x]
        ys=np.where(col[:ystop*F])[0]
        if len(ys)==0: continue
        top=ys.min()-8; bot=min(ys.max()+8,ystop*F)
        rgb[top:bot,x]=rgb[top-1,x]; fig[top:bot,x]=fig[top-1,x]
smear(882,990,850)
smear(330,375,872)
# remove arm pixels outside the repaired body
bodyCols=(xx>=352*F)&(xx<=990*F)
fig2=fig&~((armL|armR)&~bodyCols)
# --- remove baked eyes (amber + glow) by inpainting with face black
r,g,b=[rgb[...,i].astype(int) for i in range(3)]
eyebox=P([(430,420),(860,410),(860,600),(430,610)])
amber=eyebox&(((r>55)&(r>b+18))|(r>b+28))
amber=ndi.binary_dilation(amber,iterations=16)&eyebox
small=cv2.resize(rgb,(W//4,H//4),interpolation=cv2.INTER_AREA); msk=cv2.resize(amber.astype(np.uint8)*255,(W//4,H//4),interpolation=cv2.INTER_NEAREST)
inp=cv2.inpaint(small,msk,9,cv2.INPAINT_TELEA); inp=cv2.resize(inp,(W,H),interpolation=cv2.INTER_CUBIC)
noise=np.random.default_rng(1).normal(0,1.2,(H,W,1))
rgb[amber]=np.clip(inp[amber]*0.6+np.array([14,13,15])*0.4+noise[amber],0,255).astype(np.uint8)
# --- split: cap (y < neckcut within neck columns), body, shoes
capm=fig2&(yy<338*F)&(xx>458*F)&(xx<860*F)&~((yy>262*F)&((xx<528*F)|(xx>812*F)))
bodym=fig2&(yy>=320*F)&(yy<888*F)&~(capm&(yy<320*F))
# body top under neck: copy the top-edge column profile from just outside the neck
bodym&=~((yy<328*F)&(xx>520*F)&(xx<820*F))
for x in range(530*F,812*F):
    srcx=522*F if x<667*F else 816*F
    rgb[300*F:362*F,x]=rgb[300*F:362*F,srcx]; bodym[300*F:362*F,x]=bodym[300*F:362*F,srcx]
shoeL=fig&(yy>=905*F)&(xx<640*F); shoeR=fig&(yy>=905*F)&(xx>=640*F)
# re-ink the shoe tops (cut line) with a black band so leg tubes plug in
OUT='../public/characters/xbot/'; meta={}
def save(name,mask,blur=1.6,scale=0.5,src=None):
    ys,xs=np.where(mask); y0,y1,x0,x1=ys.min()-6,ys.max()+7,xs.min()-6,xs.max()+7
    al=np.array(Image.fromarray((mask*255).astype('uint8')).filter(ImageFilter.GaussianBlur(blur)))
    al=np.minimum(al,A)
    arr=np.dstack([(rgb if src is None else src)[y0:y1,x0:x1],al[y0:y1,x0:x1]])
    img=Image.fromarray(arr); img=img.resize((int(img.width*scale),int(img.height*scale)),Image.LANCZOS)
    img.save(OUT+name+'.png'); meta[name]={'x':x0/F,'y':y0/F,'w':(x1-x0)/F,'h':(y1-y0)/F}
save('body',bodym); save('cap',capm); save('shoeL',shoeL); save('shoeR',shoeR)
orig=im[:,:,:3]
save('handFist',armLm&(yy>655*F)&(xx<372*F),src=orig)
gl=armRm&(xx>880*F)&(orig.astype(int).mean(2)>110)
gl=ndi.binary_fill_holes(ndi.binary_closing(gl,iterations=6)); lg,ng=ndi.label(gl); sg=ndi.sum(gl,lg,range(1,ng+1)); gl=lg==(np.argmax(sg)+1)
thumb=ndi.binary_dilation(gl,iterations=26)&fig
save('handThumb',thumb,src=orig)
rig={'unit':'native px of ref_xbot_hero.png; images stored at 2x','layers':meta,
 'anchors':{'shoulderL':[352,640],'shoulderR':[985,610],'hipL':[470,880],'hipR':[800,880],'ankleL':[470,935],'ankleR':[820,935],
            'eyeL':[525,530],'eyeR':[745,512],'neckPivot':[667,330],'groundY':1088,'centerX':660},
 'source':'assets-src/ref_xbot_hero.png (official) upscaled 4x'}
json.dump(rig,open(OUT+'rig.json','w'),indent=1); print(json.dumps(meta))
