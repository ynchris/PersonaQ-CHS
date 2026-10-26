"""Shop UI labels, PNG-only approval sheet; no binary changes."""
import json
from PIL import Image,ImageDraw,ImageFont,ImageChops
from preview_tutorials_468 import ROOT,digest
out=ROOT/'translation/previews_494';out.mkdir(exist_ok=True)
src=ROOT/'export_base/facility/shop.spr3.00.png'
original=Image.open(src).convert('RGBA');im=original.copy()
specs=[((176,141,218,159),'持有数',11,'#dc8181'),
       ((220,141,236,159),'个',11,'#dc8181'),
       ((4,214,66,233),'所需材料',12,'#a51200'),
       ((28,234,80,253),'材料信息',11,'#454545'),
       ((192,214,246,234),'多选',11,'#454545')]
for box,text,size,color in specs:
    x0,y0,x1,y1=box
    patch=Image.new('RGBA',((x1-x0)*4,(y1-y0)*4))
    draw=ImageDraw.Draw(patch);font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',size*4)
    b=draw.textbbox((0,0),text,font=font)
    assert b[2]-b[0]+8<=patch.width
    outline='#ffffd8' if text=='所需材料' else 'white'
    draw.text((4-b[0],(patch.height-(b[3]-b[1]))/2-b[1]),text,font=font,fill=color,stroke_width=4 if y0>200 else 0,stroke_fill=outline)
    im.paste(patch.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS),box[:2])
check=im.copy()
for box,*_ in specs:check.paste(original.crop(box),box[:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,original).split())
target=out/'shop.spr3.00.png';im.save(target)
sheet=Image.new('RGBA',(270,30+28*len(specs)),'#eeeeee')
d=ImageDraw.Draw(sheet);f=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',12)
d.text((8,7),'原图',font=f,fill='black');d.text((143,7),'汉化预览',font=f,fill='black')
for row,(box,*_) in enumerate(specs):
    for col,source in enumerate([original,im]):sheet.alpha_composite(source.crop(box),(col*135+8,30+row*28))
sheet.resize((810,sheet.height*3),Image.Resampling.NEAREST).save(out/'shop_labels_compare.png')
(out/'review.json').write_text(json.dumps(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),status='pending_user_review',edits=specs,outside_labels_rgba_unchanged=True,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
