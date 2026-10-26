import json
from PIL import Image,ImageDraw,ImageFont,ImageChops
from preview_tutorials_468 import ROOT,digest
out=ROOT/'translation/previews_511';out.mkdir(exist_ok=True)
sheet=Image.new('RGBA',(768,512),'#cccccc')
for i,n in enumerate(range(18,23)):
    im=Image.open(ROOT/f'export_base/mapdat/tex/pic{n:02}.ctpk.00.png').convert('RGBA')
    sheet.alpha_composite(im,((i%3)*256,(i//3)*256))
sheet.resize((1536,1024),Image.Resampling.NEAREST).save(out/'inspect.png')
texts={18:['使用“Auto Pilot”功能，','即可自动行走。'],
19:['用“Auto Pilot”的“路线笔”，','在地图上画出','想要行走的路线吧。'],
20:['站到路线上，触摸“前进”按钮，','就会沿画好的路线自动行走。','若想中途停止，','再次触摸该按钮即可。'],
21:['触摸用“路线笔”画出的线，','即可反转行走方向。'],
22:['使用“路线橡皮擦”，','即可擦除行走路线。','请从路线一端沿线擦除。']}
results=[]
for n,lines in texts.items():
    name=f'pic{n:02}.ctpk.00.png'
    original=Image.open(ROOT/'export_base/mapdat/tex'/name).convert('RGBA');im=original.copy()
    height=len(lines)*16+4;box=(14,144,244,144+height)
    patch=Image.new('RGBA',(230*4,height*4));d=ImageDraw.Draw(patch)
    font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',48)
    for row,text in enumerate(lines):
        assert d.textlength(text,font=font)<=patch.width-8
        d.text((4,8+row*64),text,font=font,fill='#333333',anchor='lt')
    im.paste(patch.resize((230,height),Image.Resampling.LANCZOS),box[:2])
    check=im.copy();check.paste(original.crop(box),box[:2])
    assert not any(c.getbbox() for c in ImageChops.difference(check,original).split())
    target=out/name;im.save(target)
    pair=Image.new('RGBA',(520,256),'#cccccc')
    pair.alpha_composite(original,(0,0));pair.alpha_composite(im,(264,0))
    pair.resize((1040,512),Image.Resampling.NEAREST).save(out/(name+'.compare.png'))
    results.append(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),text=lines,box=box,outside_box_rgba_unchanged=True))
(out/'review.json').write_text(json.dumps(dict(status='pending_user_visual_review',files=results,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
inventory=[]
for n in range(1,23):
    version=505 if n<=4 else 508 if n<=8 else 509 if n<=12 else 504 if n==14 else 510 if n<=17 else 511
    p=ROOT/f'translation/previews_{version}/pic{n:02}.ctpk.00.png'
    assert p.exists()
    inventory.append(dict(source=f'mapdat/tex/pic{n:02}.ctpk',png=p.relative_to(ROOT).as_posix(),sha256=digest(p),status='user_approved' if n<=17 else 'pending_user_visual_review'))
(out/'map_tutorial_inventory.json').write_text(json.dumps(dict(total=22,approved=17,pending=5,scope='mapdat/tex/pic01-pic22 only; decorative screenshot logos retained',encoded=False,packaged=False,rows=inventory),ensure_ascii=False,indent=2),encoding='utf-8')
