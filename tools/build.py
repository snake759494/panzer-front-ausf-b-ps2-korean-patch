"""한글 패치 빌드: python tools/build.py [출력 ISO]"""
import sys,os,json,re,struct,glob
T=os.path.dirname(os.path.abspath(__file__));R=os.path.dirname(T);sys.path.insert(0,T);sys.path.insert(0,R+'/translation')
import numpy as np,pak,isobuild,kfont,elf_ko,atlas
X=R+'/work/x/D';BS=chr(92)
FONT=('DoHyeon-Regular.ttf',15,128)
# ---------- 번역 로드 ----------
def load_ne():
    import hk
    return hk.load('ne')   # translation/ko/ne.tsv (원문 해시 → 한국어)
NE=load_ne()
EXTRA=[]   # 다른 모듈이 쓰는 한국어 문자열
def all_ko():
    return list(NE.values())+list(elf_ko.MSG.values())+list(elf_ko.OPT.values())+list(elf_ko.OTHER.values())+EXTRA
# ---------- 문자 코드 ----------
FD=open(X+'/FO/font.dat','rb').read();CODES=[FD[i:i+2] for i in range(0,len(FD),2)]
FIRST_KANJI=343
def charmap(texts):
    hs=sorted({c for t in texts for c in t if '\uac00'<=c<='\ud7a3'})
    assert len(hs)<=len(CODES)-FIRST_KANJI,len(hs)
    return {c:CODES[FIRST_KANJI+i] for i,c in enumerate(hs)}
def encoder(cm):
    def enc(s):
        o=b''
        for c in s:
            if c in cm:o+=cm[c]
            elif c in '\n￥':o+=b'\x81\x8f'
            else:o+=c.encode('cp932')
        return o
    return enc
def decode(b): return b.decode('cp932').replace('\uffe5','\n')
# ---------- 폰트 ----------
def build_font(cm):
    d=bytearray(open(X+'/FO/font.pza','rb').read());o=16+8192
    px=np.frombuffer(bytes(d[o:o+65536]),np.uint8).reshape(256,256).copy()
    for ch,code in cm.items():
        i=CODES.index(code);p=i//256;j=i%256;y=(j//16)*16;x=(j%16)*16
        g=np.zeros((16,16),np.uint8);g[:15,:15]=kfont.glyph(ch,*FONT)
        cell=px[y:y+16,x:x+16];cell&=~np.uint8(1<<p);cell|=(g<<p).astype(np.uint8)
    d[o:o+65536]=px.tobytes();return bytes(d)
