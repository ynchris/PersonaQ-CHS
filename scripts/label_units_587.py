"""587: split each UI texture's changed area into line-level label units and attach known texts."""
import json,re,glob
from pathlib import Path
from PIL import Image,ImageChops,ImageFilter
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def final_textures():
    L={}
    for f in ['translation/build_540/images.json','translation/build_583/images.json']:
        for r in read(ROOT/f)['textures']:L[(r['container'],r['texture_offset'])]=dict(r,png=r['png'].replace('\\','/'),source=r['source'].replace('\\','/'))
    # 585: approved party help labels supersede 522 (from the other session).
    for k,r in L.items():
        if k[0]=='facility/party.spr3' and r['png'].endswith('previews_522/party.spr3.00.png'):
            rv=read(ROOT/'translation/previews_585/C_10.5/review.json');assert rv['status']=='approved_by_user'
            r['png']='translation/previews_585/C_10.5/party.spr3.00.png'
    skip=('tutorial/','mapdat/tex/pic','title/fiction','title/logo','init/','event/model/')
    return {k:r for k,r in L.items() if not k[0].startswith(skip)}
def specs():
    pat=re.compile(r"\(?\[?\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\]?\)?\s*,\s*'([^']*[\u4e00-\u9fff][^']*)'")
    out=[]
    for f in sorted(glob.glob(str(ROOT/'preview_*.py'))):
        for a in pat.findall(Path(f).read_text(encoding='utf-8')):out.append(dict(box=tuple(map(int,a[:4])),text=a[4],script=Path(f).name))
    return out
def components(mask,kx=4,ky=1):
    """Connected components after anisotropic dilation (merges glyphs of one line)."""
    w,h=mask.size;px=mask.load();on=set((x,y) for y in range(h) for x in range(w) if px[x,y])
    seen=set();comps=[]
    for p in on:
        if p in seen:continue
        stack=[p];seen.add(p);xs=[];ys=[]
        while stack:
            x,y=stack.pop();xs.append(x);ys.append(y)
            for dx in range(-kx,kx+1):
                for dy in range(-ky,ky+1):
                    q=(x+dx,y+dy)
                    if q in on and q not in seen:seen.add(q);stack.append(q)
        comps.append((min(xs),min(ys),max(xs)+1,max(ys)+1))
    return sorted(comps,key=lambda b:(b[1],b[0]))
def units(r):
    a=Image.open(ROOT/r['source']).convert('RGBA');b=Image.open(ROOT/r['png']).convert('RGBA')
    # Chinese ink of current approved image: opaque pixels that differ from original
    d=ImageChops.difference(a,b).convert('L').point(lambda v:255 if v>24 else 0)
    ink=Image.composite(d,Image.new('L',a.size),b.getchannel('A').point(lambda v:255 if v>40 else 0))
    return a,b,components(ink)
if __name__=='__main__':
    S=specs();rows=[]
    for (container,off),r in sorted(final_textures().items()):
        a,b,comps=units(r)
        for c in comps:
            if (c[2]-c[0])*(c[3]-c[1])<12:continue
            hits=[s for s in S if s['box'][0]<c[2] and c[0]<s['box'][2] and s['box'][1]<c[3] and c[1]<s['box'][3]]
            rows.append(dict(container=container,texture_offset=off,png=r['png'],source=r['source'],ink=c,candidates=sorted({h['text'] for h in hits})))
    (ROOT/'translation/inventory_587/units.json').write_text(json.dumps(rows,ensure_ascii=False,indent=1),encoding='utf-8')
    print(len(rows),'units;',sum(1 for r in rows if len(r['candidates'])==1),'with a unique text candidate')
