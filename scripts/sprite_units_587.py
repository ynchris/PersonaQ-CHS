"""587: label units from SPR3 sprite records (box + name) overlapping translated pixels."""
import json,re,struct
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
from label_units_587 import ROOT,final_textures
from check_roundtrip import parse_members
OUT=ROOT/'translation/inventory_587'
def spr3_blob(container):
    raw=(ROOT/'data'/container).read_bytes()
    if raw[8:12]==b'SPR3':return raw,0
    if not container.endswith(('.bin','.arc')):return None,0
    for name,blob in parse_members(raw):
        if blob[8:12]==b'SPR3':
            return blob,raw.index(blob)
    return None,0
def sprites(blob):
    table=struct.unpack_from('<I',blob,28)[0];rows=[]
    for i in range(struct.unpack_from('<H',blob,22)[0]):
        p=struct.unpack_from('<I',blob,table+i*8+4)[0]
        name=blob[p+4:p+20].split(b'\0')[0].decode('cp932',errors='replace')
        rows.append(dict(index=i,name=name,texture=struct.unpack_from('<I',blob,p+20)[0],box=list(struct.unpack_from('<4i',blob,p+84))))
    return rows
def main():
    units=[];T=final_textures()
    for (container,off),r in sorted(T.items()):
        a=Image.open(ROOT/r['source']).convert('RGBA');b=Image.open(ROOT/r['png']).convert('RGBA')
        from redraw_labels_587 import diff_mask
        diff=diff_mask(a,b)
        blob,base=spr3_blob(container)
        found=[]
        if blob:
            ctpk=[m.start() for m in re.finditer(b'CTPK',blob)];idx=ctpk.index(off-base) if (off-base) in ctpk else ctpk.index(off) if off in ctpk else 0
            seen=set()
            for s in sprites(blob):
                x0,y0,x1,y1=s['box']
                if s['texture']!=idx or x1<=x0 or y1<=y0 or tuple(s['box']) in seen:continue
                if diff.crop((x0,y0,x1,y1)).getbbox():
                    seen.add(tuple(s['box']));found.append(s)
        # Changed pixels not covered by any sprite box -> leftover regions (ctpk-only textures etc.)
        cover=Image.new('L',a.size)
        for s in found:ImageDraw.Draw(cover).rectangle([s['box'][0],s['box'][1],s['box'][2]-1,s['box'][3]-1],fill=255)
        left=ImageChops.subtract(diff,cover).getbbox()
        for s in found:units.append(dict(container=container,texture_offset=off,png=r['png'],source=r['source'],sprite=s['index'],name=s['name'],box=s['box']))
        if left:units.append(dict(container=container,texture_offset=off,png=r['png'],source=r['source'],sprite=None,name='(uncovered)',box=list(left)))
    (OUT/'sprite_units.json').write_text(json.dumps(units,ensure_ascii=False,indent=1),encoding='utf-8')
    # thumbnails: original | current
    cache={};per=45;S=3
    for k in range(0,len(units),per):
        chunk=units[k:k+per];rh=0;rows=[]
        for u in chunk:
            for p in (u['source'],u['png']):
                if p not in cache:cache[p]=Image.open(ROOT/p).convert('RGBA')
            x0,y0,x1,y1=u['box'];x1=min(x1,x0+150);y1=min(y1,y0+40)
            rows.append((u,cache[u['source']].crop((x0,y0,x1,y1)),cache[u['png']].crop((x0,y0,x1,y1))))
        H=sum(a.height*S+6 for _,a,_ in rows)+6;W=1000
        sheet=Image.new('RGB',(W,H),(90,90,100));d=ImageDraw.Draw(sheet);y=4
        for u,a,b in rows:
            d.text((2,y),f"{k+chunk.index(u)} {Path(u['container']).stem}#{u['sprite']} {u['name']}",fill='yellow')
            for i,im in enumerate((a,b)):
                bg=Image.new('RGBA',im.size,(90,90,100,255));bg.alpha_composite(im)
                sheet.paste(bg.resize((im.width*S,im.height*S),Image.Resampling.NEAREST),(260+i*370,y))
            y+=a.height*S+6
        sheet.save(OUT/f'sprites_{k//per}.png')
    print(len(units),'units;',sum(u['sprite'] is None for u in units),'uncovered regions')
if __name__=='__main__':main()
