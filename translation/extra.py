# SET(승무원·방향·차종 이름표), TNAME(전차 분류·별칭) 번역과 적용
import os, glob, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools'))
import brief_ko, atlas
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
X = R + '/work/x/D'
BS = chr(92)

from hk import load
SET = load('set')      # 승무원·방향·차종 이름표
TN = load('tn')        # 전차 분류·별칭

TNAME = load('tname')  # 전차 정식명·약칭
DIV = load('div')      # 부대·콜사인명
def texts():
    return _texts()+list(TNAME.values())+list(DIV.values())
def _texts():
    return list(SET.values()) + list(TN.values()) + ['제35전차연대','제2중대']

def build(enc, small=None):
    out = {}
    # SET: 영어(00) 파일 기준으로 16바이트 칸 번역 → 모든 언어 폴더에 같은 파일
    for p in sorted(glob.glob(X + '/NE/00/SET0?.PZE')):
        d = bytearray(open(p, 'rb').read())
        for i in range(0, len(d), 16):
            s = bytes(d[i:i+16]).rstrip(b'\0')
            if not s: continue
            try: t = s.decode('cp932')
            except UnicodeDecodeError: continue
            if t in SET:
                b = enc(SET[t]); assert len(b) <= 16, t
                d[i:i+16] = b + bytes(16 - len(b))
        name = os.path.basename(p)
        for lang in ['00', '01', '02', '03', '04']:
            if os.path.exists(f'{X}/NE/{lang}/{name}'):
                out[BS.join(['', 'D', 'NE', lang, name])] = bytes(d)
    # TNAME: 영어판(00) 분류·별칭 필드 번역 → tname00~04 모두 같은 내용
    d = bytearray(open(X + '/DI/tname00.pze', 'rb').read())
    for r in range(0xb8, len(d) - 0xb3, 0xb4):
        for fo, fl in [(0x0, 0x40), (0x40, 0x10), (0x50, 0x18)]:
            o = r + fo; s = bytes(d[o:o+fl]).split(b'\x00')[0]; t = s.decode('cp932', 'replace')
            if t in TNAME and TNAME[t] != t:
                b = enc(TNAME[t]); assert len(b) < fl, t
                d[o:o+fl] = b + bytes(fl - len(b))
        for fo, fl in [(0x68, 0x18), (0x80, 0x18), (0x98, 0x18)]:
            o = r + fo; s = bytes(d[o:o+fl]).split(b'\0')[0]
            t = s.decode('cp932', 'replace')
            if t in TN:
                b = enc(TN[t]); assert len(b) < fl, t
                d[o:o+len(s)] = bytes(len(s)); d[o:o+len(b)] = b
    if False:
        d2=bytearray(open(X+'/DI/DIV/01.PZE','rb').read())
        for a,b in [(b'Panzer-Regiment 35',enc('제35전차연대')),(b'2. Kompanie',enc('제2중대'))]:
            i=d2.find(a)
            while i!=-1:
                d2[i:i+len(a)]=b+bytes(len(a)-len(b));i=d2.find(a,i+1)
        out[BS.join(['','D','DI','DIV','01.PZE'])]=bytes(d2)
    # DIV: 부대명(레코드 0x54, 이름 +4 32바이트), 맨 앞 지명(0x14)
    for p in sorted(glob.glob(X + '/DI/DIV/*')):
        b0 = os.path.basename(p)
        if not (b0[:2].isdigit() and b0.upper().endswith('.PZE')): continue
        d2 = bytearray(open(p, 'rb').read()); ch = False
        nm = bytes(d2[0x14:0x34]).split(b'\x00')[0].decode('latin1')
        if small and nm in brief_ko.PZD:   # 미션 이름 칸: 브리핑 머리글(작은 글자 아틀라스)로 표시됨
            d2[0x14:0x34] = atlas.code(brief_ko.PZD[nm], small).ljust(32, bytes(1)); ch = True
        for q0 in range(0x14, len(d2) - 32, 0x54):
            for q in ((q0 + 4,)):
                s = bytes(d2[q:q+32]).split(b'\x00')[0]
                if len(s) < 2 or any(c < 0x20 for c in s): continue
                t = s.decode('cp932', 'replace')
                if t in DIV and DIV[t] != t:
                    b = enc(DIV[t]); assert len(b) <= 31, t
                    d2[q:q+32] = b + bytes(32 - len(b)); ch = True
        if ch: out[BS.join(['', 'D', 'DI', 'DIV', b0.upper()])] = bytes(d2)
    for n in range(5):
        out[BS.join(['', 'D', 'DI', 'TNAME%02d.PZE' % n])] = bytes(d)
    return out
