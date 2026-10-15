# 이미지 한글화

import os,sys

R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,R+'/tools')

import numpy as np,images as I

X=R+'/work/x/D';BS=chr(92)

def P(*a): return BS+BS.join(('D',)+a)

H='NanumSquareNeo-eHv.ttf';B='NanumSquareNeo-dEb.ttf'

MON={'JAN':1,'FEB':2,'MAR':3,'APR':4,'MAY':5,'JUN':6,'JNE':6}

MISSION=[('훈련',None),('메르도르프','1940.5.13'),('필라스트리노 요새','1941.1.21'),('베다 폼','1941.2.6'),

 ('아제다비아','1941.4.2'),('라스 엘 메다우아르','1941.5.1'),('카푸초 요새','1941.5.15'),(None,None),

 ('BP 42','1941.5.15'),(None,None),('할파야 고개','1941.5.27'),('208 거점','1941.6.15'),('하페이드 능선','1941.6.15'),

 ('카푸초 요새 II','1941.6.15'),('카푸초 요새 III','1941.6.16'),('미정','19XX')]

def mname2():

    t,w,h,pal,idx,rest=I.load(X+'/ME/mname2.pza');idx=idx.copy();ramp=[14]+list(range(13,-1,-1))

    for r,(name,date) in enumerate(MISSION):

        y=24*r

        if name: I.put(idx,176,y+1,I.fit(name,200,22,H,17),ramp)

        if date: I.put(idx,4,y+1,I.fit(date,136,22,H,17,align='r'),ramp)

    return I.save(t,w,h,pal,idx,rest)

import cv2

MENU=['전술','옵션','불러오기','제작진']

ROWS=[(0,107),(107,107),(214,107),(321,107)]

def _bigmask(text,w,h,size=92,ss=4,dy=4):

    return I.fit(text,w,h,H,size,align='l',ss=ss,dy=dy)

def m00():

    t,w,h,pal,idx,rest=I.load(X+'/ME/m00.pza');idx=idx.copy()

    idx[0:448,:]=15

    alpha=[(4,96),(5,64),(6,40),(7,32),(8,28),(9,24),(10,20),(11,16),(12,12),(13,8),(14,4),(15,0)]

    for txt,(y,hh) in zip(MENU,ROWS):

        c=_bigmask(txt,500,hh)

        sh=cv2.GaussianBlur(np.roll(np.roll(c,5,0),5,1),(0,0),3)*110

        reg=np.full(c.shape,15,np.uint8)

        for i,a in alpha[::-1]:reg[sh>=a-2]=i

        reg[c>0.5]=0;reg[(c>0.25)&(c<=0.5)]=2

        idx[y:y+hh,8:508]=reg

    return I.save(t,w,h,pal,idx,rest)

def m01():

    t,w,h,pal,idx,rest=I.load(X+'/ME/m01.pza');idx=idx.copy()

    txt_ids={0,1,2,3,5,6,7,8,9,11,12,14}

    for txt,(y,hh) in zip(MENU,ROWS):

        bg=[]

        for yy in range(y,y+hh):

            v=[x for x in idx[yy] if x not in txt_ids];bg.append(np.bincount(v,minlength=16).argmax() if v else 15)

        c=_bigmask(txt,500,hh,dy=-1)

        m=(c>0.5).astype(np.uint8)

        din=cv2.distanceTransform(m,cv2.DIST_L2,3)

        reg=np.repeat(np.array(bg,np.uint8)[:,None],500,1)

        ring=(cv2.dilate(m,np.ones((3,3),np.uint8))>0)&(m==0)

        reg[ring]=14

        ramp=[(1,11),(2,9),(3,7),(4,5),(5,2)]

        for d,i in ramp[::-1]:reg[(m>0)&(din<=d)]=i

        reg[(m>0)&(din>5)]=0

        idx[y:y+hh,8:508]=reg

    return I.save(t,w,h,pal,idx,rest)

COUNTRY=[['독일','이탈리아','영국'],['프랑스','소련','미국'],['일본','호주','기타']]

def skin(name='skin.pza'):

    t,w,h,pal,idx,rest=I.load(X+'/ME/'+name);idx=idx.copy()

    a=np.array(I.pza.to_img(I.pza.encode(t,w,h,pal,idx,rest)))[...,3]

    for r,y in enumerate((14,34,54)):

        for c,x0 in enumerate((0,170,340)):

            # 아이콘 끝 찾기: 왼쪽에서 첫 빈 세로줄

            xe=x0+20

            I.put_color(idx,pal,xe+1,y-1,I.fit(COUNTRY[r][c],160-(xe-x0),18,H,16),(255,255,255))

    return I.save(t,w,h,pal,idx,rest)

