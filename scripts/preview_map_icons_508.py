import json
from PIL import Image,ImageDraw,ImageFont,ImageChops
from preview_tutorials_468 import ROOT,digest
out=ROOT/'translation/previews_508';out.mkdir(exist_ok=True)
sheet=Image.new('RGBA',(512,512),'#cccccc')
for i in range(4):
    im=Image.open(ROOT/f'export_base/mapdat/tex/pic{i+5:02}.ctpk.00.png').convert('RGBA')
    sheet.alpha_composite(im,((i%2)*256,(i//2)*256))
sheet.resize((1024,1024),Image.Resampling.NEAREST).save(out/'inspect.png')
texts=[
 ['给地板涂色时，','触摸“Color”按钮打开调色板，','即可选择要使用的颜色。'],
 ['在地图上放置各种图标，','可标记门等位置。','按住要放置的图标，','拖到地图上后松开。'],
 ['要删除地图上放置的图标，','先切换到“钢笔工具”，','再按住要删除的图标，','将其拖入“垃圾桶”。'],
 ['触摸图标后，','即可通过调色板','更改图标的颜色或类型。']]
results=[]
for i,lines in enumerate(texts,5):
    name=f'pic{i:02}.ctpk.00.png'
    original=Image.open(ROOT/'export_base/mapdat/tex'/name).convert('RGBA');im=original.copy()
    height=len(lines)*16;box=(14,144,242,144+height)
    patch=Image.new('RGBA',(228*4,height*4));d=ImageDraw.Draw(patch)
    font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',48)
    for row,text in enumerate(lines):
        assert d.textlength(text,font=font)<=patch.width-8
        d.text((4,4+row*64),text,font=font,fill='#333333',anchor='lt')
    im.paste(patch.resize((228,height),Image.Resampling.LANCZOS),box[:2])
    check=im.copy();check.paste(original.crop(box),box[:2])
    assert not any(c.getbbox() for c in ImageChops.difference(check,original).split())
    target=out/name;im.save(target)
    pair=Image.new('RGBA',(520,256),'#cccccc')
    pair.alpha_composite(original,(0,0));pair.alpha_composite(im,(264,0))
    pair.resize((1040,512),Image.Resampling.NEAREST).save(out/(name+'.compare.png'))
    results.append(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),text=lines,box=box,outside_box_rgba_unchanged=True))
(out/'review.json').write_text(json.dumps(dict(status='pending_user_visual_review',files=results,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
