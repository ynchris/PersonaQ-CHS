"""Translate shop accessory/item tabs. PNG preview only, no repacking."""
import json
from PIL import Image, ImageDraw, ImageFont, ImageChops
from preview_tutorials_468 import ROOT, digest

out=ROOT/'translation/previews_497'
out.mkdir(exist_ok=True)
previous=Image.open(ROOT/'translation/previews_496/shop.spr3.00.png').convert('RGBA')
im=previous.copy()
specs=[((171,52,220,69),'饰品',13),((172,70,220,86),'道具',13)]
for box,text,size in specs:
    x0,y0,x1,y1=box
    patch=Image.new('RGBA',((x1-x0)*4,(y1-y0)*4))
    d=ImageDraw.Draw(patch)
    font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',size*4)
    b=d.textbbox((0,0),text,font=font)
    assert b[2]-b[0]+8<=patch.width and b[3]-b[1]+8<=patch.height
    d.text(((patch.width-(b[2]-b[0]))/2-b[0],(patch.height-(b[3]-b[1]))/2-b[1]),text,font=font,fill='white')
    im.paste(patch.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS),box[:2])
check=im.copy()
for box,*_ in specs:check.paste(previous.crop(box),box[:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,previous).split())
target=out/'shop.spr3.00.png'
im.save(target)
# Neutral backdrop for visibility only; actual atlas retains transparency.
sheet=Image.new('RGBA',im.size,'#666666')
sheet.alpha_composite(im)
sheet.resize((768,768),Image.Resampling.NEAREST).save(out/'shop_full_preview.png')
(out/'review.json').write_text(json.dumps(dict(
    png=target.relative_to(ROOT).as_posix(),sha256=digest(target),
    status='pending_user_visual_review',edits=specs,
    unchanged_outside_two_boxes=True,
    preview_has_no_added_text=True,
    supersedes='translation/previews_496/shop.spr3.00.png',
    encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
