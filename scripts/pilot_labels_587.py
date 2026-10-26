"""587 pilot: redraw a subset of units and build original | current | FZ comparison."""
import json,sys
from pathlib import Path
from PIL import Image,ImageDraw
from redraw_labels_587 import ROOT,redraw_unit,read
U=read(ROOT/'translation/inventory_587/sprite_units.json')
TEXTS=read(ROOT/'translation/inventory_587/label_texts.json')
OUT=ROOT/'translation/previews_587';OUT.mkdir(exist_ok=True)
ids=[int(x) for a in sys.argv[1].split(',') for x in (range(int(a.split('-')[0]),int(a.split('-')[1])+1) if '-' in a else [a])]
tex={};log=[];fails=[]
for i in ids:
    cfg=TEXTS.get(str(i))
    if not cfg or cfg=='skip':continue
    if isinstance(cfg,(str,list)):cfg={'text':cfg}
    u=U[i];k=(u['png'])
    if k not in tex:tex[k]=[Image.open(ROOT/u['source']).convert('RGBA'),Image.open(ROOT/u['png']).convert('RGBA'),None]
    o,c,n=tex[k];n=n or c.copy()
    try:r=redraw_unit(n,o,u,cfg)
    except AssertionError as e:print('FAIL',i,cfg.get('text'),e);fails.append(i);r=None
    if r:tex[k][2],info=r;log.append(dict(unit=i,**info))
    else:tex[k][2]=n
S=4;rows=[]
for i in ids:
    if str(i) not in TEXTS or TEXTS[str(i)]=='skip':continue
    u=U[i];o,c,n=tex[u['png']];x0,y0,x1,y1=u['box'];x1=min(x1,x0+130);y1=min(y1,y0+50)
    rows.append((i,[im.crop((x0,y0,x1,y1)) for im in (o,c,n)]))
W=40+3*(130*S+10);H=sum(r[1][0].height*S+6 for r in rows)+20
sheet=Image.new('RGB',(W,H),(96,96,106));d=ImageDraw.Draw(sheet);y=18
for k,t in enumerate(['original','current','FZ redraw']):d.text((40+k*(130*S+10),2),t,fill='white')
for i,ims in rows:
    d.text((2,y),str(i),fill='yellow')
    for k,im in enumerate(ims):
        bg=Image.new('RGBA',im.size,(96,96,106,255));bg.alpha_composite(im)
        sheet.paste(bg.resize((im.width*S,im.height*S),Image.Resampling.NEAREST),(40+k*(130*S+10),y))
    y+=ims[0].height*S+6
name=sys.argv[2] if len(sys.argv)>2 else 'pilot'
sheet.save(OUT/f'{name}.png');(OUT/f'{name}.json').write_text(json.dumps(log,ensure_ascii=False,indent=1),encoding='utf-8')
for k,(o,c,n) in tex.items():
    if n is not None:n.save(OUT/(Path(k).parent.name+'_'+Path(k).name))
print(OUT/f'{name}.png')
