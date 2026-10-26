"""Restore original status-tag frames without altering approved text or other UI."""
import json
from collections import Counter
from PIL import Image,ImageChops
import preview_tutorials_468 as render
from preview_tutorials_468 import ROOT,digest,label

out=ROOT/'translation/previews_483';out.mkdir(exist_ok=True)
original=Image.open(ROOT/'export_base/tutorial/t026.ctpk.00.png').convert('RGBA')
old=Image.open(ROOT/'translation/previews_482/t026.ctpk.00.png').convert('RGBA')
pair=Image.new('RGBA',(80,40),'black')
pair.paste(original.crop((26,40,66,80)),(0,0));pair.paste(old.crop((26,40,66,80)),(40,0))
pair.resize((800,400),Image.Resampling.NEAREST).save(out/'frame_inspection.png')
im=old.copy()
render.FONT='C:/Windows/Fonts/msyhbd.ttc'
boxes=[(31,45,60,57),(31,59,60,71)]
frames=[(31,46,60,57),(31,60,60,71)]
colors=Counter(original.crop((32,47,59,56)).getdata())
bg=max((p for p in colors if p[1]<130),key=colors.get)
fg=max((p for p in colors if p[1]>145 and p[0]<80),key=colors.get)
for box,frame in zip(boxes,frames):
    im.paste(original.crop(box),box[:2])
    x0,y0,x1,y1=frame
    inner=(x0+1,y0+1,x1-1,y1-1)
    label(im,inner,'受理中',fg,bg,size=9,align='center')
    # Frame perimeter is copied verbatim, not redrawn or approximated.
    for x in range(x0,x1):
        assert im.getpixel((x,y0))==original.getpixel((x,y0))
        assert im.getpixel((x,y1-1))==original.getpixel((x,y1-1))
    for y in range(y0,y1):
        assert im.getpixel((x0,y))==original.getpixel((x0,y))
        assert im.getpixel((x1-1,y))==original.getpixel((x1-1,y))
check=im.copy()
for box in boxes:check.paste(old.crop(box),box[:2])
assert ImageChops.difference(check,old).convert('RGB').getbbox() is None
target=out/'t026.ctpk.00.png';im.save(target)
pair=Image.new('RGBA',(592,184),'black')
pair.paste(original.crop((0,0,296,184)),(0,0));pair.paste(im.crop((0,0,296,184)),(296,0))
pair.resize((1184,368),Image.Resampling.NEAREST).save(out/'t026_compare.png')
(out/'review.json').write_text(json.dumps(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),background=bg,foreground=fg,font_size=9,original_frame_perimeters_preserved=True,outside_tags_unchanged=True,status='pending_user_review',encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
