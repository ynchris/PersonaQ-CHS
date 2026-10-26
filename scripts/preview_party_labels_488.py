"""Party/navigation menu atlas labels only. No texture import or game packaging."""
import json
from PIL import Image,ImageChops,ImageDraw,ImageFont
import preview_tutorials_468 as render
from preview_tutorials_468 import ROOT,label,digest

out=ROOT/'translation/previews_490';out.mkdir(exist_ok=True)
src=ROOT/'export_base/facility/party.spr3.00.png'
original=Image.open(src).convert('RGBA');im=original.copy()
render.FONT='C:/Windows/Fonts/msyhbd.ttc'
specs=[((470,86,500,104),'卸下',12,'white'),
       ((444,107,499,123),'状态',11,'black'),
       ((444,124,499,142),'切换语音',11,'black'),
       ((443,143,470,160),'删除',11,'black'),
       ((14,278,109,297),'当前导航设置',12,'#ffff00'),
       ((25,298,55,315),'战斗',12,'#999999'),
       ((70,298,100,315),'迷宫',12,'#999999')]
for i,(box,text,size,color) in enumerate(specs):
    bg=original.getpixel((box[0],box[1]))
    print(text,bg)
    if i<4:
        x0,y0,x1,y1=box
        patch=Image.new('RGBA',((x1-x0)*4,(y1-y0)*4),bg)
        d=ImageDraw.Draw(patch);f=ImageFont.truetype(render.FONT,size*4)
        b=d.textbbox((0,0),text,font=f)
        d.text((4-b[0],(patch.height-b[3]+b[1])//2-b[1]),text,font=f,fill='black',stroke_width=4,stroke_fill='white')
        im.paste(patch.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS),box[:2])
    else:
        label(im,box,text,color,bg,size=size,align='left')
check=im.copy()
for box,_,_,_ in specs:check.paste(original.crop(box),box[:2])
for mode in ('RGB','RGBA'):
    assert ImageChops.difference(check,original).convert(mode).getbbox() is None
assert ImageChops.difference(check.getchannel('A'),original.getchannel('A')).getbbox() is None
target=out/'party.spr3.00.png';im.save(target)
sheet=Image.new('RGBA',(260,7*30),'#d8d8d8')
for i,(box,_,_,_) in enumerate(specs):
    for j,img in enumerate((original,im)):
        crop=img.crop(box)
        sheet.alpha_composite(crop,(j*130+12,i*30+5))
sheet.resize((780,630),Image.Resampling.NEAREST).save(out/'party_labels_compare.png')
(out/'review.json').write_text(json.dumps(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),edits=specs,status='pending_user_review',outside_labels_and_alpha_unchanged=True,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
