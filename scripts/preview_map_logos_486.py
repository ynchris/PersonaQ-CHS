"""First three fully visible map logos; PNG-only review, no binary imports."""
import json
from PIL import Image,ImageDraw,ImageFont,ImageChops
from preview_tutorials_468 import ROOT,digest

out=ROOT/'translation/previews_486';out.mkdir(exist_ok=True)
records=[]
for n,x,y,w in [(16,201,11,54),(17,199,8,55),(40,205,8,54)]:
    source=ROOT/f'export_base/tutorial/t{n:03}.ctpk.00.png'
    original=Image.open(source).convert('RGBA');im=original.copy()
    title=(x,y,x+w,y+21);chapter=(x+28,y+21,x+w,y+30)
    bg=original.getpixel((x+w-2,y+31))
    patch=Image.new('RGBA',(w*4,21*4),bg)
    d=ImageDraw.Draw(patch);f=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',10*4)
    for i,text in enumerate(['不可思议','之国的你']):
        b=d.textbbox((0,0),text,font=f)
        d.text(((patch.width-b[2]+b[0])//2-b[0],(1+i*10)*4-b[1]),text,font=f,fill='#a3b5b5',stroke_width=3,stroke_fill='#374b4c')
    im.paste(patch.resize((w,21),Image.Resampling.LANCZOS),title[:2])
    small=Image.new('RGBA',((w-28)*4,9*4),bg)
    d=ImageDraw.Draw(small);f=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',7*4)
    b=d.textbbox((0,0),'第1章',font=f)
    d.text((0,(36-b[3]+b[1])//2-b[1]),'第1章',font=f,fill='#a44b9a')
    im.paste(small.resize((w-28,9),Image.Resampling.LANCZOS),chapter[:2])
    boxes=[title,chapter]
    check=im.copy()
    for box in boxes:check.paste(original.crop(box),box[:2])
    assert ImageChops.difference(check,original).convert('RGB').getbbox() is None
    target=out/f't{n:03}.ctpk.00.png';im.save(target)
    pair=Image.new('RGBA',(592,184),'black');pair.paste(original.crop((0,0,296,184)),(0,0));pair.paste(im.crop((0,0,296,184)),(296,0))
    pair.resize((1184,368),Image.Resampling.NEAREST).save(out/f't{n:03}_compare.png')
    records.append(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),title='不可思议之国的你',chapter='第1章',status='pending_user_review',outside_boxes_unchanged=True,edit_boxes=boxes))
(out/'review.json').write_text(json.dumps(dict(images=records,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
