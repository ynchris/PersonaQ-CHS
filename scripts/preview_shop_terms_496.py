"""Larger shop material labels; complete atlas preview, no binary writes."""
import json
from PIL import Image, ImageDraw, ImageFont, ImageChops
from preview_tutorials_468 import ROOT, digest

out = ROOT/'translation/previews_496'
out.mkdir(exist_ok=True)
previous = Image.open(ROOT/'translation/previews_495/shop.spr3.00.png').convert('RGBA')
original = Image.open(ROOT/'export_base/facility/shop.spr3.00.png').convert('RGBA')
im = previous.copy()
specs = [((4,214,66,233), '所需素材', 14, '#a51200', '#ffffd8'),
         ((28,234,80,253), '素材信息', 12, '#454545', 'white')]
for box,text,size,color,outline in specs:
    x0,y0,x1,y1 = box
    patch = Image.new('RGBA',((x1-x0)*4,(y1-y0)*4))
    d = ImageDraw.Draw(patch)
    font = ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',size*4)
    b = d.textbbox((0,0),text,font=font)
    assert b[2]-b[0]+8 <= patch.width
    assert b[3]-b[1]+8 <= patch.height
    d.text((4-b[0],(patch.height-(b[3]-b[1]))/2-b[1]),text,font=font,
           fill=color,stroke_width=4,stroke_fill=outline)
    im.paste(patch.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS),box[:2])
check = im.copy()
for box,*_ in specs:
    check.paste(previous.crop(box),box[:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,previous).split())
target = out/'shop.spr3.00.png'
im.save(target)
sheet = Image.new('RGBA',(532,284),'#eeeeee')
d = ImageDraw.Draw(sheet)
font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',12)
d.text((6,5),'日文原图',font=font,fill='black')
d.text((270,5),'汉化修订（完整贴图）',font=font,fill='black')
sheet.alpha_composite(original,(6,24))
sheet.alpha_composite(im,(270,24))
sheet.resize((1064,568),Image.Resampling.NEAREST).save(out/'shop_full_compare.png')
(out/'review.json').write_text(json.dumps(dict(
    png=target.relative_to(ROOT).as_posix(),sha256=digest(target),
    status='pending_user_visual_review',terminology_user_approved=True,
    edits=specs,unchanged_outside_two_boxes=True,
    supersedes='translation/previews_495/shop.spr3.00.png',
    encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
