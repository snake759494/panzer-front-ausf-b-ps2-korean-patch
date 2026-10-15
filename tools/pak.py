import struct
import os
ISO=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'Panzer Front Ausf.B (Europe).iso')
PAKS={'D1.PAK':1135,'D.PAK':200409}
def entries(f,lba):
    f.seek(lba*2048);n,hs=struct.unpack('<II',f.read(8));d=f.read(n*0x48);out=[]
    for i in range(n):
        o,s=struct.unpack_from('<II',d,i*0x48);nm=d[i*0x48+8:i*0x48+0x48].split(b'\0')[0].decode('latin1')
        out.append((nm,o,s))
    return out
def read(f,pak,nm):
    for n,o,s in entries(f,PAKS[pak]):
        if n==nm: f.seek(PAKS[pak]*2048+o);return f.read(s)
