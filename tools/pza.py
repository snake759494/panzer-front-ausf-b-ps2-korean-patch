import struct,numpy as np
from PIL import Image
def decode(d):
    t,w,h,z=struct.unpack_from('<4I',d);n=16 if t==0 else 256
    pal=np.frombuffer(d[16:16+n*4],np.uint8).reshape(n,4).copy()
    o=16+n*4
    if t==0:
        b=np.frombuffer(d[o:o+w*h//2],np.uint8);idx=np.empty(w*h,np.uint8);idx[0::2]=b&15;idx[1::2]=b>>4
    else: idx=np.frombuffer(d[o:o+w*h],np.uint8).copy()
    return t,w,h,pal,idx.reshape(h,w),d[o+(w*h//2 if t==0 else w*h):]
def unswz(pal):  # PS2 CSM1 swizzle for 256 palettes
    if len(pal)!=256: return pal
    p=pal.copy()
    for i in range(256):
        j=(i&0xE7)|((i&8)<<1)|((i&16)>>1);p[i]=pal[j]
    return p
def to_img(d,swz=True):
    t,w,h,pal,idx,rest=decode(d);p=unswz(pal) if swz else pal
    rgba=p[idx].astype(np.uint16);rgba[...,3]=np.minimum(rgba[...,3]*2,255)
    return Image.fromarray(rgba.astype(np.uint8),'RGBA')
def encode(t,w,h,pal,idx,rest=b''):
    o=struct.pack('<4I',t,w,h,0)+pal.astype(np.uint8).tobytes()
    i=idx.reshape(-1).astype(np.uint8)
    o+=((i[0::2]&15)|(i[1::2]<<4)).astype(np.uint8).tobytes() if t==0 else i.tobytes()
    return o+rest
if __name__=='__main__':
    import sys
    for p in sys.argv[1:]:
        im=to_img(open(p,'rb').read());bg=Image.new('RGBA',im.size,(40,80,40,255));bg.alpha_composite(im);bg.convert('RGB').save(p+'.png')
