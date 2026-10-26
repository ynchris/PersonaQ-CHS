"""Read-only contact sheets to locate opening quotation textures."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
out=ROOT/'translation/inspection_528';out.mkdir(exist_ok=True)
import sys
group=sys.argv[1] if len(sys.argv)>1 else 'cutin'
assert group in ['cutin','opening','misc']
files=sorted((ROOT/'export_base/event/cutin').glob('*.png')) if group=='cutin' else sorted(p for folder in (['title','photo','font','init'] if group=='opening' else ['blank_board','staff','dungeon_in','attraction']) for p in (ROOT/'export_base'/folder).glob('*.png'))
seen=set();unique=[]
for p in files:
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    if h not in seen:unique.append(p);seen.add(h)
for start in range(0,len(unique),64):
    canvas=Image.new('RGB',(1024,1024),'#222222');d=ImageDraw.Draw(canvas)
    for i,p in enumerate(unique[start:start+64]):
        im=Image.open(p).convert('RGBA');im.thumbnail((124,109))
        x=(i%8)*128;y=(i//8)*128
        canvas.paste(im,(x,y),im);d.text((x,y+110),str(start+i)+' '+p.name[:4],fill='white')
    canvas.save(out/f'{group}_{start//64}.png')
(out/f'{group}_index.json').write_text(json.dumps([p.relative_to(ROOT).as_posix() for p in unique],indent=2),encoding='utf-8')
print('Unique cutin textures:',len(unique),'sheets:',(len(unique)+63)//64)
