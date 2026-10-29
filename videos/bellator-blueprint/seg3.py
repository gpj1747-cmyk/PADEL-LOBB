import cv2, numpy as np
im=cv2.imread('src/1.png'); m=cv2.imread('assets/mask_raw.png',0); h,w=m.shape
YH=752
top=np.zeros_like(m); top[:YH]=m[:YH]
# only the main component pixels
pts=cv2.findNonZero(top)
hull=cv2.convexHull(pts)
sil=np.zeros_like(m); cv2.fillPoly(sil,[hull],255)
sil[YH:]=0
low=m.copy(); low[:YH-4]=0
n,lab,st,_=cv2.connectedComponentsWithStats(low)
for i in range(1,n):
    if st[i,4]>200: sil[lab==i]=255
sil=cv2.morphologyEx(sil,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
cv2.imwrite('assets/sil.png',sil)
v=im.copy(); v[sil==0]=(v[sil==0]*0.3+np.array([200,0,200])*0.7).astype(np.uint8)
cv2.imwrite('/tmp/claude-0/-home-user-PADEL-LOBB/05bc97dc-cb01-5db7-971f-ff3d5fd7f4f4/scratchpad/segv.png',v[260:980,190:620])
