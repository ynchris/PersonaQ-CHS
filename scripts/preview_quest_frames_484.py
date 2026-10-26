"""User-corrected colors: black text/frame, light cyan interior. PNG only."""
import json
from PIL import Image,ImageDraw,ImageChops
import preview_tutorials_468 as render
from preview_tutorials_468 import ROOT,label,digest

out=ROOT/'translation/previews_484';out.mkdir(exist_ok=True)
original=Image.open(ROOT/'export_base/tutorial/t026.ctpk.00.png').convert('RGBA')
old=Image.open(ROOT/'translation/previews_482/t026.ctpk.00.png').convert('RGBA')
im=old.copy()
render.FONT='C:/Windows/Fonts/msyhbd.ttc'
frames=[(31,46,60,57),(31,60,60,71)]
for x0,y0,x1,y1 in frames:
    ImageDraw.Draw(im).rectangle((x0,y0,x1-1,y1-1),fill='#00d6e5',outline='black',width=1)
    label(im,(x0+1,y0+1,x1-1,y1-1),'受理中','black','#00d6e5',size=9,align='center')
check=im.copy()
for b in frames:check.paste(old.crop(b),b[:2])
assert ImageChops.difference(check,old).convert('RGB').getbbox() is None
target=out/'t026.ctpk.00.png';im.save(target)
pair=Image.new('RGBA',(592,184),'black')
pair.paste(original.crop((0,0,296,184)),(0,0));pair.paste(im.crop((0,0,296,184)),(296,0))
pair.resize((1184,368),Image.Resampling.NEAREST).save(out/'t026_compare.png')
im.crop((28,43,63,74)).resize((420,372),Image.Resampling.NEAREST).save(out/'status_detail.png')
(out/'review.json').write_text(json.dumps(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),background='#00d6e5',foreground='#000000',frame='#000000',font_size=9,outside_tags_unchanged=True,status='pending_user_review',supersedes='previews_483 (rejected colors)',encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
