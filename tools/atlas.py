"""PFFONT.PZA 아틀라스 한글화.
큰 글자(32x48, A~Z)·중간 글자(16x24, A~Z): 한글 음절을 영문자 칸에 그리고 문자열은 그 영문자로 쓴다.
작은 글자(12x16, 코드-0x20 → 32열): 0xA1~0xDF, a~z 칸에 갈무리11 음절을 그리고 해당 바이트로 쓴다."""
import numpy as np,os,sys
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,os.path.dirname(__file__));import pza
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLOTS='ABCDEFGHJKMNOPQRSTUVWXYZ'   # I, L 칸(폭이 다름)은 쓰지 않음
SMALL=list(range(0xA1,0xE0))
def _mask(ch,w,h,size,font='NanumSquareNeo-eHv.ttf',ss=4):
    f=ImageFont.truetype(os.path.join(R,font),size*ss)
    im=Image.new('L',(w*ss,h*ss),0);d=ImageDraw.Draw(im)
    d.text((w*ss/2,h*ss/2),ch,255,font=f,anchor='mm')
    return np.array(im.resize((w,h),Image.BOX)).astype(float)/255
def _idx(m):
    o=np.full(m.shape,13,np.uint8);o[m>0.15]=12;o[m>0.4]=11;o[m>0.72]=9;return o
def _small(ch,width=8):
    """작은 글자(12x16 칸): 엔진이 원래 글자 폭만큼만 잘라 그리므로 갈무리11 Condensed(12px, 폭 7)를 그 폭 안에 그린다."""
    f=ImageFont.truetype(os.path.join(R,'Galmuri11-Condensed.ttf'),12);im=Image.new('L',(12,16),0);d=ImageDraw.Draw(im)
    l,t,r,b=f.getbbox('뷁');w=r-l;d.text((max((width-w)//2,0)-l,3-t),ch,255,font=f)
    a=np.array(im)>=128
    if a.any() and np.where(a.any(0))[0].max()+1<width: a=a|np.roll(a,1,1)   # 폭이 남으면 1px 굵게
    a[:,width:]=False;o=np.full(a.shape,13,np.uint8);o[a]=9
    return o
def uniq(strings): return ''.join(dict.fromkeys(c for s in strings for c in s if '\uac00'<=c<='\ud7a3'))
def build(src,big,mid,small,smallcodes=None):
    t,w,h,pal,idx,rest=pza.decode(src);idx=idx.copy();m={'big':{},'mid':{},'small':{}}
    assert len(big)<=len(SLOTS) and len(mid)<=len(SLOTS) and len(small)<=len(SMALL),(len(big),len(mid),len(small))
    for i,ch in enumerate(big):
        L=SLOTS[i];k=ord(L)-65;r,c=divmod(k,16);y,x=r*48,c*32
        idx[y:y+48,x:x+32]=13;idx[y+4:y+44,x+1:x+31]=_idx(_mask(ch,30,40,34));m['big'][ch]=L
    for i,ch in enumerate(mid):
        L=SLOTS[i];k=ord(L)-65;y,x=96,k*16
        idx[y:y+24,x:x+16]=13;idx[y+2:y+24,x:x+16]=_idx(_mask(ch,16,22,17));m['mid'][ch]=L
    for i,ch in enumerate(small):
        code=smallcodes[ch] if smallcodes else SMALL[i];k=code-0x20;y=120+(k//32)*16;x=(k%32)*12
        orig=(idx[y:y+16,x:x+12]!=13).any(0);ow=int(np.where(orig)[0].max())+1 if orig.any() else 8
        idx[y:y+16,x:x+12]=_small(ch,ow);m['small'][ch]=bytes([code])
    return pza.encode(t,w,h,pal,idx,rest),m
def code(s,table):
    """문자열 → 바이트(표에 있는 한글은 칸 코드, 나머지는 ASCII)."""
    o=b''
    for c in s:
        v=table.get(c)
        o+= (v if isinstance(v,bytes) else v.encode()) if v is not None else c.encode('ascii')
    return o
# 전투 HUD 글꼴(SCR.PZA): 글자 번호 g=코드-0x21(반각 가나 영역 0xA1~은 코드-0x44), 행=g//28, x=(g%28)*9, y=274+행*11, 칸 8x11
def hud_cell(code):
    g=code-0x44 if code>=0xA1 else code-0x21;return 274+(g//28)*11,(g%28)*9
def build_hud(src,table):
    t,w,h,pal,idx,rest=pza.decode(src);idx=idx.copy()
    f=ImageFont.truetype(os.path.join(R,'Galmuri11-Condensed.ttf'),12);l,tp,r,b=f.getbbox('뷁')
    bgi=int(np.bincount(idx[270:345].ravel()).argmax())
    for ch,code in table.items():
        y,x=hud_cell(code[0])
        im=Image.new('L',(8,11),0);d=ImageDraw.Draw(im);d.text((0-l,0-tp),ch,255,font=f)
        a=np.array(im)>=128;a=a|np.roll(a,1,1)   # 원본 영문처럼 획을 가로로 1px 굵게(8px 칸을 채움)
        cell=np.full((11,9),bgi,np.uint8);cell[:,:8][a]=13;idx[y:y+11,x:x+9]=cell
    return pza.encode(t,w,h,pal,idx,rest)
