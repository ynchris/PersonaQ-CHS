"""DLC menu labels with original per-row gradient samples; PNG previews only."""
import json
from PIL import Image,ImageDraw,ImageFont,ImageChops
from preview_tutorials_468 import ROOT,digest

out=ROOT/'translation/previews_491';out.mkdir(exist_ok=True)
src=ROOT/'export_base/title/dlc.spr3.00.png'
original=Image.open(src).convert('RGBA');im=original.copy()
specs=[((10,5,40,22),'余额',12,'white',7,'left'),
       ((8,30,99,47),'所需区块数',12,'white',5,'left'),
       ((151,33,181,46),'区块',8,'#009fff',147,'right'),
       ((10,78,40,93),'价格',12,'white',7,'left'),
       ((15,101,67,115),'已购买',12,'white',7,'center'),
       ((15,121,67,135),'已接收',12,'white',7,'center'),
       ((15,141,67,155),'可接收',12,'white',7,'center')]
for box,text,size,color,sample_x,align in specs:
    x0,y0,x1,y1=box
    for y in range(y0,y1):
        for x in range(x0,x1):im.putpixel((x,y),original.getpixel((sample_x,y)))
    ink=Image.new('RGBA',((x1-x0)*4,(y1-y0)*4))
    d=ImageDraw.Draw(ink);f=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',size*4)
    b=d.textbbox((0,0),text,font=f);w=b[2]-b[0]
    assert w<=ink.width
    x={'left':0,'center':(ink.width-w)//2,'right':ink.width-w}[align]
    d.text((x-b[0],(ink.height-b[3]+b[1])//2-b[1]),text,font=f,fill=color)
    im.alpha_composite(ink.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS),(x0,y0))
check=im.copy()
for box,*_ in specs:check.paste(original.crop(box),box[:2])
assert ImageChops.difference(check,original).convert('RGB').getbbox() is None
assert ImageChops.difference(check.getchannel('A'),original.getchannel('A')).getbbox() is None
target=out/'dlc.spr3.00.png';im.save(target)
pair=Image.new('RGBA',(420,166),'white')
pair.alpha_composite(original.crop((0,0,210,166)),(0,0));pair.alpha_composite(im.crop((0,0,210,166)),(210,0))
pair.resize((1260,498),Image.Resampling.NEAREST).save(out/'dlc_labels_compare.png')
(out/'review.json').write_text(json.dumps(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),edits=specs,status='pending_user_review',outside_labels_and_alpha_unchanged=True,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
