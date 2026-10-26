"""Skill tutorial PNG previews; no texture encoding."""
import json
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter
import preview_tutorials_468 as render
from preview_tutorials_468 import ROOT,label,digest

OUT=ROOT/'translation/previews_478'

def clean_light(im,box):
    patch=im.crop(box)
    mask=Image.new('L',patch.size)
    for y in range(patch.height):
        for x in range(patch.width):
            r,g,b,a=patch.getpixel((x,y))
            if min(r,g,b)>100 and max(r,g,b)-min(r,g,b)<65:mask.putpixel((x,y),255)
    mask=mask.filter(ImageFilter.MaxFilter(3))
    clean=patch.copy()
    for y in range(patch.height):
        for x in range(patch.width):
            if not mask.getpixel((x,y)):continue
            candidates=[]
            for yy in range(max(0,y-7),min(patch.height,y+8)):
                for xx in range(max(0,x-7),min(patch.width,x+8)):
                    if not mask.getpixel((xx,yy)):
                        candidates.append(((xx-x)**2+(yy-y)**2,xx,yy))
            if candidates:
                _,xx,yy=min(candidates);clean.putpixel((x,y),patch.getpixel((xx,yy)))
            else:clean.putpixel((x,y),(16,12,18,255))
    im.paste(clean,box[:2])

def overlay(im,box,text,size=8,angle=0):
    x0,y0,x1,y1=box
    ink=Image.new('RGBA',((x1-x0)*4,(y1-y0)*4))
    f=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',size*4)
    d=ImageDraw.Draw(ink);b=d.textbbox((0,0),text,font=f)
    tx=(ink.width-(b[2]-b[0]))//2-b[0] if angle else 0
    d.text((tx,(ink.height-(b[3]-b[1]))//2-b[1]),text,font=f,fill='white')
    if angle:ink=ink.rotate(angle,Image.Resampling.BICUBIC)
    im.alpha_composite(ink.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS),box[:2])

def main():
    OUT.mkdir(exist_ok=True)
    records=[]
    for n in (4,30):
        src=ROOT/f'export_base/tutorial/t{n:03}.ctpk.00.png'
        original=Image.open(src).convert('RGBA');im=original.copy();boxes=[]
        render.FONT='C:/Windows/Fonts/msyhbd.ttc'
        name='反叛' if n==4 else '玛哈塔尔卡加'
        b=(64,8,137,21);label(im,b,name,'white',original.getpixel((145,12)),size=9);boxes.append(b)
        for b,t in [((39,23,100,34),'持续５回合，' if n==4 else '持续３回合，'),
                    ((39,34,215,46),'提升自身暴击率。' if n==4 else '提升全体同伴的物理与属性攻击力。')]:
            clean_light(im,b);overlay(im,b,t,8);boxes.append(b)
        slots=[(24,66,88,77)] if n==4 else [(24,66,89,77),(119,66,184,77),(212,66,277,77),(72,124,137,136),(169,124,234,136)]
        for i,b in enumerate(slots):
            bg=original.getpixel((b[0]+5,b[1]))
            selected=(n==4 or i==0)
            label(im,b,name,'black' if selected else 'white','white' if selected else '#d00000',size=8)
            boxes.append(b)
        # Rotated 強化 label: only the white glyphs are removed, retaining the red arrow.
        b=(235,13,268,45);clean_light(im,b);overlay(im,b,'强化',11,45);boxes.append(b)
        for b,t in [((232,163,252,175),'全体'),((265,163,284,175),'返回')]:
            clean_light(im,b);overlay(im,b,t,8);boxes.append(b)
        restored=im.copy()
        for b in boxes:restored.paste(original.crop(b),b[:2])
        assert ImageChops.difference(restored,original).convert('RGB').getbbox() is None
        target=OUT/f't{n:03}.ctpk.00.png';im.save(target)
        pair=Image.new('RGBA',(592,184),'black');pair.paste(original.crop((0,0,296,184)),(0,0));pair.paste(im.crop((0,0,296,184)),(296,0))
        pair.resize((1184,368),Image.Resampling.NEAREST).save(OUT/f't{n:03}_compare.png')
        records.append(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),edit_boxes=boxes,status='pending_user_review',outside_boxes_unchanged=True))
    (OUT/'review.json').write_text(json.dumps(dict(images=records,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':main()