def title01():

    t,w,h,pal,idx,rest=I.load(X+'/ME/title01.pza');idx=idx.copy()

    c=I.fit('스타트 버튼을 누르세요',300,24,H,18,align='l')

    I.put_rgba(idx,pal,40,194,I.outlined(c,(255,255,255),(0,0,0)))

    return I.save(t,w,h,pal,idx,rest)

def loading():

    t,w,h,pal,idx,rest=I.load(X+'/OT/AS/ETC/LOADING.PZA');idx=idx.copy()

    for k in range(5):

        y=k*32;idx[y:y+32,:]=next(i for i,p in enumerate(pal) if p[3]==0) if any(p[3]==0 for p in pal) else idx[0,0]

        for yy,txt,sz in ((y,'로딩 중'+'.'*k,15),(y+16,'(잠시 기다려 주세요)',13)):

            c=I.cov(txt,200,16,H,sz);rgba=np.zeros(c.shape+(4,));rgba[...,:3]=np.array((234,163,26))*c[...,None];rgba[...,3]=128

            I.put_rgba(idx,pal,40,yy,rgba)

    return I.save(t,w,h,pal,idx,rest)

import glob,hashlib,struct,brief_ko

BF=X+'/ME/BRIEFING/00/'

def _wrap(text,fname,size,maxw):

    f=I.font(fname,size*4);meas=lambda t:I.ImageDraw.Draw(I.Image.new('L',(1,1))).textlength(t,font=f)/4

    out=[]

    for para in text.split(chr(10)):

        if not para.strip():out.append('');continue

        cur=''

        for w in para.split(' '):

            t=(cur+' '+w) if cur else w

            if meas(t)<=maxw:cur=t

            else:

                if cur:out.append(cur)

                cur=w

                while meas(cur)>maxw:  # 단어가 너무 길면 글자 단위

                    k=len(cur)

                    while meas(cur[:k])>maxw:k-=1

                    out.append(cur[:k]);cur=cur[k:]

        out.append(cur)

    return out

def _pages_of(d):

    n=struct.unpack_from('<I',open(d+'0.PZD','rb').read(),0x40)[0]

    fs={os.path.basename(f).upper():f for f in glob.glob(d+'F*') if f.upper().endswith('.PZA')}

    return [fs['F%02d.PZA'%i] for i in range(n)]

def briefing(small=None):

    out={};keyhash={}

    for k in brief_ko.BRIEF:

        keyhash[tuple(hashlib.md5(open(f,'rb').read()).hexdigest() for f in _pages_of(BF+k+'/'))]=k

    for d in sorted(glob.glob(BF+'*/*/')):

        pages=_pages_of(d);hk=tuple(hashlib.md5(open(f,'rb').read()).hexdigest() for f in pages)

        k=keyhash.get(hk)

        if k is None:print('브리핑 번역 없음',d);continue

        n=len(pages)

        for size,pitch in ((15,18),(14,17),(13,16),(12,15)):

            lines=_wrap(brief_ko.BRIEF[k],B,size,226)

            per=(256-4)//pitch

            if len(lines)<=per*n:break

        else: raise SystemExit('브리핑 넘침 '+k)

        for i,f in enumerate(pages):

            t,w,h,pal,idx,rest=I.load(f)

            tr=[i for i,p in enumerate(pal) if p[3]==0][0];op=sorted([i for i,p in enumerate(pal) if p[3]>0],key=lambda i:int(pal[i][:3].sum()))

            ramp=[tr]+op;idx=np.full_like(idx,tr)

            for j,line in enumerate(lines[i*per:(i+1)*per]):

                if line:I.put(idx,16,4+j*pitch,I.cov(line,236,pitch,B,size),ramp,clear=False)

            rel=f[len(X):].replace('/',BS)

            out[BS+'D'+rel if not rel.startswith(BS) else BS+'D'+rel]=I.save(t,w,h,pal,idx,rest)

        # 0.PZD 지명·날짜

        pz=bytearray(open(d+'0.PZD','rb').read())
        if small:
            import atlas
            nm=pz[0:32].split(b'\x00')[0].decode();dt=pz[32:64].split(b'\x00')[0].decode().split()
            kn=atlas.code(brief_ko.PZD.get(nm,nm),small);pz[0:32]=kn.ljust(32,bytes(1))
            if len(dt)==3: kd='%s.%d.%s'%(dt[2],brief_ko.MONTH[dt[1]],dt[0])
            else: kd=' '.join(dt)
            pz[32:64]=kd.encode().ljust(32,bytes(1))

        out[BS+'D'+(d+'0.PZD')[len(X):].replace('/',BS)]=bytes(pz)

    return out

