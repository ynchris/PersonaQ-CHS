import json
from PIL import Image,ImageDraw,ImageFont,ImageChops
from preview_tutorials_468 import ROOT,digest
out=ROOT/'translation/previews_510';out.mkdir(exist_ok=True)
indices=[13,15,16,17]
sheet=Image.new('RGBA',(512,512),'#cccccc')
for i,n in enumerate(indices):
    im=Image.open(ROOT/f'export_base/mapdat/tex/pic{n:02}.ctpk.00.png').convert('RGBA')
    sheet.alpha_composite(im,((i%2)*256,(i//2)*256))
sheet.resize((1024,1024),Image.Resampling.NEAREST).save(out/'inspect.png')
texts={13:['显示楼层全图时，','触摸楼层编号，','即可查看对应楼层的地图。'],
15:['触摸地图左上角的指南针，','即可让角色朝向始终保持向上。','角色转向时，','地图会随之旋转。'],
16:['如需解除朝向锁定，','再次触摸指南针即可。'],
17:['地图画错时，','触摸“Undo”按钮，','即可撤销上一步操作。']}
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
