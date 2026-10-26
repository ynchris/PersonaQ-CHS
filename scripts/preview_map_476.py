"""Minimal glyph edits: preserve existing Chinese-compatible labels and arrows."""
import json
from PIL import Image, ImageDraw, ImageFont, ImageChops
from preview_tutorials_468 import ROOT,digest

out=ROOT/'translation/previews_477'
out.mkdir(exist_ok=True)
src=ROOT/'export_base/tutorial/t038.ctpk.00.png'
original=Image.open(src).convert('RGBA')
im=original.copy()
# Only 角→位 and 視→视 need editing; the other glyphs are already correct.
# Donors use the same columns and whole grid-cell offsets, away from the arrow.
edits=[((37,109,52,125),'位',28),((151,153,167,171),'视',56)]
for box,text,dy in edits:
    x0,y0,x1,y1=box
    im.paste(original.crop((x0,y0-dy,x1,y1-dy)),(x0,y0))
    ink=Image.new('RGBA',((x1-x0)*4,(y1-y0)*4))
    d=ImageDraw.Draw(ink);f=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',15*4)
    b=d.textbbox((0,0),text,font=f)
    d.text(((ink.width-(b[2]-b[0]))//2-b[0],(ink.height-(b[3]-b[1]))//2-b[1]),text,font=f,fill='white',stroke_width=2,stroke_fill='#727272')
    im.alpha_composite(ink.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS),(x0,y0))
restored=im.copy()
for box,_,_ in edits:restored.paste(original.crop(box),box[:2])
assert ImageChops.difference(restored,original).convert('RGB').getbbox() is None
target=out/'t038.ctpk.00.png';im.save(target)
pair=Image.new('RGBA',(592,184),'black')
pair.paste(original.crop((0,0,296,184)),(0,0));pair.paste(im.crop((0,0,296,184)),(296,0))
pair.resize((1184,368),Image.Resampling.NEAREST).save(out/'t038_compare.png')
(out/'review.json').write_text(json.dumps(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),edits=edits,texts=['方位固定','视野方向固定'],status='pending_user_review',outside_boxes_unchanged=True,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
