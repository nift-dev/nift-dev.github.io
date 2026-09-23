#!/usr/bin/env python3
"""Restore the approved raster art's framing; no vector redraw or new AI assets.

Optional asset-maintenance dependencies: Pillow, numpy, opencv-python.
This uses the supplied poster as a source master for the hero and full-card
scenes, not as an image of the page. Text is removed before rendering. The
approved raster objects and illustration style are retained. Only landscape margins are extended; none of the
main glass objects are stretched, cropped off, or painted over.

The source master is deliberately not deployed by the site build.
"""
from pathlib import Path
import json
import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parent.parent
ASSETS=ROOT/'public/assets/images/about'
SOURCE=ROOT/'docs/artwork/about-poster-reference.png'

def erase_letters(im, boxes):
    arr=np.array(im.convert('RGB'))
    mask=np.zeros(arr.shape[:2],np.uint8)
    for x0,y0,x1,y1,threshold in boxes:
        patch=arr[y0:y1,x0:x1]
        letters=(patch.max(axis=2)>threshold).astype(np.uint8)*255
        letters=cv2.dilate(letters,np.ones((3,3),np.uint8),iterations=1)
        mask[y0:y1,x0:x1]=letters
    return Image.fromarray(cv2.inpaint(arr,mask,5,cv2.INPAINT_TELEA))

def expand_landscape(im, top, bottom):
    """Extend just sky / water margin, retaining every pixel of the source image."""
    arr=np.asarray(im.convert('RGB'),dtype=np.float32)
    h,w=arr.shape[:2]
    bg=np.array([2.,9.,14.])
    out=np.zeros((h+top+bottom,w,3),dtype=np.float32)
    out[top:top+h]=arr
    # Smooth horizontal edge sampling continues scenery to the image boundary.
    sky=cv2.GaussianBlur(arr[:min(3,h)].mean(axis=0)[None,:,:],(9,1),0)[0]
    for y in range(top):
        t=(y+1)/(top+1)
        out[y]=bg*(1-t)+sky*t
    # Mirror a shallow piece of the existing foreground with small ripples,
    # then fade it into the lake. A repeated edge row produces ugly vertical
    # streaks; a reflection preserves the original raster lighting naturally.
    reflected=arr[::-1].copy()
    reflected=cv2.GaussianBlur(reflected,(5,3),0)
    for y in range(bottom):
        t=(y+1)/(bottom+1)
        row=np.roll(reflected[min(y,h-1)], int(2*np.sin(y*1.6)),axis=0)
        intensity=.7*(1-t)**2
        out[top+h+y]=row*intensity+bg*(1-intensity)
    return Image.fromarray(np.uint8(np.clip(out,0,255)))

def save(im,name):
    im.convert('RGB').save(ASSETS/name,'WEBP',quality=96,method=6)

poster=Image.open(SOURCE).convert('RGB')
hero=poster.crop((0,0,1024,290))
hero=erase_letters(hero,[(35,20,490,130,85),(35,132,505,217,75),
                          (35,233,515,280,70),(838,215,1010,280,65)])
# The old copy sat over intentionally dark scenery. A gentle left-side wash
# preserves that design and prevents retouching texture from competing with HTML.
a=np.asarray(hero,dtype=np.float32)
x=np.linspace(0,1,a.shape[1]); fade=np.clip((.53-x)/.35,0,1)*.42
base=np.array([2.,9.,14.]); a=a*(1-fade[None,:,None])+base*fade[None,:,None]
# Replace the old typography field with a clean night-sky wash. Do not leave
# inpainted letter-shaped texture behind the real heading. The detailed lake,
# mountain skyline, moon and complete N stack to its right stay untouched.
y=np.linspace(0,1,a.shape[0])[:,None,None]
wash=base[None,None,:]+np.array([1.,2.,3.])[None,None,:]*(1-y)
left=np.clip((530-np.arange(a.shape[1]))/110,0,1)
a=a*(1-left[None,:,None])+wash*left[None,:,None]
# The old corner caption sat in the dark bank: smooth just that text field.
blur=cv2.GaussianBlur(a,(0,0),14)
mask=np.zeros(a.shape[:2],np.float32);mask[216:286,829:1018]=1
mask=cv2.GaussianBlur(mask,(0,0),7)
a=a*(1-mask[:,:,None])+blur*mask[:,:,None]
hero=expand_landscape(Image.fromarray(np.uint8(a)),24,62)
save(hero,'hero.webp')

# Full card scenes, not inset pictures. Trim only the poster's 1px outer frame,
# remove its copy, and retain the glass objects / scenery at their native scale.
# The left of each scene is intentionally empty for real HTML text.
rows = [(594,714), (724,845), (854,975), (985,1106), (1116,1242)]
names = [('websites','frontend'), ('automation','shell'), ('data','game'),
         ('desktop','agents'), ('packages','creators')]
sizes={}
for (y0,y1),pair in zip(rows,names):
    for col,name in enumerate(pair):
        x0,x1 = (32,507) if col==0 else (517,993)
        im=poster.crop((x0,y0,x1,y1))
        im=erase_letters(im,[(0,0,249,im.height,75)])
        if name=='shell':
            im=erase_letters(im,[(779-x0+4,724-y0+41,879-x0,724-y0+86,75)])
        elif name=='data':
            im=erase_letters(im,[(310-x0,910-y0,347-x0,935-y0,118),
                                  (370-x0,897-y0,402-x0,923-y0,118),
                                  (435-x0,906-y0,471-x0,934-y0,118)])
        arr=np.asarray(im,dtype=np.float32)
        wash=np.clip((259-np.arange(im.width))/35,0,1)
        arr=arr*(1-wash[None,:,None])+np.array([2.,9.,14.])*wash[None,:,None]
        im=Image.fromarray(np.uint8(arr))
        top,bottom=(14,180-im.height-14)
        if name=='automation': top,bottom=(180-im.height-4,4)
        framed=expand_landscape(im,top,bottom)
        save(framed,f'{name}.webp')
        sizes[name]={'width':framed.width,'height':framed.height,'source_top':top,
                     'poster_x':x0,'poster_y':y0,'source_height':im.height}

(ROOT/'docs/artwork/about-art-dimensions.json').write_text(json.dumps(sizes,indent=2)+'\n')
print('Restored full raster framing:',sizes)
print('Text-free hero:',hero.size)
