"""원본 ISO에서 빌드에 필요한 파일을 work/ 로 추출한다(로컬 전용, 저장소에 넣지 않음).
python tools/prepare.py"""
import os, sys, hashlib
T = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(T); sys.path.insert(0, T)
import pak, iso
B = chr(92)
SRC_SHA = 'f37f08210c361975432bb47d8f0601c897c4e9c6994e55cbf89767f2c7b37f55'
PREFIX = [B + 'D' + B + x for x in ('NE', 'FO', 'ME', 'DI', 'OT' + B + 'TH', 'OT' + B + 'AS' + B + 'ETC')]
def main():
    h = hashlib.sha256()
    with open(pak.ISO, 'rb') as f:
        for b in iter(lambda: f.read(1 << 24), b''): h.update(b)
    if h.hexdigest() != SRC_SHA: sys.exit('원본 ISO 해시 불일치: ' + h.hexdigest())
    f = open(pak.ISO, 'rb'); w = os.path.join(R, 'work'); os.makedirs(w, exist_ok=True)
    lba, sz, _ = iso.records(f)['SLES_529.84']; f.seek(lba * 2048)
    open(os.path.join(w, 'SLES_529.84'), 'wb').write(f.read(sz))
    n = 0
    for name, o, s in pak.entries(f, pak.PAKS['D.PAK']):
        if any(name.lower().startswith(p.lower()) for p in PREFIX):
            p = os.path.join(w, 'x', *name.strip(B).split(B))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            f.seek(pak.PAKS['D.PAK'] * 2048 + o); open(p, 'wb').write(f.read(s)); n += 1
    print('추출', n, '파일 →', w)
if __name__ == '__main__': main()
