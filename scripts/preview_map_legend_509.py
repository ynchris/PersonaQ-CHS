import json
from PIL import Image,ImageDraw,ImageFont,ImageChops
from preview_tutorials_468 import ROOT,digest
out=ROOT/'translation/previews_509';out.mkdir(exist_ok=True)
sheet=Image.new('RGBA',(512,512),'#cccccc')
for i in range(4):
    im=Image.open(ROOT/f'export_base/mapdat/tex/pic{i+9:02}.ctpk.00.png').convert('RGBA')
    sheet.alpha_composite(im,((i%2)*256,(i//2)*256))
sheet.resize((1024,1024),Image.Resampling.NEAREST).save(out/'inspect.png')
specs={
 9:[((24,50,246,113),['可以用来标记门的位置。','对于上锁的门，','将图标设为“关闭的门”，','会更容易辨认。']),((24,149,246,181),['分别在对应位置放置','上楼和下楼的楼梯图标。'])],
 10:[((24,50,250,82),['可放在会自动前进的地板上，','方便标记移动方向。']),((24,118,250,135),['可用于标记发生事件的位置。']),((24,178,250,195),['可用于标记机关。'])],
 11:[((24,36,246,68),['可用来标记F.O.E.所在的位置，','方便查看。']),((24,102,246,134),['需要用数字标记顺序等信息时，','可在相应位置放置数字图标。']),((24,168,246,200),['放置后即可输入文字。','用它记录各种信息吧。'])],
 12:[((24,36,250,68),['放在能量点出现的位置，','方便查找。']),((24,102,252,119),['放在捷径上，会自动变成方向箭头。']),((24,151,250,200),['放在宝箱所在的位置，','取走箱内物品后，','图标会自动变成打开的宝箱。'])]}
results=[]
for index,blocks in specs.items():
    name=f'pic{index:02}.ctpk.00.png'
    original=Image.open(ROOT/'export_base/mapdat/tex'/name).convert('RGBA');im=original.copy()
    for box,lines in blocks:
        l,t,r,bottom=box;w=r-l;h=bottom-t
        patch=Image.new('RGBA',(w*4,h*4));d=ImageDraw.Draw(patch)
        font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',48)
        for row,text in enumerate(lines):
            assert d.textlength(text,font=font)<=patch.width-8
            d.text((4,4+row*64),text,font=font,fill='#333333',anchor='lt')
        im.paste(patch.resize((w,h),Image.Resampling.LANCZOS),box[:2])
    check=im.copy()
    for box,_ in blocks:check.paste(original.crop(box),box[:2])
    assert not any(c.getbbox() for c in ImageChops.difference(check,original).split())
    target=out/name;im.save(target)
    pair=Image.new('RGBA',(520,256),'#cccccc')
    pair.alpha_composite(original,(0,0));pair.alpha_composite(im,(264,0))
    pair.resize((1040,512),Image.Resampling.NEAREST).save(out/(name+'.compare.png'))
    results.append(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),blocks=blocks,outside_boxes_rgba_unchanged=True))
(out/'review.json').write_text(json.dumps(dict(status='pending_user_visual_review',files=results,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
