"""587: inventory every changed UI label region (original vs current approved texture)."""
import json
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw,ImageFilter
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'translation/inventory_587';OUT.mkdir(exist_ok=True)
SKIP=('tutorial/','mapdat/tex/pic','title/fiction','title/logo','init/','event/model/')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
latest={}
for r in read(ROOT/'translation/build_540/images.json')['textures']:
    latest[(r['container'],r['texture_offset'])]=r
for r in read(ROOT/'translation/build_583/images.json')['textures']:
    latest[(r['container'],r['texture_offset'])]=r
regions=[];sheets=[]
for (container,_),r in sorted(latest.items()):
    source=r['source']
    if container.startswith(SKIP):continue
    a=Image.open(ROOT/source.replace('\\','/')).convert('RGBA');b=Image.open(ROOT/r['png'].replace('\\','/')).convert('RGBA')
    diff=ImageChops.difference(a,b).convert('L').point(lambda v:255 if v>0 else 0)
    grown=diff.filter(ImageFilter.MaxFilter(5))
    # connected components on grown mask
    w,h=grown.size;px=grown.load();seen=set()
    for y in range(h):
        for x in range(w):
            if px[x,y] and (x,y) not in seen:
                stack=[(x,y)];seen.add((x,y));x0=x1=x;y0=y1=y
                while stack:
                    cx,cy=stack.pop();x0=min(x0,cx);x1=max(x1,cx);y0=min(y0,cy);y1=max(y1,cy)
                    for nx,ny in((cx+1,cy),(cx-1,cy),(cx,cy+1),(cx,cy-1)):
                        if 0<=nx<w and 0<=ny<h and px[nx,ny] and (nx,ny) not in seen:seen.add((nx,ny));stack.append((nx,ny))
                box=(max(0,x0-1),max(0,y0-1),min(w,x1+2),min(h,y1+2))
                if (box[2]-box[0])*(box[3]-box[1])>=30:
                    regions.append(dict(id=len(regions),container=container,source=source,png=r['png'],box=box))
(OUT/'regions.json').write_text(json.dumps(regions,ensure_ascii=False,indent=1),encoding='utf-8')
# contact sheets: original | current, on grey and dark backgrounds
S=3;per_sheet=40;
for k in range(0,len(regions),per_sheet):
    chunk=regions[k:k+per_sheet];rows=[]
    for g in chunk:
        a=Image.open(ROOT/g['source'].replace('\\','/')).convert('RGBA').crop(g['box']);b=Image.open(ROOT/g['png'].replace('\\','/')).convert('RGBA').crop(g['box'])
        rows.append((g,a,b))
    colw=min(max(a.width for _,a,_ in rows),200)*S+10
    H=sum(min(a.height,60)*S+8 for _,a,_ in rows)+10;W=110+colw*2
    sheet=Image.new('RGB',(W,H),(70,70,78));d=ImageDraw.Draw(sheet);y=5
    for g,a,b in rows:
        d.text((4,y+2),f"#{g['id']} {Path(g['container']).stem}",fill='white')
        for i,im in enumerate((a,b)):
            im=im.crop((0,0,min(im.width,200),min(im.height,60)));bg=Image.new('RGBA',im.size,(70,70,78,255));bg.alpha_composite(im)
            sheet.paste(bg.resize((im.width*S,im.height*S),Image.Resampling.NEAREST),(110+i*colw,y))
        y+=min(a.height,60)*S+8
    p=OUT/f'sheet_{k//per_sheet:02}.png';sheet.save(p);sheets.append(p.name)
print(len(regions),'regions;',sheets)
