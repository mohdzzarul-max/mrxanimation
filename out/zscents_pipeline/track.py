import cv2,numpy as np,json
cap=cv2.VideoCapture('/root/.claude/uploads/6372891a-b8b6-550d-800d-91a8e1dbdf79/f44b129d-lv_0_20261123210257.mp4')
res=[];i=0
while True:
    ok,f=cap.read()
    if not ok: break
    f=cv2.flip(f,1)
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV); hsv[:950]=0
    m=((hsv[...,0]<22)&(hsv[...,1]>140)&(hsv[...,2]>110)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    n,l,st,cen=cv2.connectedComponentsWithStats(m)
    if n>1:
        k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
        if a>1500:
            g=cv2.cvtColor(f[y:y+h,x:x+w],cv2.COLOR_BGR2GRAY)
            sh=cv2.Laplacian(g,cv2.CV_64F).var()
            res.append([i,int(x),int(y),int(w),int(h),int(a),round(sh,1)]); i+=1; continue
    res.append([i,None]); i+=1
json.dump(res,open('track.json','w'))
for r in res:
    if r[1] is not None and r[0]%3==0: print(r)
