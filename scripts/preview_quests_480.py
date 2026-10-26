"""Quest tutorial previews, no encoding. Reward name remains explicitly provisional."""
import json
from PIL import Image,ImageChops
import preview_tutorials_468 as render
from preview_tutorials_468 import ROOT,label,digest

out=ROOT/'translation/previews_480'
out.mkdir(exist_ok=True)
records=[]
for n in (26,27):
    original=Image.open(ROOT/f'export_base/tutorial/t{n:03}.ctpk.00.png').convert('RGBA')
    im=original.copy();boxes=[]
    render.FONT='C:/Windows/Fonts/msyhbd.ttc'
    dim=n==27
    def put(b,t,size,color,bg):
        label(im,b,t,color,bg,size=size);boxes.append(b)
    dark=original.getpixel((280,140))
    white='#929292' if dim else 'white'
    gold='#8c7700' if dim else '#e9cb00'
    put((28,29,118,41),'查看委托',8,gold,original.getpixel((120,34)))
    if n==26:
        put((32,45,59,57),'受理中',7,'#00383c','#00d6e5')
        put((32,59,59,71),'受理中',7,'#00383c','#00d6e5')
        put((62,45,230,57),'帮忙参加以物易物对决',9,'white',original.getpixel((220,51)))
        put((62,59,230,71),'创造獬豸',9,'black',original.getpixel((220,65)))
        put((39,117,79,129),'详细说明',7,'white',original.getpixel((85,122)))
    else:
        bg=original.getpixel((245,78))
        put((35,52,239,65),'从菜单的“校内漫步”中选择',9,'#325052',bg)
        put((35,65,239,78),'“以物易物对决”进行挑战。',9,'#325052',bg)
    put((107,123,155,135),'校内漫步',9,'#202000',original.getpixel((153,125)))
    put((106,136,261,147),'想和小熊进行以物易物对决，',9,white,dark)
    put((106,147,261,159),'让玲吃到美味的食物。',9,white,dark)
    put((106,160,127,172),'报酬',8,gold,dark)
    put((140,160,191,172),'低级成长',9,white,dark)
    check=im.copy()
    for b in boxes:check.paste(original.crop(b),b[:2])
    assert ImageChops.difference(check,original).convert('RGB').getbbox() is None
    target=out/f't{n:03}.ctpk.00.png';im.save(target)
    pair=Image.new('RGBA',(592,184),'black');pair.paste(original.crop((0,0,296,184)),(0,0));pair.paste(im.crop((0,0,296,184)),(296,0))
    pair.resize((1184,368),Image.Resampling.NEAREST).save(out/f't{n:03}_compare.png')
    records.append(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),status='pending_user_review',edit_boxes=boxes,outside_boxes_unchanged=True,reward_note='ローグロウ rendered 低级成长; needs actual item name-table cross-check before encoding.'))
(out/'review.json').write_text(json.dumps(dict(images=records,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
