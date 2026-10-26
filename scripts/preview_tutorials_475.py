"""Map label previews only; keep arrows and source screenshots intact elsewhere."""
import json
from PIL import Image, ImageDraw, ImageFont, ImageChops
from preview_tutorials_468 import ROOT,digest,label

OUT=ROOT/'translation/previews_475'

def main():
    OUT.mkdir(exist_ok=True)
    records=[]
    for n in (20,):
        source=ROOT/f'export_base/tutorial/t{n:03}.ctpk.00.png'
        original=Image.open(source).convert('RGBA');im=original.copy()
        boxes=[]
        if n==20:
            box=(173,97,205,108)
            label(im,box,'捷径','#505050','white',size=9,align='center')
            for y in range(box[1],box[3]):
                for x in range(box[0],box[2]):
                    if x+y>=305:im.putpixel((x,y),original.getpixel((x,y)))
            boxes.append(box)
            texts=['捷径']
        else:
            texts=['方位固定','视野方向固定']
            for box,text in zip([(22,108,85,127),(152,153,243,171)],texts):
                x0,y0,x1,y1=box
                # Restore the regular map grid from two cells above, not by blurring.
                patch=original.crop((x0,y0-28,x1,y1-28))
                im.paste(patch,(x0,y0))
                scale=4
                ink=Image.new('RGBA',((x1-x0)*scale,(y1-y0)*scale))
                d=ImageDraw.Draw(ink);f=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',13*scale)
                b=d.textbbox((0,0),text,font=f)
                d.text((-b[0],((y1-y0)*scale-(b[3]-b[1]))//2-b[1]),text,font=f,fill='white',stroke_width=2,stroke_fill='#727272')
                ink=ink.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS)
                im.alpha_composite(ink,(x0,y0));boxes.append(box)
        restored=im.copy()
        for box in boxes:restored.paste(original.crop(box),box[:2])
        assert ImageChops.difference(restored,original).convert('RGB').getbbox() is None
        target=OUT/f't{n:03}.ctpk.00.png';im.save(target)
        pair=Image.new('RGBA',(592,184),'black');pair.paste(original.crop((0,0,296,184)),(0,0));pair.paste(im.crop((0,0,296,184)),(296,0))
        pair.resize((1184,368),Image.Resampling.NEAREST).save(OUT/f't{n:03}_compare.png')
        records.append(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),texts=texts,edit_boxes=boxes,status='pending_user_review',outside_boxes_unchanged=True))
    (OUT/'review.json').write_text(json.dumps(dict(images=records,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':main()
