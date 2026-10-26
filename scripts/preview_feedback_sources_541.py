from PIL import Image
from compile_translation import ROOT
from pathlib import Path
import struct,json
out=ROOT/'translation/feedback_541'
for p in (out/'decoded').glob('*.png'):
    im=Image.open(p).convert('RGBA')
    if 'camp_c_main.spr3.tex1' not in p.name:continue
    bg=Image.new('RGBA',im.size,'#555555');bg.alpha_composite(im)
    bg.resize((im.width*3,im.height*3),Image.Resampling.NEAREST).save(out/'camp_secondary_large.png')
raw=(ROOT/'data/camp/c_main.spr3').read_bytes()
print('header',struct.unpack_from('<12I',raw))
table=struct.unpack_from('<I',raw,28)[0]
records=[]
for i in range(struct.unpack_from('<H',raw,22)[0]):
    p=struct.unpack_from('<I',raw,table+8*i+4)[0]
    name=raw[p+4:p+36].split(b'\0')[0].decode('cp932',errors='replace')
    box=struct.unpack_from('<4i',raw,p+84)
    records.append(dict(index=i,name=name,box=box,header=raw[p+36:p+84].hex()))
    if any(s in name for s in ['記憶','切替','スキル','戻','控え','パーティ','リーダー','属性']):print(records[-1])
(out/'camp_sprite_records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