import maplabels
def _label_img(path,labels):
    import cv2
    t,w,h,pal,idx,rest=I.load(path);idx=idx.copy()
    P=(I.pza.unswz(pal) if len(pal)==256 else pal).astype(float)
    rgba=P[idx].copy();orig=rgba.copy();cleared=np.zeros((h,w),bool);boxes=[]
    for x0,y0,x1,y1,txt,col in labels:
        c=np.array(maplabels.COLOR[col],float)
        nx0,ny0,nx1,ny1=max(x0-14,0),max(y0-4,0),min(x1+14,w),min(y1+4,h)
        reg=rgba[ny0:ny1,nx0:nx1];rr=reg[...,:3];rs=rr.max(-1)-rr.min(-1);al=reg[...,3]>0
        near=((rr-c)**2).sum(-1)<120**2
        halo=al&(rr.min(-1)>130)&(rs<90)
        # 원래 상자 근처의 흰 테두리와 연결된 것만
        n,lab=cv2.connectedComponents(cv2.dilate(halo.astype(np.uint8),np.ones((3,3),np.uint8)))
        inner=lab[max(y0-ny0,0):y1-ny0,max(x0-nx0,0):x1-nx0];keep=set(np.unique(inner))-{0}
        halo=halo&np.isin(lab,list(keep))
        zone=cv2.dilate(halo.astype(np.uint8),np.ones((3,3),np.uint8),iterations=2)>0
        clr=al&(halo|(zone&(near|(rs<90))))
        cleared[ny0:ny1,nx0:nx1]|=clr;boxes.append((x0,y0,x1,y1,txt,c))
    # 지운 자리 복원(주변 색·알파로 채움)
    m=cleared.astype(np.uint8)*255
    rgb8=np.clip(orig[...,:3],0,255).astype(np.uint8);a8=np.clip(orig[...,3]*2,0,255).astype(np.uint8)
    rgb8=cv2.inpaint(rgb8,m,4,cv2.INPAINT_TELEA);a8=cv2.inpaint(a8,m,4,cv2.INPAINT_TELEA)
    a8=np.where(a8<128,0,255).astype(np.uint8)   # 반투명 경계는 없애고 0/불투명
    rgba[cleared,:3]=rgb8[cleared];rgba[cleared,3]=a8[cleared]/2
    for x0,y0,x1,y1,txt,c in boxes:
        bw,bh=x1-x0,y1-y0;lines=txt.split(chr(10));lh=bh/len(lines)
        for li,line in enumerate(lines):
            size=int(min(lh-3,14))
            cw=max(bw,int(I.ImageDraw.Draw(I.Image.new('L',(1,1))).textlength(line,font=I.font(B,size*4))/4)+6)
            cv=I.fit(line,cw,int(lh),B,size,align='c',minsize=9)
            halo=cv2.dilate((cv>0.3).astype(np.uint8),np.ones((3,3),np.uint8),iterations=2).astype(float)
            cx=x0+bw//2-cw//2;cy=int(y0+li*lh);xa=max(cx,0);xb=min(cx+cw,w);ya=cy;yb=min(cy+int(lh),h)
            sub=rgba[ya:yb,xa:xb];cvv=cv[:yb-ya,xa-cx:xb-cx];hv=halo[:yb-ya,xa-cx:xb-cx]
            sub[hv>0]=np.array([235,235,225,128.])
            a=cvv[...,None];sub[...]=sub*(1-a)+np.concatenate([np.broadcast_to(c,cvv.shape+(3,)),np.full(cvv.shape+(1,),128.)],-1)*a
    pm=np.concatenate([P[:,:3]*P[:,3:4]/128,P[:,3:4]],1);tgt=np.concatenate([rgba[...,:3]*rgba[...,3:4]/128,rgba[...,3:4]],-1)
    changed=(rgba!=P[idx]).any(-1);tc=tgt[changed]
    d=((tc[:,None,:]-pm[None])**2).sum(-1);idx[changed]=d.argmin(1).astype(np.uint8)
    return I.save(t,w,h,pal,idx,rest)
