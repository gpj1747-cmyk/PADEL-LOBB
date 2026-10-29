import cv2, numpy as np
im=cv2.imread('src/1.png'); m=cv2.imread('assets/mask_raw.png',0)
# width profile
for y in range(700,800,5):
    xs=np.nonzero(m[y])[0]; print(y, xs.min() if len(xs) else None, xs.max() if len(xs) else None, len(xs))
