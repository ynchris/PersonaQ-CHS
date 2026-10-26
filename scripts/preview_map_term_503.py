"""Unify the floor-painting heading with existing tutorial text. PNG only."""
import json
from PIL import Image,ImageDraw,ImageFont,ImageChops
from preview_tutorials_468 import ROOT,digest
out=ROOT/'translation/previews_503';out.mkdir(exist_ok=True)
original=Image.open(ROOT/'export_base/mapdat/tex/map_tutorial.spr3.00.png').convert('RGBA')
previous=Image.open(ROOT/'translation/previews_502/map_tutorial.spr3.00.png').convert('RGBA')
im=previous.copy()
box=(282,19,487,36);text='地板涂色与擦除'
x0,y0,x1,y1=box
patch=Image.new('RGBA',((x1-x0)*4,(y1-y0)*4))
d=ImageDraw.Draw(patch);font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',52)
b=d.textbbox((0,0),text,font=font)
assert b[2]-b[0]<patch.width and b[3]-b[1]<patch.height
d.text(((patch.width-b[2]+b[0])/2-b[0],(patch.height-b[3]+b[1])/2-b[1]),text,font=font,fill='white')
im.paste(patch.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS),box[:2])
check=im.copy();check.paste(previous.crop(box),box[:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,previous).split())
target=out/'map_tutorial.spr3.00.png';im.save(target)
pair=Image.new('RGBA',(1032,128),'#555555')
pair.alpha_composite(original,(0,0));pair.alpha_composite(im,(520,0))
pair.resize((1548,192),Image.Resampling.NEAREST).save(out/'map_full_compare.png')
detail=Image.new('RGBA',(420,21),'#555555')
detail.alpha_composite(original.crop(box),(2,2));detail.alpha_composite(im.crop(box),(213,2))
detail.resize((1260,63),Image.Resampling.NEAREST).save(out/'floor_compare.png')
(out/'review.json').write_text(json.dumps(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),status='pending_user_visual_review',terminology_user_approved=True,text=text,box=box,outside_box_rgba_unchanged=True,supersedes='translation/previews_502/map_tutorial.spr3.00.png',encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
