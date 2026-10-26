"""Attribute, stat and system-menu tutorials: PNG review only."""
import json
from PIL import Image, ImageDraw, ImageChops
import preview_tutorials_468 as rendering
from preview_tutorials_468 import ROOT, label, digest

OUT=ROOT/'translation/previews_470'

def main():
    OUT.mkdir(exist_ok=True)
    records=[]
    for n in (34,36,25):
        src=ROOT/f'export_base/tutorial/t{n:03}.ctpk.00.png'
        original=Image.open(src).convert('RGBA')
        im=original.copy()
        boxes=[]
        labels=[]
        def put(box,text,size=12,color='black',bg='white',bold=False):
            rendering.FONT='C:/Windows/Fonts/msyhbd.ttc' if bold else 'C:/Windows/Fonts/msyh.ttc'
            label(im,box,text,color,bg,size=size)
            boxes.append(box)
            labels.append(text)
        if n==34:
            put((19,16,84,34),'属性效果',14,'#980000',bold=True)
            for y,text in zip((39,60,81,102,123,144),('火炎属性','电击属性','光属性','冰结属性','疾风属性','暗属性')):
                put((90,y,153,y+18),text)
            for y,text in zip((39,60,81),('斩击属性','突刺属性','打击属性')):
                put((188,y,251,y+18),text)
            # Keep the 1px icon frames; replace Japanese-only interior glyphs.
            for box,text,bg in [((70,104,83,117),'冰','#075976'),
                                ((70,125,83,138),'风','#10685a'),
                                ((70,146,83,159),'暗','#393939'),
                                ((170,41,183,54),'斩','#008dd7'),
                                ((170,83,183,96),'坏','#008dd7')]:
                put(box,text,12,'white',bg)
        elif n==36:
            put((23,19,123,38),'能力提升效果',14,'#980000',bold=True)
            for y,text in zip((49,70,91,112,133),('力','魔','速','耐','运')):
                put((78,y,96,y+18),text)
            put((156,90,206,108),'命中率')
            put((156,111,252,129),'暴击率')
            put((60,136,73,149),'运',12,'white','#60d400')
        else:
            # Preserve dimmed screenshot colors and the red dashed highlight.
            put((21,42,45,54),'委托',9,'#101010',original.getpixel((24,43)))
            for y,text in [(55,'教程'),(69,'设置'),(83,'读取存档'),(97,'返回标题')]:
                put((21,y,91,y+14),text,9,'#919500','#101010')
            # The tutorial's red highlight crosses the second menu row.
            # Restore every red annotation pixel, including its dim edge.
            for y in range(30,75):
                for x in range(7,60):
                    r,g,b,a=original.getpixel((x,y))
                    if r>50 and r>g*1.5 and r>b*1.5:
                        im.putpixel((x,y),(r,g,b,a))
        mask=Image.new('L',im.size,0)
        for x0,y0,x1,y1 in boxes:
            ImageDraw.Draw(mask).rectangle((x0,y0,x1-1,y1-1),fill=255)
        diff=ImageChops.difference(im,original)
        for mode in ('RGB','RGBA'):
            assert Image.composite(diff.convert(mode),Image.new(mode,im.size),ImageChops.invert(mask)).getbbox() is None
        target=OUT/f't{n:03}.ctpk.00.png'
        im.save(target)
        pair=Image.new('RGBA',(592,184),'black')
        pair.paste(original.crop((0,0,296,184)),(0,0))
        pair.paste(im.crop((0,0,296,184)),(296,0))
        pair.resize((1184,368),Image.Resampling.NEAREST).save(OUT/f't{n:03}_compare.png')
        records.append(dict(source=src.relative_to(ROOT).as_posix(),png=target.relative_to(ROOT).as_posix(),sha256=digest(target),labels=labels,edit_boxes=boxes,outside_boxes_unchanged=True,status='pending_user_review'))
    (OUT/'review.json').write_text(json.dumps(dict(images=records,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
    print('3 PNG previews generated, no encoding or packaging.')

if __name__=='__main__':
    main()
