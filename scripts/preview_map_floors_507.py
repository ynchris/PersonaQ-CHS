import json
from PIL import Image,ImageDraw,ImageFont,ImageChops
from preview_tutorials_468 import ROOT,digest
out=ROOT/'translation/previews_507';out.mkdir(exist_ok=True)
previous=Image.open(ROOT/'translation/previews_506/map_plt_icon.ctpk.00.png').convert('RGBA')
original=Image.open(ROOT/'export_base/mapdat/tex/map_plt_icon.ctpk.00.png').convert('RGBA')
im=previous.copy()
rows=[(['第1章','第2章','第3章','最终章'],'#ff00ff'),
 (['第1场','第2场','第3场','第4场','终点'],'#ff00ff'),
 (['第一怪','第二怪','第三怪','第四怪','最终怪'],'#ff3300'),
 (['第一夜','第二夜','第三夜','第四夜','最终夜'],'#ffff00'),
 (['1层','2层','3层','4层','5层'],'#333333'),
 (['6层','7层','8层','9层','顶层'],'#333333')]
edits=[]
font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',36)
for row,(texts,color) in enumerate(rows):
    for col,text in enumerate(texts):
        x=315+31*col;y=391+14*row
        width=46 if row==1 and col==4 else 30
        box=(x,y,x+width,y+13)
        patch=Image.new('RGBA',(width*4,52));d=ImageDraw.Draw(patch)
        b=d.textbbox((0,0),text,font=font)
        assert b[2]-b[0]<=patch.width
        d.text(((patch.width-b[2]+b[0])/2-b[0],(patch.height-b[3]+b[1])/2-b[1]),text,font=font,fill=color)
        im.paste(patch.resize((width,13),Image.Resampling.LANCZOS),box[:2])
        edits.append(dict(text=text,box=box,color=color))
check=im.copy()
for e in edits:check.paste(previous.crop(e['box']),e['box'][:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,previous).split())
target=out/'map_plt_icon.ctpk.00.png';im.save(target)
pair=Image.new('RGBA',(1032,512),'#cccccc');pair.alpha_composite(original,(0,0));pair.alpha_composite(im,(520,0));pair.save(out/'map_full_compare.png')
detail=Image.new('RGBA',(348,87),'#999999')
detail.alpha_composite(original.crop((313,389,485,476)),(0,0));detail.alpha_composite(im.crop((313,389,485,476)),(176,0))
detail.resize((1392,348),Image.Resampling.NEAREST).save(out/'floors_compare.png')
(out/'review.json').write_text(json.dumps(dict(status='pending_user_visual_review',png=target.relative_to(ROOT).as_posix(),sha256=digest(target),edits=edits,outside_boxes_rgba_unchanged=True,decorative_logos_unchanged=True,english_control_labels_retained=True,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
