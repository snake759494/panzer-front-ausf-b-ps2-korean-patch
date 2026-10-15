"""본문 한글 1bpp 글리프: 원본 영문이 굵고 가로로 넓은 각진 글꼴이라 배민 도현체를 15x14 칸에 꽉 채워 그린다."""
import numpy as np,os
from PIL import Image,ImageDraw,ImageFont
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_F={}
def glyph(ch,font='NanumSquareNeo-dEb.ttf',size=15,th=100,box=15):
    if font not in _F:_F[font]=ImageFont.truetype(os.path.join(ROOT,font),size*4)
    f=_F[font];im=Image.new('L',(80,80));d=ImageDraw.Draw(im);d.text((40,40),ch,255,font=f,anchor='mm')
    a=np.array(im);ys,xs=np.where(a>0);a=a[ys.min():ys.max()+1,xs.min():xs.max()+1]
    a=np.array(Image.fromarray(a).resize((box,box-1),Image.BOX));o=np.zeros((box,box),np.uint8);o[:box-1]=(a>=th)
    return o
