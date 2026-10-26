"""Mode labels in battle tutorial screenshots; PNG-only review."""
import json
from PIL import Image, ImageDraw, ImageFont, ImageChops
from preview_tutorials_468 import ROOT,digest

OUT=ROOT/'translation/previews_474'

def main():
    OUT.mkdir(exist_ok=True)
    records=[]
    for n in (10,11,12):
        src=ROOT/f'export_base/tutorial/t{n:03}.ctpk.00.png'
        original=Image.open(src).convert('RGBA')
        im=original.copy()
        # The bar is one flat-color band; source screenshots have differing crops.
        box=(8,133,68,143) if n==10 else ((8,132,68,142) if n==11 else (21,130,72,140))
        text='狂欢模式' if n==10 else '过热'
        x0,y0,x1,y1=box
        # Sample text-free row within the blue bar at each x, preserving dimming.
        sample_x=74 if n in (10,11) else 80
        for x in range(x0,x1):
            for y in range(y0,y1):
                bg=original.getpixel((sample_x,y))
                if n==10 and x<40:
                    bg=tuple(round(c*.5) for c in bg[:3])+(255,)
                im.putpixel((x,y),bg)
        mask=Image.new('L',((x1-x0)*4,(y1-y0)*4),0)
        draw=ImageDraw.Draw(mask)
        f=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',8*4)
        b=draw.textbbox((0,0),text,font=f)
        draw.text((-b[0],(mask.height-(b[3]-b[1]))//2-b[1]),text,font=f,fill=255)
        mask=mask.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS)
        ink=Image.new('RGBA',mask.size,'white')
        if n==10:
            for x in range(mask.width):
                if x+x0<40:
                    for y in range(mask.height):ink.putpixel((x,y),(150,150,150,255))
        im.paste(ink,(x0,y0),mask)
        # Preserve every annotation pixel crossing the edited label.
        red_count=0
        for y in range(y0,y1):
            for x in range(x0,x1):
                p=original.getpixel((x,y));r,g,b,a=p
                if r>50 and r>g*1.5 and r>b*1.5:
                    im.putpixel((x,y),p);red_count+=1
        restored=im.copy();restored.paste(original.crop(box),box[:2])
        assert ImageChops.difference(restored,original).convert('RGB').getbbox() is None
        target=OUT/f't{n:03}.ctpk.00.png';im.save(target)
        pair=Image.new('RGBA',(592,184),'black')
        pair.paste(original.crop((0,0,296,184)),(0,0));pair.paste(im.crop((0,0,296,184)),(296,0))
        pair.resize((1184,368),Image.Resampling.NEAREST).save(OUT/f't{n:03}_compare.png')
        original.crop((4,124,124,147)).resize((960,184),Image.Resampling.NEAREST).save(OUT/f't{n:03}_source_detail.png')
        records.append(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),source=src.relative_to(ROOT).as_posix(),text=text,edit_box=box,red_pixels_preserved=red_count,status='pending_user_review',outside_box_unchanged=True))
    (OUT/'review.json').write_text(json.dumps(dict(images=records,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
    print('3 previews; no binary writes.')

if __name__=='__main__':main()
