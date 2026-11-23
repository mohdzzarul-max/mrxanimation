"""Cut sticker-outlined sprites from the official combined design sheet (4x upscaled).
Per box: white sticker outline -> flood from box border -> largest enclosed region."""
from PIL import Image, ImageFilter; import numpy as np, json
from scipy import ndimage as ndi
Image.MAX_IMAGE_PIXELS=None
im=np.array(Image.open('up/ref_combined_sheet@4x.png').convert('RGB')).astype(int)
NAT=np.array(Image.open('ref_combined_sheet.png').convert('RGB')).astype(int)
BOX={ # native coords on ref_combined_sheet.png
 'poses/thumb_chin':(192,82,448,538),'poses/hold_perfume':(30,598,200,832),
 'poses/headphones_point':(618,598,792,830),
 'heads/biasa':(452,452,535,532),'heads/gembira':(538,452,620,532),'heads/terkejut':(622,452,705,532),
 'heads/marah':(707,452,790,532),'heads/malu':(793,452,872,532),'heads/fikir':(876,452,958,532),
}
meta={}
for name,(x0,y0,x1,y1) in BOX.items():
    r=im[y0*4:y1*4,x0*4:x1*4]
    nr=NAT[y0:y1,x0:x1]; mn=nr.min(2); mx=nr.max(2)
    white=(mn>170)&((mx-mn)<55)
    best=None
    for it in (1,2,3,4,5,6):
        w=ndi.binary_closing(white,structure=ndi.generate_binary_structure(2,2),iterations=it)
        w[:it+1]=False; w[-it-1:]=False; w[:,:it+1]=False; w[:,-it-1:]=False
        lab,n=ndi.label(~w); border=np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]]))
        f=~np.isin(lab,border); l,n=ndi.label(f)
        if n==0: continue
        sz=ndi.sum(f,l,range(1,n+1)); f=ndi.binary_fill_holes(l==(np.argmax(sz)+1))
        if f.sum()>0.25*f.size: best=f; break
        if best is None or f.sum()>best.sum(): best=f
    print(name,it,round(best.sum()/best.size,2))
    nfig=best
    if name.startswith('heads/'):
        # thin outlines leak: fit a circle to the white outline ring instead
        ys,xs=np.where((mn>200)&((mx-mn)<40))
        A_=np.c_[2*xs,2*ys,np.ones(len(xs))]; bb=xs**2+ys**2
        for _ in range(3):
            cx,cy,c=np.linalg.lstsq(A_,bb,rcond=None)[0]; R=np.sqrt(c+cx**2+cy**2)
            d=np.abs(np.hypot(xs-cx,ys-cy)-R); keep=d<np.percentile(d,60); A_,bb,xs,ys=A_[keep],bb[keep],xs[keep],ys[keep]
        yy,xx=np.mgrid[0:nr.shape[0],0:nr.shape[1]]; nfig=np.hypot(xx-cx,yy-cy)<R+1.8
        print(name,'circle',round(cx,1),round(cy,1),round(R,1))
    fig=np.array(Image.fromarray((nfig*255).astype('uint8')).resize((r.shape[1],r.shape[0]),Image.BILINEAR).filter(ImageFilter.GaussianBlur(2)))>127
    ys,xs=np.where(fig); a0,a1,b0,b1=max(0,ys.min()-4),ys.max()+5,max(0,xs.min()-4),xs.max()+5
    al=np.array(Image.fromarray((fig*255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.4)))
    out=np.dstack([r[a0:a1,b0:b1].astype('uint8'),al[a0:a1,b0:b1]])
    import os; os.makedirs(os.path.dirname('../public/characters/mrx/'+name),exist_ok=True)
    Image.fromarray(out).save('../public/characters/mrx/'+name+'.png'); meta[name]=out.shape[:2]
print(meta)
# brand wordmark (white on dark): luminance -> alpha
r=im[8*4:86*4,95*4:515*4].astype(float); lum=r.mean(2); sat=r.max(2)-r.min(2)
a=np.clip((lum-70)/150,0,1); a[sat>60]=0
out=np.dstack([np.full(a.shape+(3,),246,np.uint8),(a*255).astype('uint8')])
Image.fromarray(out).save('../public/brand/experimental_wordmark.png'); print('logo',out.shape)
