import struct
from PIL import Image
from compile_translation import ROOT,read,write
OUT=ROOT/'translation/previews_545';OUT.mkdir(exist_ok=True)
for name in ['shop','velvet','partyinfo']:
    path=f'camp/{name}.spr3' if name=='partyinfo' else f'facility/{name}.spr3'
    raw=(ROOT/'data'/path).read_bytes();table=struct.unpack_from('<I',raw,28)[0];rows=[]
    for i in range(struct.unpack_from('<H',raw,22)[0]):
        p=struct.unpack_from('<I',raw,table+i*8+4)[0]
        n=raw[p+4:p+36].split(b'\0')[0].decode('cp932',errors='replace');box=struct.unpack_from('<4i',raw,p+84)
        rows.append(dict(index=i,name=n,box=box))
    write(OUT/f'{name}_records.json',rows)
    print(name)
    for r in rows:
        if any(ord(c)>127 for c in r['name']):print(r)
for n in ['05','10','13','14','16','17']:
    im=Image.open(ROOT/f'translation/feedback_543/secondary_decoded/{n}.ctpk.00.png').convert('RGBA')
    bg=Image.new('RGBA',im.size,'#444444');bg.alpha_composite(im);bg.resize((im.width*3,im.height*3),Image.Resampling.NEAREST).save(OUT/f'{n}_original.png')
