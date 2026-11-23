"""Cut the official Mr X expression poses (ref_mrx_poses.png) into alpha sprites + head-circle metadata.
Segmentation at native res (white sticker outline -> flood from box border -> largest region), applied to the 4x upscale."""
from PIL import Image, ImageFilter; import numpy as np, json
from scipy import ndimage as ndi
Image.MAX_IMAGE_PIXELS=None
NAT=np.array(Image.open('ref_mrx_poses.png').convert('RGB')).astype(int)
UP=np.array(Image.open('up/ref_mrx_poses@4x.png').convert('RGB'))
BOX={'gembira':(30,15,405,650),'terkejut':(405,15,825,650),'marah':(825,15,1235,650),'malu':(100,640,610,1245),'fikir':(620,640,1215,1245)}
OUT='../public/characters/mrx/poses/'; meta={}
HEAD={'gembira':(225,168,155),'terkejut':(625,202,155),'marah':(1025,168,155),'malu':(360,808,155),'fikir':(820,850,162)}
for name,(x0,y0,x1,y1) in BOX.items():
    r=NAT[y0:y1,x0:x1]; mn=r.min(2); mx=r.max(2)
    # background = cream paper (+ soft brown floor shadow near the bottom); flood it from the box border
    cream=np.array([254,229,212]); d=np.sqrt(((r-cream)**2).sum(2))
    hh=r.shape[0]; yy=np.arange(hh)[:,None]
    shadow=(yy>hh*0.86)&(r[...,0]>150)&(r[...,0]-r[...,2]>15)&(r[...,0]-r[...,2]<90)&(mn<235)
    passable=(d<24)|shadow
    lab,n=ndi.label(passable); border=np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])); border=border[border>0]
    bg=np.isin(lab,border)
    f2=~bg; l,n=ndi.label(f2); sz=ndi.sum(f2,l,range(1,n+1)); nfig=ndi.binary_fill_holes(l==(np.argmax(sz)+1))
    fig=ndi.binary_opening(nfig,iterations=1)
    big=np.array(Image.fromarray((fig*255).astype('uint8')).resize(((x1-x0)*4,(y1-y0)*4),Image.BILINEAR).filter(ImageFilter.GaussianBlur(2.2)))
    ys,xs=np.where(big>127); a0,a1,b0,b1=max(0,ys.min()-6),ys.max()+7,max(0,xs.min()-6),xs.max()+7
    rgb=UP[y0*4:y1*4,x0*4:x1*4][a0:a1,b0:b1]; al=big[a0:a1,b0:b1]
    Image.fromarray(np.dstack([rgb,al])).save(OUT+name+'.png')
    # head circle: fit outer boundary near the hand-located head (native estimate below)
    ex,ey,er=HEAD[name]; ex=(ex-x0)*4-b0; ey=(ey-y0)*4-a0; er*=4
    m=al>127; edge=m&~ndi.binary_erosion(m,iterations=2)
    py,px=np.where(edge); d=np.hypot(px-ex,py-ey)
    k=(d>0.82*er)&(d<1.18*er)&(py<ey+er*0.2)
    px,py=px[k].astype(float),py[k].astype(float)
    A=np.c_[2*px,2*py,np.ones(len(px))]; bb=px**2+py**2
    cx,cy,c=np.linalg.lstsq(A,bb,rcond=None)[0]; R=float(np.sqrt(c+cx**2+cy**2))
    H,W=m.shape
    meta[name]={'w':W,'h':H,'headCx':float(cx),'headCy':float(cy),'headR':R}
    print(name,W,H,round(cx),round(cy),round(R))
json.dump(meta,open(OUT+'poses.json','w'),indent=1)