def maps():
    out={};byhash={}
    for k,lab in maplabels.LABELS.items():
        byhash[hashlib.md5(open(BF+k,'rb').read()).hexdigest()]=_label_img(BF+k,lab)
    for f in glob.glob(BF+'*/*/*'):
        n=os.path.basename(f).upper()
        if n.startswith('M') and n.endswith('.PZA'):
            h=hashlib.md5(open(f,'rb').read()).hexdigest()
            if h in byhash: out[BS+'D'+f[len(X):].replace('/',BS)]=byhash[h]
    return out
CREDIT=[(9,23,128,'감독'),(9,23,384,'영업'),(40,58,126,'프로그램'),(40,58,383,'개발 협력'),(73,89,126,'전차 모델링'),
 (73,89,384,'제품 관리'),(105,121,132,'배경 그래픽'),(105,121,385,'프로듀서'),(137,151,128,'사운드'),(168,185,128,'패키지 디자인'),
 (202,215,130,'일러스트'),(233,246,128,'홍보'),(266,282,255,'총괄 프로듀서'),(297,310,255,'소프트웨어 매뉴얼')]
def credit():
    t,w,h,pal,idx,rest=I.load(X+'/ME/CREDIT/NAME00.PZA');idx=idx.copy();idx[:330,:]=0
    ramp=[0]+list(range(15,0,-1))
    for y0,y1,cx,txt in CREDIT:
        c=I.cov(txt,200,20,B,15,align='c');I.put(idx,cx-100,(y0+y1)//2-10,c,ramp,clear=False)
    return I.save(t,w,h,pal,idx,rest)
def build(small=None):

    out={P('ME','MNAME2.PZA'):mname2(),P('ME','M00.PZA'):m00(),P('ME','M01.PZA'):m01(),P('ME','SKIN.PZA'):skin(),

         P('ME','TITLE01.PZA'):title01(),P('OT','AS','ETC','LOADING.PZA'):loading()}

    out[P('ME','CREDIT','NAME00.PZA')]=credit()
    out.update(briefing(small));out.update(maps())

    return out

if __name__=='__main__':
    ims=[]
    for k in maplabels.LABELS:
        d=_label_img(BF+k,maplabels.LABELS[k]);o=I.pza.to_img(open(BF+k,'rb').read());n=I.pza.to_img(d)
        def bb(im):
            g=I.Image.new('RGBA',im.size,(30,30,30,255));g.alpha_composite(im);return g.convert('RGB')
        xs=[l[0] for l in maplabels.LABELS[k]]+[l[2] for l in maplabels.LABELS[k]];ys=[l[1] for l in maplabels.LABELS[k]]+[l[3] for l in maplabels.LABELS[k]]
        box=(max(min(xs)-40,0),max(min(ys)-30,0),min(max(xs)+40,512),min(max(ys)+30,512))
        a,b2=bb(o).crop(box),bb(n).crop(box);c=I.Image.new('RGB',(a.width*2+4,a.height+12));c.paste(a,(0,12));c.paste(b2,(a.width+4,12));I.ImageDraw.Draw(c).text((0,0),k,(255,255,0));ims.append(c)
    for i in range(0,len(ims),4):
        W=max(x.width for x in ims[i:i+4]);H=sum(x.height for x in ims[i:i+4]);c=I.Image.new('RGB',(W,H));y=0
        for x in ims[i:i+4]:c.paste(x,(0,y));y+=x.height
        c.save(R+'/work/pl_%d.png'%(i//4))
    raise SystemExit

    o=briefing();print(len(o))

    for k,v in o.items():

        if k.endswith('01'+BS+'00'+BS+'F00.pza') or k.endswith('06'+BS+'00'+BS+'F01.pza'):I.preview(v,R+'/work/p_'+k.split(BS)[-3]+'.png',None,2)

    I.preview(title01(),R+'/work/p_t1.png',(0,180,400,230),3);I.preview(loading(),R+'/work/p_ld.png',(0,0,256,160),2)

    I.preview(m00(),R+'/work/p_m00.png',None,1);I.preview(m01(),R+'/work/p_m01.png',None,1)

