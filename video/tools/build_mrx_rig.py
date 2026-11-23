"""Builds Mr X cut-out rig layers from the 4x-upscaled official front turnaround.
Each layer is cropped to its bbox; offsets + pivots go to rig.json (coords in the 4x canvas space)."""
from PIL import Image, ImageDraw, ImageFilter; import numpy as np, json
from scipy import ndimage as ndi
SRC='cut/mrx_front@4x.png'; OUT='../public/characters/mrx/'
im=np.array(Image.open(SRC)); H,W=im.shape[:2]
rgb=im[:,:,:3].astype(int); A=im[:,:,3]
def poly(pts):
    m=Image.new('L',(W,H),0); ImageDraw.Draw(m).polygon([tuple(p) for p in pts],fill=255)
    return np.array(m)>127
def smooth(mask,r=1.2): return np.array(Image.fromarray((mask*255).astype('uint8')).filter(ImageFilter.GaussianBlur(r)))
# ---- head: above a curve along the chin
xs=np.arange(W); chin=np.where(xs<450,1322,np.where(xs>945,1322, 1322+98*np.sin(np.pi*np.clip((xs-450)/(945-450),0,1))))
yy=np.arange(H)[:,None]; head=(yy<chin[None,:])
# ---- arms
armL=poly([(196,1585),(290,1592),(432,1652),(416,1760),(391,1850),(381,1960),(373,2030),(331,2100),(270,2128),(176,2112),(108,2060),(88,1960),(104,1840),(156,1716)])
armR=poly([(976,1668),(1112,1598),(1192,1598),(1262,1760),(1304,1900),(1304,2040),(1244,2114),(1130,2134),(1068,2092),(1040,2000),(1020,1900),(1000,1790)])
sleeveL=poly([(150,1440),(430,1420),(470,1560),(440,1690),(415,1688),(290,1626),(205,1606),(170,1600)])
sleeveR=poly([(960,1420),(1230,1440),(1215,1590),(1178,1612),(1112,1628),(984,1694),(955,1690),(930,1560)])
fig=A>8
armL&=fig; armR&=fig
body=fig&~head&~(armL&~sleeveL)&~(armR&~sleeveR)
lb,nb=ndi.label(body); szb=ndi.sum(body,lb,range(1,nb+1)); body=lb==(np.argmax(szb)+1)
layers={}
def save(name,mask,rgbarr=None,pad=4):
    ys,xs_=np.where(mask); y0,y1,x0,x1=max(0,ys.min()-pad),min(H,ys.max()+pad+1),max(0,xs_.min()-pad),min(W,xs_.max()+pad+1)
    src=rgb if rgbarr is None else rgbarr
    a=np.minimum(smooth(mask,0.8),A) if name!='body' else np.minimum(smooth(mask,0.8),np.maximum(A,smooth(mask,0.8)))
    out=np.dstack([src[y0:y1,x0:x1].astype('uint8'),a[y0:y1,x0:x1]])
    Image.fromarray(out).save(OUT+name+'.png'); layers[name]={'x':int(x0),'y':int(y0),'w':int(x1-x0),'h':int(y1-y0)}
# body: fill a collar/neck underlay behind the head so head tilt never shows holes
under=poly([(420,1180),(944,1180),(990,1330),(930,1460),(682,1500),(430,1460),(375,1330)])
brgb=rgb.copy(); fillc=np.array([30,29,36])
add=under&~body
brgb[add]=fillc
# fill arm holes inside silhouette (where arms leave the torso) with torso dark edge: just leave transparent
save('body',body|add,brgb)
save('head',head&fig)
save('armL',armL); save('armR',armR)
save('sleeveL',sleeveL&fig&~head); save('sleeveR',sleeveR&fig&~head)
# ---- eyes: find blue iris blobs & eye openings (skin/white/blue region) in head
r,g,b=rgb[...,0],rgb[...,1],rgb[...,2]
blue=(b>150)&(b>r+60)&head
skin=(r>200)&(g>140)&(b>100)&(r>b+35)&head
white=(r>225)&(g>225)&(b>225)
lab,n=ndi.label(blue); sz=ndi.sum(blue,lab,range(1,n+1)); big=np.argsort(sz)[-2:]+1
eyes=[]
for k in big:
    ys,xs_=np.where(lab==k); cx,cy=xs_.mean(),ys.mean()
    # opening: skin+blue+white near iris
    box=np.zeros_like(blue); box[int(cy-170):int(cy+150),int(cx-190):int(cx+190)]=True
    op=(skin|blue|(white&box))&box
    op=ndi.binary_closing(op,iterations=6); l2,n2=ndi.label(op); s2=ndi.sum(op,l2,range(1,n2+1)); op=l2==(np.argmax(s2)+1)
    oy,ox=np.where(op)
    eyes.append({'irisCx':float(cx),'irisCy':float(cy),'irisR':float(np.sqrt(len(xs_)/np.pi)),'x0':int(ox.min()),'x1':int(ox.max()),'y0':int(oy.min()),'y1':int(oy.max())})
eyes.sort(key=lambda e:e['irisCx'])
rig={'canvas':{'w':W,'h':H},'scale':4,'layers':layers,
 'pivots':{'head':[682,1400],'armL':[330,1636],'armR':[1048,1650],'body':[682,2780],'neck':[682,1420]},'eyes':eyes,
 'source':'assets-src/ref_mrx_turnaround.png (official front view) upscaled 4x'}
json.dump(rig,open(OUT+'rig.json','w'),indent=1); print(json.dumps(rig,indent=1))
