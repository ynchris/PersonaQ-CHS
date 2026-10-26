import subprocess
from collections import defaultdict
from PIL import Image,ImageDraw
from compile_translation import ROOT,read,write
from encode_images_540 import DOTNET,HELPER
from check_roundtrip import parse_members
out=ROOT/'translation/feedback_543';src=out/'secondary_sources';src.mkdir(exist_ok=True)
records=[]
for row in read(out/'multi_texture_inventory.json'):
    parts=row['source'].split('::');raw=(ROOT/'data'/parts[0]).read_bytes()
    if len(parts)==2:raw=dict(parse_members(raw))[parts[1]]
    for i,t in enumerate(row['textures'][1:],1):
        name=f'{len(records):02}.ctpk';(src/name).write_bytes(raw[t['offset']:t['offset']+t['bytes']])
        records.append(dict(unit=name,source=row['source'],texture_index=i,**t))
subprocess.run([str(DOTNET),str(HELPER),'export','-i',str(src),'-o',str(out/'secondary_decoded')],check=True)
write(out/'secondary_textures.json',records)
for page in range((len(records)+5)//6):
    sheet=Image.new('RGB',(1040,900),'#444444');d=ImageDraw.Draw(sheet)
    for k,r in enumerate(records[page*6:page*6+6]):
        im=Image.open(out/'secondary_decoded'/(r['unit']+'.00.png')).convert('RGBA');im.thumbnail((510,265))
        x=k%2*520;y=k//2*300
        d.text((x+5,y+5),r['unit']+' '+r['source']+f" #{r['texture_index']}",fill='white')
        sheet.paste(im,(x+5,y+30),im)
    sheet.save(out/f'secondary_contact_{page}.png')
group=defaultdict(list)
for r in read(out/'enemy_candidates.json'):group[r['enemy']].append(r)
for name,rows in group.items():
    print('\n',name,'=>',rows[0]['expected'],'count',len(rows))
    for r in rows[:3]:print(r['key'],repr(r['translation']))
