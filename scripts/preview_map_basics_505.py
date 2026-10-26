from PIL import Image,ImageDraw,ImageFont,ImageChops
import json
from preview_tutorials_468 import ROOT,digest
out=ROOT/'translation/previews_505';out.mkdir(exist_ok=True)
sheet=Image.new('RGBA',(512,512),'#cccccc')
for i in range(4):
    im=Image.open(ROOT/f'export_base/mapdat/tex/pic{i+1:02}.ctpk.00.png').convert('RGBA')
    sheet.alpha_composite(im,((i%2)*256,(i//2)*256))
sheet.resize((1024,1024),Image.Resampling.NEAREST).save(out/'inspect.png')
texts=[
 ['触摸选择“钢笔工具”，','沿着方格边缘描画，','即可画出墙壁的线条。'],
 ['触摸选择“橡皮擦工具”，','再触摸需要擦除的位置，','即可擦除画好的墙壁线条。'],
 ['触摸选择“画笔工具”，','在需要涂色的方格上触摸或滑动，','即可为地图上的地板涂色。'],
 ['触摸选择“抹布工具”，','再触摸需要擦除的位置，','即可擦除地板的颜色。']]
results=[]
for i,lines in enumerate(texts,1):
    name=f'pic{i:02}.ctpk.00.png'
    original=Image.open(ROOT/'export_base/mapdat/tex'/name).convert('RGBA');im=original.copy()
    box=(14,144,242,192)
    patch=Image.new('RGBA',(228*4,48*4));d=ImageDraw.Draw(patch)
    font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',48)
    for row,text in enumerate(lines):
        assert d.textlength(text,font=font)<=patch.width-8
        d.text((4,4+row*64),text,font=font,fill='#333333',anchor='lt')
    im.paste(patch.resize((228,48),Image.Resampling.LANCZOS),box[:2])
    check=im.copy();check.paste(original.crop(box),box[:2])
    assert not any(c.getbbox() for c in ImageChops.difference(check,original).split())
    target=out/name;im.save(target)
    pair=Image.new('RGBA',(520,256),'#cccccc')
    pair.alpha_composite(original,(0,0));pair.alpha_composite(im,(264,0))
    pair.resize((1040,512),Image.Resampling.NEAREST).save(out/(name+'.compare.png'))
    results.append(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),text=lines,box=box,outside_box_rgba_unchanged=True))
(out/'review.json').write_text(json.dumps(dict(status='pending_user_visual_review',files=results,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
