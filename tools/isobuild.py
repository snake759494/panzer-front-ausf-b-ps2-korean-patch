"""원본 ISO + (새 ELF, D.PAK 교체 파일들) -> 새 ISO. 바뀐 파일은 D.PAK 끝에 추가하고 목차만 고친다."""
import struct,shutil,os,sys
sys.path.insert(0,os.path.dirname(__file__));import pak,iso
SEC=2048
def build(out,elf=None,repl={}):
    src=open(pak.ISO,'rb');recs=iso.records(src)
    shutil.copyfile(pak.ISO,out);f=open(out,'r+b')
    if elf is not None:
        lba,sz,_=recs['SLES_529.84'];assert len(elf)==sz;f.seek(lba*SEC);f.write(elf)
    lba,sz,rec=recs['D.PAK'];base=lba*SEC
    src.seek(base);n,hs=struct.unpack('<II',src.read(8));toc=bytearray(src.read(n*0x48))
    names={}
    for i in range(n):names.setdefault(toc[i*0x48+8:i*0x48+0x48].split(b'\0')[0].decode('latin1').upper(),[]).append(i)
    end=(sz+SEC-1)//SEC*SEC;pos=end
    for nm,data in repl.items():
        idx=names[nm.upper()]
        for i in idx:
            o,s=struct.unpack_from('<II',toc,i*0x48)
            if len(data)<=s or (len(data)+15)//16*16<= s:  # 같은 크기 이하면 제자리
                f.seek(base+o);f.write(data);struct.pack_into('<I',toc,i*0x48+4,len(data))
            else:
                f.seek(base+pos);f.write(data);struct.pack_into('<II',toc,i*0x48,pos,len(data));pos=(pos+len(data)+SEC-1)//SEC*SEC
                break
        for j in idx[1:]: toc[j*0x48:j*0x48+8]=toc[idx[0]*0x48:idx[0]*0x48+8]
    f.seek(base+8);f.write(toc)
    newsz=pos if pos>end else sz
    f.seek(rec+10);f.write(struct.pack('<I',newsz)+struct.pack('>I',newsz))
    total=lba+(newsz+SEC-1)//SEC
    f.seek(16*SEC+80);vs=struct.unpack('<I',f.read(4))[0]
    if total>vs:
        f.seek(16*SEC+80);f.write(struct.pack('<I',total)+struct.pack('>I',total))
        f.truncate(total*SEC)
    f.close()