# ---------- ELF ----------
def patch_elf(enc):
    ORIG=open(R+'/work/SLES_529.84','rb').read();e=bytearray(ORIG);warn=[]
    def cap(o):
        j=o
        while e[j]!=0:j+=1
        while j<len(e) and e[j]==0:j+=1
        return j-o-1
    def put(o,b,c=None):
        c=cap(o) if c is None else c
        if len(b)>c: warn.append((hex(o),len(b),c,decode(bytes(b)) if False else ''));return False
        n=e.index(0,o)-o;e[o:o+max(n,len(b))+1]=b+bytes(max(n,len(b))+1-len(b));return True
    def tables(base,size,cnt,slot,dic):
        for o in range(base,base+size,slot):
            s=bytes(e[o:o+slot]).split(b'\0')[0]
            if not s:continue
            t=decode(s).replace('\n','￥')
            if t not in dic:continue
            b=enc(dic[t])
            for k in range(cnt):
                oo=o+k*size;assert len(b)<slot,(t,len(b))
                e[oo:oo+slot]=b+bytes(slot-len(b))
    tables(0x150df0,0x3000,5,0x100,elf_ko.MSG)
    tables(0x15ff40,0xC00,5,0x20,elf_ko.OPT)
    done=set()
    for m in re.finditer(rb'(?:[\x20-\x7e]|[\x81-\x9f\xe0-\xfc][\x40-\xfc]){1,}\x00',bytes(e[0x13c000:0x169000])):
        o=0x13c000+m.start();s=m.group()[:-1]
        if 0x150df0<=o<0x15cdf0+0x3000 or 0x15ff40<=o<0x15ff40+0xC00*5:continue
        try:t=decode(s).replace('\n','￥')
        except:continue
        if elf_ko.HUD_RANGE[0]<=o<elf_ko.HUD_RANGE[1] and t in elf_ko.HUDSTR:
            ko=elf_ko.HUDSTR[t]
            if t in elf_ko.HUDCENTER: ko=' '*((len(t)-len(ko))//2)+ko   # 원문 길이 기준 고정 위치 → 공백으로 가운데 맞춤
            put(o,atlas.code(ko,ATL['hud']))
        elif 0x13df00<=o<0x142300 and t in elf_ko.AMMO: put(o,atlas.code(elf_ko.AMMO[t],ATL['hud']))
        elif t in elf_ko.OTHER and True: put(o,enc(elf_ko.OTHER[t]))
    # 아틀라스(큰/중간 글자) 제목: 칸 코드로 기록
    for o,s0,ko,kind in ATLAS_STR:
        assert ORIG[o:o+len(s0)]==s0.encode(),hex(o)
        b=atlas.code(ko,ATL[kind]);assert len(b)<=len(s0),(ko,len(b))
        e[o:o+len(s0)]=b+bytes(len(s0)-len(b))
    import hk
    for o,(h,ko) in elf_ko.HUDFORM.items():
        s0=ORIG[o:ORIG.index(0,o)].decode('cp932');assert hk.key(s0)==h,hex(o)
        b=atlas.code(ko,ATL['hud'])
        n=o+len(s0)
        while ORIG[n]==0 and n-o<40:n+=1
        assert len(b)<n-o,(ko,len(b),n-o);e[o:n-1]=b+bytes(n-1-o-len(b))
    for w in warn:print('ELF 용량 초과',w)
    return bytes(e)
# ---------- NE ----------
def patch_ne(enc):
    out={};miss=set()
    for lang in ['00','01','02','03','04']:
        for f0 in glob.glob(X+'/NE/00/NOR0?.PZE')+glob.glob(X+'/NE/00/MAP/EVT??.PZE'):
            rel=os.path.relpath(f0,X+'/NE/00').replace(os.sep,'/');p=f'{X}/NE/{lang}/{rel}'
            if not os.path.exists(p):continue
            en=open(f0,'rb').read();d=bytearray(open(p,'rb').read())
            for i in range(138):
                s=en[i*0x88:i*0x88+0x80].split(b'\0')[0]
                if not s:continue
                try:t=decode(s)
                except:continue
                if t not in NE:
                    if not re.search(r'[\x00-\x09\x0b-\x1f\uf8f3]',t):miss.add(t)
                    continue
                b=enc(NE[t]);assert len(b)<=127,(t,len(b))
                d[i*0x88:i*0x88+0x80]=b+bytes(0x80-len(b))
            out[BS+'D'+BS+'NE'+BS+lang+BS+rel.replace('/',BS)]=bytes(d)
    if miss:print('NE 미번역',len(miss),[repr(x) for x in miss])
    return out
ATLAS_STR=[(0x150a70,'TACTICS','전술','big'),(0x163c70,'OPTION','옵션','big'),
 (0x163b60,'VETERAN','베테랑','mid'),(0x163b68,'ACE','에이스','mid'),(0x163b70,'CUSTOM','사용자','mid'),
 (0x165920,'MISSION BRIEFING','작전 브리핑','mid'),
 (0x13a750,'MISSION BRIEFING','작전 브리핑','small'),(0x13a768,'START BATTLE','전투 개시','small')]
ATL={}
def main(out):
    import extra,img_ko,brief_ko
    EXTRA.extend(extra.texts())
    cm=charmap(all_ko());enc=encoder(cm);print('한글 글자 수',len(cm))
    repl={BS+'D'+BS+'FO'+BS+'FONT.PZA':build_font(cm)}
    big=atlas.uniq(k for o,s0,k,t in ATLAS_STR if t=='big');mid=atlas.uniq(k for o,s0,k,t in ATLAS_STR if t=='mid')
    # 작은 글자(브리핑 머리글·팝업): 렌더러가 0xC0 이상을 그리지 않으므로 A1~BF + 안 쓰는 소문자 칸만 사용
    small=atlas.uniq([k for o,s0,k,t in ATLAS_STR if t=='small']+list(brief_ko.PZD.values()))
    slots=list(range(0xA1,0xC0))+[0x71,0x77,0x79,0x6B,0x6D,0x75]
    assert len(small)<=len(slots),(len(small),len(slots))
    codes={c:slots[i] for i,c in enumerate(small)}
    pf,m=atlas.build(open(X+'/FO/PFFONT.PZA','rb').read(),big,mid,small,codes);ATL.update(m);print('아틀라스 음절',len(big),len(mid),len(small))
    repl[BS+'D'+BS+'FO'+BS+'PFFONT.PZA']=pf
    # 전투 HUD 글꼴(SCR.PZA): 탄종 + 전투 메뉴, 코드 0xA2~0xDF
    hs=atlas.uniq(list(elf_ko.AMMO.values())+list(elf_ko.HUDSTR.values())+[v for k,v in elf_ko.HUDFORM.values()])
    assert len(hs)<=0xDF-0xA2+1,len(hs)
    ATL['hud']={c:bytes([0xA2+i]) for i,c in enumerate(hs)}
    repl[BS+'D'+BS+'OT'+BS+'TH'+BS+'SCR.PZA']=atlas.build_hud(open(X+'/OT/TH/SCR.PZA','rb').read(),ATL['hud'])
    repl.update(patch_ne(enc));repl.update(extra.build(enc,ATL['small']));repl.update(img_ko.build(ATL['small']))
    elf=patch_elf(enc)
    isobuild.build(out,elf,repl);print('완료',out,len(repl),'파일')
if __name__=='__main__':
    main(sys.argv[1] if len(sys.argv)>1 else R+'/Panzer Front Ausf.B (Korean).iso')
