"""Inspect original quest status glyphs before exact replacement."""
from PIL import Image
from preview_tutorials_468 import ROOT
out=ROOT/'translation/previews_500';out.mkdir(exist_ok=True)
original=Image.open(ROOT/'export_base/facility/noffice.spr3.00.png').convert('RGBA')
crop=original.crop((323,175,459,213))
bg=Image.new('RGBA',crop.size,'#666666');bg.alpha_composite(crop)
bg.resize((1088,304),Image.Resampling.NEAREST).save(out/'status_inspect.png')
import json
from PIL import ImageDraw,ImageFont,ImageChops
from preview_tutorials_468 import digest
previous=Image.open(ROOT/'translation/previews_499/noffice.spr3.00.png').convert('RGBA')
im=previous.copy()
specs=[((326,197,364,210),'受理中',False),((372,178,410,191),'可报告',False),((371,196,398,211),'完成',True),((417,177,457,192),'已过期',True)]
for box,text,inverted in specs:
    x0,y0,x1,y1=box
    size=((x1-x0)*4,(y1-y0)*4)
    mask=Image.new('L',size)
    d=ImageDraw.Draw(mask);f=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',48)
    b=d.textbbox((0,0),text,font=f)
    assert b[2]-b[0]<=size[0]
    d.text(((size[0]-b[2]+b[0])/2-b[0],(size[1]-b[3]+b[1])/2-b[1]),text,font=f,fill=255)
    mask=mask.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS)
    if inverted:mask=ImageChops.invert(mask)
    patch=Image.new('RGBA',mask.size,'white');patch.putalpha(mask)
    im.paste(patch,box[:2])
check=im.copy()
for box,*_ in specs:check.paste(previous.crop(box),box[:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,previous).split())
target=out/'noffice.spr3.00.png';im.save(target)
pair=Image.new('RGBA',(1032,256),'#666666')
pair.alpha_composite(original,(0,0));pair.alpha_composite(im,(520,0))
pair.resize((1548,384),Image.Resampling.NEAREST).save(out/'noffice_compare.png')
details=Image.new('RGBA',(280,38),'#666666')
details.alpha_composite(original.crop((323,175,459,213)),(0,0))
details.alpha_composite(im.crop((323,175,459,213)),(144,0))
details.resize((1120,152),Image.Resampling.NEAREST).save(out/'status_compare.png')
(out/'review.json').write_text(json.dumps(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),status='pending_user_visual_review',edits=specs,outside_boxes_rgba_unchanged=True,checkmark_unchanged=True,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
