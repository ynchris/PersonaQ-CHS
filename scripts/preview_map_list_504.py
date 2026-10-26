import json
from PIL import Image,ImageDraw,ImageFont,ImageChops
from preview_tutorials_468 import ROOT,digest
out=ROOT/'translation/previews_504';out.mkdir(exist_ok=True)
for name in ['pic14.ctpk.00.png','map_plt_icon.ctpk.00.png']:
    im=Image.open(ROOT/'export_base/mapdat/tex'/name).convert('RGBA')
    bg=Image.new('RGBA',im.size,'#555555');bg.alpha_composite(im)
    bg.resize((im.width*3,im.height*3),Image.Resampling.NEAREST).save(out/(name+'.inspect.png'))
results=[]
for name,specs in [
 ('map_plt_icon.ctpk.00.png',[( (251,180,299,191),'迷宫列表',9,249),((313,180,361,191),'迷宫列表',9,311)]),
 ('pic14.ctpk.00.png',[((57,118,86,124),'迷宫列表',5,56),((198,118,227,124),'迷宫列表',5,197)])]:
    original=Image.open(ROOT/'export_base/mapdat/tex'/name).convert('RGBA');im=original.copy()
    boxes=[]
    for box,text,size,sample in specs:
        x0,y0,x1,y1=box;boxes.append(box)
        for y in range(y0,y1):
            for x in range(x0,x1):im.putpixel((x,y),original.getpixel((sample,y)))
        patch=Image.new('RGBA',((x1-x0)*4,(y1-y0)*4))
        d=ImageDraw.Draw(patch);font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',size*4)
        b=d.textbbox((0,0),text,font=font)
        d.text(((patch.width-b[2]+b[0])/2-b[0],(patch.height-b[3]+b[1])/2-b[1]),text,font=font,fill='#333300')
        im.alpha_composite(patch.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS),box[:2])
    if name.startswith('pic14'):
        box=(14,150,242,199);boxes.append(box)
        patch=Image.new('RGBA',(228*4,49*4))
        d=ImageDraw.Draw(patch);font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',48)
        for row,text in enumerate(['触摸“迷宫列表”按钮，','选择迷宫后，就能查看','对应的楼层地图。']):
            d.text((4,4+row*16*4),text,font=font,fill='#333333',anchor='lt')
        im.paste(patch.resize((228,49),Image.Resampling.LANCZOS),box[:2])
    check=im.copy()
    for box in boxes:check.paste(original.crop(box),box[:2])
    assert not any(c.getbbox() for c in ImageChops.difference(check,original).split())
    target=out/name;im.save(target)
    pair=Image.new('RGBA',(original.width*2+8,original.height),'#cccccc')
    pair.alpha_composite(original,(0,0));pair.alpha_composite(im,(original.width+8,0))
    if name.startswith('pic14'):pair=pair.resize((1040,512),Image.Resampling.NEAREST)
    pair.save(out/(name+'.compare.png'))
    results.append(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),changed_boxes=boxes,outside_boxes_rgba_unchanged=True))
(out/'review.json').write_text(json.dumps(dict(status='pending_user_visual_review',files=results,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
