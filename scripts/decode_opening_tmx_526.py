"""Decode known PSMT8/PSMTC32 TMX opening textures; never rewrite game data."""
import json,struct,hashlib
from pathlib import Path
from PIL import Image
from check_roundtrip import parse_members
ROOT=Path(__file__).resolve().parent

def decode(raw):
    assert raw[8:12]==b'TMX0' and struct.unpack_from('<I',raw,4)[0]==len(raw)
    assert raw[16:18]==bytes([1,0]) and raw[22] in (0x13,0x14) and raw[23]==0
    w,h=struct.unpack_from('<HH',raw,18)
    eight=raw[22]==0x13
    colors=256 if eight else 16
    start=64+colors*4
    assert len(raw)==start+(w*h if eight else w*h//2)
    pal=[]
    for i in range(colors):
        j=(i&~24)|((i&8)<<1)|((i&16)>>1) if eight else i
        r,g,b,a=raw[64+j*4:68+j*4]
        pal.append(bytes([r,g,b,min(255,round(a*255/128))]))
    indices=raw[start:] if eight else [i for v in raw[start:] for i in (v&15,v>>4)]
    return Image.frombytes('RGBA',(w,h),b''.join(pal[i] for i in indices))

def main():
    out=ROOT/'translation/opening_526';out.mkdir(exist_ok=True)
    rows=[]
    for name,data in parse_members((ROOT/'data/title/logo.bin').read_bytes()):
        im=decode(data);p=out/(name+'.png');im.save(p)
        rows.append(dict(member=name,size=list(im.size),source_sha256=hashlib.sha256(data).hexdigest(),png=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    (out/'decoded.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Decoded',len(rows),'original TMX textures; no source writes.')

if __name__=='__main__':main()
