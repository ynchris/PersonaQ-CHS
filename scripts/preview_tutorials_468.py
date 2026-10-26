"""PNG-only tutorial labels; no texture encoding or game packaging."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw, ImageFont, ImageChops

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'translation/previews_468'
FONT = 'C:/Windows/Fonts/msyh.ttc'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def label(im, box, text, color, background, size=12, align='left'):
    x0,y0,x1,y1=box
    w,h=x1-x0,y1-y0
    patch=Image.new('RGBA',(w*4,h*4),background)
    d=ImageDraw.Draw(patch)
    f=ImageFont.truetype(FONT,size*4)
    b=d.textbbox((0,0),text,font=f)
    tw,th=b[2]-b[0],b[3]-b[1]
    assert tw<=w*4 and th<=h*4, (text,box,tw,th)
    x=(w*4-tw)//2 if align=='center' else 0
    d.text((x-b[0],(h*4-th)//2-b[1]),text,font=f,fill=color)
    im.paste(patch.resize((w,h),Image.Resampling.LANCZOS),(x0,y0))

def main():
    OUT.mkdir(exist_ok=True)
    approved=[]
    for p in ['translation/previews_467/t043.ctpk.00.png','translation/previews_466/t044.ctpk.00.png']:
        approved.append(dict(png=p,sha256=digest(ROOT/p),status='user_approved'))
    (OUT/'prior_approvals.json').write_text(json.dumps(approved,indent=2),encoding='utf-8')
    specs={
        2:[((38,47,132,63),'角色的','white',(255,35,35,255),'center'),
           ((160,47,260,63),'副人格面具的','white',(30,159,255,255),'center'),
           ((54,63,116,80),'HP与SP','white',(255,35,35,255),'center'),
           ((179,63,242,80),'HP与SP','white',(30,159,255,255),'center')],
        6:[((56,21,82,37),'优先','black','white','left'),
           ((209,21,235,37),'次之','black','white','left'),
           ((97,73,159,90),'无法战斗','black','white','left'),
           ((191,73,225,90),'石化','black','white','left'),
           ((97,97,148,114),'诅咒','black','white','left'),
           ((191,97,225,114),'中毒','black','white','left'),
           ((97,121,148,138),'睡眠','black','white','left'),
           ((191,121,225,138),'混乱','black','white','left'),
           ((97,145,148,162),'麻痹','black','white','left')]
    }
    records=[]
    for number,entries in specs.items():
        src=ROOT/f'export_base/tutorial/t{number:03}.ctpk.00.png'
        original=Image.open(src).convert('RGBA')
        im=original.copy()
        mask=Image.new('L',im.size,0)
        for box,text,color,bg,align in entries:
            # Reuse exact flat label background from source; never alter arrows/icons.
            if number==2:
                bg=original.getpixel((35 if box[0]<150 else 160,44))
            size=(14 if text=='HP与SP' else 13) if number==2 else 12
            label(im,box,text,color,bg,size=size,align=align)
            ImageDraw.Draw(mask).rectangle((box[0],box[1],box[2]-1,box[3]-1),fill=255)
        diff=ImageChops.difference(im,original).convert('RGB')
        outside=Image.composite(diff,Image.new('RGB',im.size),ImageChops.invert(mask))
        assert outside.getbbox() is None
        target=OUT/f't{number:03}.ctpk.00.png'
        im.save(target)
        crop=im.crop((0,0,296,184))
        crop.resize((888,552),Image.Resampling.NEAREST).save(OUT/f't{number:03}_preview.png')
        comparison=Image.new('RGBA',(592,184),'black')
        comparison.paste(original.crop((0,0,296,184)),(0,0))
        comparison.paste(crop,(296,0))
        comparison.resize((1184,368),Image.Resampling.NEAREST).save(OUT/f't{number:03}_compare.png')
        records.append(dict(source=str(src.relative_to(ROOT)),png=str(target.relative_to(ROOT)),sha256=digest(target),status='pending_user_review',outside_rectangles_unchanged=True,labels=[e[1] for e in entries]))
    (OUT/'review.json').write_text(json.dumps(dict(encoded=False,packaged=False,images=records),ensure_ascii=False,indent=2),encoding='utf-8')
    print('Two PNG previews generated; no encoding or packaging.')

if __name__=='__main__':
    main()
