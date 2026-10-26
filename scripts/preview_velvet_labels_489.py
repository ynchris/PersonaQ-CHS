"""Velvet Room atlas labels, isolated transparent regions; previews only."""
import json
from PIL import Image,ImageDraw,ImageFont,ImageChops
from preview_tutorials_468 import ROOT,digest

out=ROOT/'translation/previews_489';out.mkdir(exist_ok=True)
src=ROOT/'export_base/facility/velvet.spr3.00.png'
original=Image.open(src).convert('RGBA');im=original.copy()
specs=[((96,153,174,171),'切换人格面具'),((175,153,228,171),'切换显示'),
       ((96,172,161,190),'已登录全书'),((163,172,240,190),'技能说明'),
       ((96,192,161,210),'切换页面'),((162,192,216,210),'切换手册'),
       ((216,192,245,210),'召唤'),((96,211,125,229),'保护'),
       ((126,211,156,229),'删除'),((159,211,188,229),'登录'),
       ((190,463,220,481),'选择'),((205,492,255,511),'菜单')]
f=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',48)
for box,text in specs:
    x0,y0,x1,y1=box
    patch=Image.new('RGBA',((x1-x0)*4,(y1-y0)*4),(255,255,255,0))
    d=ImageDraw.Draw(patch);b=d.textbbox((0,0),text,font=f)
    assert b[2]-b[0]+8<=patch.width,(text,b)
    d.text((4-b[0],(patch.height-b[3]+b[1])//2-b[1]),text,font=f,fill='#201957',stroke_width=4,stroke_fill='#e5e1ff')
    im.paste(patch.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS),box[:2])
check=im.copy()
for box,_ in specs:check.paste(original.crop(box),box[:2])
assert ImageChops.difference(check,original).convert('RGB').getbbox() is None
assert ImageChops.difference(check.getchannel('A'),original.getchannel('A')).getbbox() is None
target=out/'velvet.spr3.00.png';im.save(target)
sheet=Image.new('RGBA',(230,len(specs)*25),'#d8d8d8')
for i,(box,_) in enumerate(specs):
    for j,img in enumerate((original,im)):
        sheet.alpha_composite(img.crop(box),(j*115+8,i*25+3))
sheet.resize((690,len(specs)*75),Image.Resampling.NEAREST).save(out/'velvet_labels_compare.png')
(out/'review.json').write_text(json.dumps(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),edits=specs,status='pending_user_review',outside_labels_and_alpha_unchanged=True,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
