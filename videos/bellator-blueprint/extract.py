# Extrae la geometría real de la pala (src/1.png) como trazados SVG en coordenadas de la foto.
import cv2, numpy as np, json
im=cv2.imread('src/1.png'); hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
sil=cv2.imread('assets/sil.png',0); tri=cv2.imread('assets/tri.png',0)
holes=json.load(open('assets/holes.json'))
H,S,V=hsv[...,0].astype(int),hsv[...,1].astype(int),hsv[...,2].astype(int)
lum=im.mean(2)

def smooth_d(c, sigma):
    """Contorno -> trazo suave (gaussiana circular + Catmull-Rom). sigma en px de la foto."""
    c=c.astype(float); n=len(c)
    if sigma>0 and n>8:
        k=int(3*sigma)+1; x=np.arange(-k,k+1); g=np.exp(-x*x/(2*sigma*sigma)); g/=g.sum()
        c=np.stack([np.convolve(np.r_[c[-k:,i],c[:,i],c[:k,i]],g,'valid') for i in (0,1)],1)
    step=max(1,int(round(sigma))) if sigma>0 else 1
    p=c[::step]
    if len(p)<4: p=c
    n=len(p); d=f'M{p[0][0]:.2f},{p[0][1]:.2f}'
    for i in range(n):
        p0,p1,p2,p3=p[i-1],p[i],p[(i+1)%n],p[(i+2)%n]
        c1=p1+(p2-p0)/6; c2=p2-(p3-p1)/6
        d+=f' C{c1[0]:.2f},{c1[1]:.2f} {c2[0]:.2f},{c2[1]:.2f} {p2[0]:.2f},{p2[1]:.2f}'
    return d+' Z'

def paths(mask, sigma=1.6, minarea=30, mode=cv2.RETR_EXTERNAL, smooth=True):
    m=mask.copy()
    if smooth:
        m=cv2.GaussianBlur(m,(5,5),0); m=(m>127).astype(np.uint8)*255
    cs,_=cv2.findContours(m,mode,cv2.CHAIN_APPROX_NONE)
    return [smooth_d(c.reshape(-1,2),sigma) for c in cs if cv2.contourArea(c)>=minarea]

# 1) silueta exterior: cabeza+garganta (y<752) y mango por separado
head=sil.copy(); head[752:]=0
handle=sil.copy(); handle[:748]=0
# quitar cordón: el mango es la franja central x 370-432
hm=np.zeros_like(handle); hm[:, 372:430]=255; grip=cv2.bitwise_and(handle,hm); grip[905:]=0
strap=handle.copy(); strap[:, 372:430]=0; strap[:880]=0
# 2) zona negra de la cara (carbono + oro), límite con la garganta blanca
face=((sil>0)&((lum<120)|((H>=5)&(H<=30)&(S>60)))).astype(np.uint8)*255
face[650:]=0
face=cv2.morphologyEx(face,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
n,lab,st,_=cv2.connectedComponentsWithStats(face); k=1+np.argmax(st[1:,4]); face=((lab==k)*255).astype(np.uint8)
ff=face.copy(); cv2.floodFill(ff,None,(0,0),255); face=face|cv2.bitwise_not(ff)
# 3) oro: manchas del sol (y<600) y puente (y>600)
gold=((sil>0)&(H>=5)&(H<=30)&(S>70)&(V>90)).astype(np.uint8)*255
gold=cv2.morphologyEx(gold,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
sun=gold.copy(); sun[:318]=0; sun[580:]=0
gfrac=[]
for hx_,hy_,hr_ in holes:
    ring=np.zeros_like(sun); cv2.circle(ring,(int(round(hx_)),int(round(hy_))),int(round(hr_+3)),255,3)
    f=(sun[ring>0]>0).mean(); gfrac.append(f)
    if f>0.4: cv2.circle(sun,(int(round(hx_)),int(round(hy_))),int(round(hr_+2)),255,-1)
sun=cv2.morphologyEx(sun,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
sun=cv2.morphologyEx(sun,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
cv2.imwrite('assets/sun.png',sun)
bridge=gold.copy(); bridge[:610]=0; bridge[760:]=0
n,lab,st,_=cv2.connectedComponentsWithStats(bridge); k=1+np.argmax(st[1:,4]); bridge=((lab==k)*255).astype(np.uint8)
bf=bridge.copy(); cv2.floodFill(bf,None,(0,0),255); bridge=bridge|cv2.bitwise_not(bf)
# 4) texto BELLATOR (blanco sobre carbono)
txt=((sil>0)&(lum>150)&(S<60)).astype(np.uint8)*255; txt[:290]=0; txt[328:]=0; txt[:, :270]=0; txt[:, 520:]=0
# 5) logo PADEL LOBB (oro pequeño)
logo=gold.copy(); logo[:585]=0; logo[612:]=0

P={
 'head':paths(head,sigma=2.0,minarea=500),
 'grip':paths(grip,sigma=2.0,minarea=200),
 'strap':paths(strap,sigma=2.0,minarea=40),
 'face':paths(face,sigma=2.0,minarea=500),
 'sun':paths(sun,sigma=1.6,minarea=60,mode=cv2.RETR_CCOMP),
 'bridge':paths(bridge,sigma=2.0,minarea=200),
 'tri':paths(tri,sigma=2.0,minarea=200),
 'text':paths(txt,sigma=0.9,minarea=6,smooth=False,mode=cv2.RETR_CCOMP),
 'logo':paths(logo,sigma=0.7,minarea=3,smooth=False,mode=cv2.RETR_CCOMP),
 'holes':holes,
}
ys,xs=np.nonzero(sil)
P['bbox']=[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]
# eje de simetría: centro de la cabeza en la fila más ancha
w=[(np.nonzero(head[y])[0]) for y in range(283,752)]
wid=[(a.max()-a.min()) if len(a) else 0 for a in w]; yi=int(np.argmax(wid)); a=w[yi]
P['widest']=[int(a.min()),int(283+yi),int(a.max())]
gx=np.nonzero(grip)[1]; P['axis']=float((a.min()+a.max())/2); P['gripx']=[int(gx.min()),int(gx.max())]
gy=np.nonzero(grip)[0]; P['gripy']=[int(gy.min()),int(gy.max())]
P['topy']=int(ys.min())
json.dump(P,open('assets/geometry.json','w'))
for k,v in P.items(): print(k, len(v) if isinstance(v,list) else v)
print(P['widest'],P['axis'],P['gripx'],P['gripy'])

# círculo de construcción ajustado al arco superior real de la cabeza
cs,_=cv2.findContours(head,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
pts=max(cs,key=cv2.contourArea).reshape(-1,2).astype(float)
pts=pts[pts[:,1]<430]
A=np.c_[2*pts[:,0],2*pts[:,1],np.ones(len(pts))]; b=(pts**2).sum(1)
cx,cy,c=np.linalg.lstsq(A,b,rcond=None)[0]; r=np.sqrt(c+cx*cx+cy*cy)
P['arc']=[float(cx),float(cy),float(r)]
print('arc',P['arc'])
json.dump(P,open('assets/geometry.json','w'))

# vértices del hueco triangular del corazón
t=cv2.imread('assets/tri.png',0); cs,_=cv2.findContours(t,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
c=max(cs,key=cv2.contourArea); tv=cv2.approxPolyDP(c,0.08*cv2.arcLength(c,True),True).reshape(-1,2)
P['triv']=tv.tolist(); print('triv',P['triv'])
json.dump(P,open('assets/geometry.json','w'))
open('assets/geo.js','w').write('window.GEO='+json.dumps(P)+';')
