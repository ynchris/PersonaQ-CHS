"""Read-only keyboard source investigation; no game asset modifications."""
import json, re, struct
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent
out=ROOT/'translation/keyboard_524';out.mkdir(exist_ok=True)
src=ROOT/'export_base/init/nameentry.arc_key_board_button.ctpk.00.png'
im=Image.open(src).convert('RGBA')
canvas=Image.new('RGBA',(1024,512),'#222222');canvas.alpha_composite(im)
light=Image.new('RGBA',im.size,'#cccccc');light.alpha_composite(im);canvas.paste(light,(512,0))
canvas.save(out/'keyboard_dark_light.png')
terms=['おまかせ','キャンセル','決定','記号','小字','かな','カナ','運命は','志ある者','志なき者','権利者']
rows=[]
for rel in ['exefs/code.bin','update/exefs/code.bin','data/init/nameentry.arc']:
    raw=(ROOT/rel).read_bytes()
    hits=[]
    for term in terms:
        for enc in ['utf-16-be','utf-32-le','utf-32-be']:
            needle=term.encode(enc);pos=raw.find(needle)
            if pos>=0:hits.append(dict(term=term,encoding=enc,offset=pos))
    names=[m.group().decode('ascii') for m in re.finditer(rb'[A-Za-z0-9_./-]{3,}\.(?:bclyt|bclan|bcfnt|ctpk|tbl|bmd|bcma|bcskl|bflim|bin)',raw)]
    rows.append(dict(source=rel,header=raw[:128].hex(),names=sorted(set(names)),hits=hits))
(out/'sources.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
for row in rows:
    print(row['source'],'additional encoding hits:',row['hits'])
    print('keyboard/layout names:',[n for n in row['names'] if any(s in n.lower() for s in ['key','name','lyt','font'])][:35])
print('archive header:',rows[-1]['header'])
