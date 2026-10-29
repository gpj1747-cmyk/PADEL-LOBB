import cv2, numpy as np
im=cv2.imread('src/1.png'); h,w=im.shape[:2]
bg=np.array([231,229,229])
d=np.abs(im.astype(int)-bg).max(2)
fgc=(d>14).astype(np.uint8)
# grabcut init
mask=np.full((h,w),cv2.GC_PR_BGD,np.uint8)
mask[d<=4]=cv2.GC_BGD
mask[d>40]=cv2.GC_FGD
mask[:, :150]=cv2.GC_BGD; mask[:, 650:]=cv2.GC_BGD; mask[:250]=cv2.GC_BGD; mask[1080:]=cv2.GC_BGD
bgm=np.zeros((1,65));fgm=np.zeros((1,65))
cv2.grabCut(im,mask,None,bgm,fgm,6,cv2.GC_INIT_WITH_MASK)
m=((mask==1)|(mask==3)).astype(np.uint8)*255
cv2.imwrite('assets/mask_raw.png',m)
ys,xs=np.nonzero(m); print(xs.min(),xs.max(),ys.min(),ys.max())
