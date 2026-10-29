import cv2, numpy as np, json
im=cv2.imread('src/1.png'); sil=cv2.imread('assets/sil.png',0)
hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
lum=im.mean(2); sat=hsv[...,1]
cand=((sil>0)&(sat<40)&(lum>150)).astype(np.uint8)
cand[:318]=0; cand[600:]=0
n,lab,st,cen=cv2.connectedComponentsWithStats(cand,connectivity=4)
out=np.zeros_like(sil); holes=[]
for i in range(1,n):
    x,y,ww,hh,a=st[i]
    if a<25 or a>260: continue
    if max(ww,hh)/max(1,min(ww,hh))>1.6: continue
    comp=(lab==i).astype(np.uint8)
    comp=cv2.dilate(comp,np.ones((3,3),np.uint8))
    out[comp>0]=255
    holes.append([float(cen[i][0]),float(cen[i][1]),float((ww+hh)/4+0.5)])
# triangle opening
d=np.abs(im.astype(int)-np.array([231,229,229])).max(2)
c2=((sil>0)&(d<=12)).astype(np.uint8); c2[:620]=0; c2[720:]=0
n2,lab2,st2,_=cv2.connectedComponentsWithStats(c2,connectivity=4)
k=1+np.argmax(st2[1:,4]); tri=(lab2==k).astype(np.uint8)*255
tri=cv2.morphologyEx(tri,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
print(len(holes),'holes; tri',st2[k])
cv2.imwrite('assets/holes.png',out); cv2.imwrite('assets/tri.png',tri)
alpha=sil.copy(); alpha[out>0]=0; alpha[tri>0]=0
alpha=cv2.GaussianBlur(alpha,(3,3),0)
cv2.imwrite('assets/alpha.png',alpha)
rgba=cv2.cvtColor(im,cv2.COLOR_BGR2BGRA); rgba[...,3]=alpha
cv2.imwrite('assets/racket_cut.png',rgba)
json.dump(holes,open('assets/holes.json','w'))
r=rgba; a=r[...,3:4]/255.; bg=np.zeros_like(r[...,:3]); bg[:]=(80,30,10)
o=(r[...,:3]*a+bg*(1-a)).astype(np.uint8)
cv2.imwrite('/tmp/claude-0/-home-user-PADEL-LOBB/05bc97dc-cb01-5db7-971f-ff3d5fd7f4f4/scratchpad/cut.png',cv2.resize(o[270:960,200:590],None,fx=1.4,fy=1.4))
