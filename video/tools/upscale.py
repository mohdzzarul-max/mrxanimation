"""4x anime upscaler (Real-ESRGAN x4plus anime 6B, BSD-3) via onnxruntime, tiled.
Usage: python3 upscale.py in.png out.png"""
import sys, numpy as np, onnxruntime as ort
from PIL import Image
import os
M=os.path.join(os.path.dirname(os.path.abspath(__file__)),'models','realesrgan_anime6b.onnx')
so=ort.SessionOptions(); so.intra_op_num_threads=4
s=ort.InferenceSession(M,so)
def up(rgb,tile=256,pad=16):
    h,w,_=rgb.shape; out=np.zeros((h*4,w*4,3),np.float32)
    x=rgb.astype(np.float32)/255.
    for y0 in range(0,h,tile):
        for x0 in range(0,w,tile):
            y1=min(h,y0+tile); x1=min(w,x0+tile)
            py0=max(0,y0-pad); px0=max(0,x0-pad); py1=min(h,y1+pad); px1=min(w,x1+pad)
            t=x[py0:py1,px0:px1].transpose(2,0,1)[None]
            r=s.run(None,{'input':t})[0][0].transpose(1,2,0)
            oy=(y0-py0)*4; ox=(x0-px0)*4
            out[y0*4:y1*4,x0*4:x1*4]=r[oy:oy+(y1-y0)*4, ox:ox+(x1-x0)*4]
    return (np.clip(out,0,1)*255+0.5).astype(np.uint8)
if __name__=='__main__':
    im=Image.open(sys.argv[1]); 
    rgba=im.convert('RGBA'); a=np.array(rgba)
    r=up(a[:,:,:3])
    if im.mode=='RGBA':
        al=Image.fromarray(a[:,:,3]).resize((r.shape[1],r.shape[0]),Image.LANCZOS)
        Image.fromarray(np.dstack([r,np.array(al)])).save(sys.argv[2])
    else: Image.fromarray(r).save(sys.argv[2])
