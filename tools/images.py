"""PZA 이미지 글자 교체 도구."""
import numpy as np,os,sys
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,os.path.dirname(__file__));import pza
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_fc={}
def font(name,size):
    k=(name,size)
    if k not in _fc:_fc[k]=ImageFont.truetype(os.path.join(R,name),size)
    return _fc[k]
def cov(text,w,h,fname,size,align='l',ss=4,dy=0,spacing=0):
    """w x h 영역 안의 글자 커버리지(0~1). align l/c/r, 세로 가운데."""
    f=font(fname,size*ss);im=Image.new('L',(w*ss,h*ss),0);d=ImageDraw.Draw(im)
    tw=d.textlength(text,font=f)+spacing*ss*max(len(text)-1,0)
    x={'l':0,'c':(w*ss-tw)/2,'r':w*ss-tw}[align]
    if spacing:
        for ch in text:
            d.text((x,h*ss/2+dy*ss),ch,255,font=f,anchor='lm');x+=d.textlength(ch,font=f)+spacing*ss
    else: d.text((x,h*ss/2+dy*ss),text,255,font=f,anchor='lm')
    return np.array(im.resize((w,h),Image.BOX)).astype(float)/255
def fit(text,w,h,fname,size,minsize=8,**k):
    """폭에 맞을 때까지 크기를 줄여 커버리지 반환."""
    s=size
    while s>minsize:
        f=font(fname,s*4)
        if ImageDraw.Draw(Image.new('L',(1,1))).textlength(text,font=f)/4<=w: break
        s-=1
    return cov(text,w,h,fname,s,**k)
def put(idx,x,y,c,ramp,clear=True):
    """ramp: 투명→진한 순 팔레트 인덱스 목록."""
    h,w=c.shape;reg=idx[y:y+h,x:x+w]
    k=np.clip(np.rint(c*(len(ramp)-1)),0,len(ramp)-1).astype(int)
    new=np.array(ramp,np.uint8)[k]
    if clear: reg[:]=new
    else: reg[k>0]=new[k>0]
def load(p): return pza.decode(open(p,'rb').read())
def save(t,w,h,pal,idx,rest): return pza.encode(t,w,h,pal,idx,rest)
def preview(data,path,crop=None,scale=2):
    im=pza.to_img(data);bg=Image.new('RGBA',im.size,(40,70,40,255));bg.alpha_composite(im)
    if crop:bg=bg.crop(crop)
    bg.resize((bg.width*scale,bg.height*scale),0).convert('RGB').save(path)
def put_color(idx,pal,x,y,c,rgb,amax=128,bg=None):
    """커버리지 c를 rgb 색으로 그려 가장 가까운 팔레트 항목으로 양자화(8/4bpp 공용).
    bg: 지운 자리의 배경 RGBA(None이면 투명)."""
    P=(pza.unswz(pal) if len(pal)==256 else pal).astype(float)
    pm=np.concatenate([P[:,:3]*P[:,3:4]/128,P[:,3:4]],1)
    h,w=c.shape;a=c*amax
    if bg is None: base=np.zeros((h,w,4))
    else: base=np.broadcast_to(np.array(bg,float),(h,w,4)).copy()
    bpm=np.concatenate([base[...,:3]*base[...,3:4]/128,base[...,3:4]],2)
    fpm=np.concatenate([np.array(rgb,float)*a[...,None]/128,a[...,None]],2)
    tgt=fpm+bpm*(1-c[...,None])
    d=((tgt[...,None,:]-pm[None,None])**2).sum(-1)
    idx[y:y+h,x:x+w]=d.argmin(-1).astype(np.uint8)
def put_rgba(idx,pal,x,y,rgba):
    """rgba(h,w,4; 알파 0~128)를 가장 가까운 팔레트 항목으로 양자화해 기록."""
    P=(pza.unswz(pal) if len(pal)==256 else pal).astype(float)
    pm=np.concatenate([P[:,:3]*P[:,3:4]/128,P[:,3:4]],1)
    t=np.concatenate([rgba[...,:3]*rgba[...,3:4]/128,rgba[...,3:4]],2)
    h,w=rgba.shape[:2];best=np.zeros((h,w),np.uint8);bd=np.full((h,w),1e18)
    for i,p in enumerate(pm):
        d=((t-p)**2).sum(-1);m=d<bd;bd[m]=d[m];best[m]=i
    idx[y:y+h,x:x+w]=best
def outlined(c,fg,ol,width=1,amax=128):
    """글자 커버리지 c → fg 글자 + ol 테두리 RGBA."""
    import cv2
    k=np.ones((2*width+1,2*width+1),np.uint8)
    o=cv2.dilate((c*255).astype(np.uint8),k).astype(float)/255
    rgba=np.zeros(c.shape+(4,))
    rgba[...,:3]=np.array(ol,float);rgba[...,3]=o*amax
    rgba[...,:3]=rgba[...,:3]*(1-c[...,None])+np.array(fg,float)*c[...,None]
    return rgba
