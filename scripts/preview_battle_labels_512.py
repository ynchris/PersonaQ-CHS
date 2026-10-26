import json
from PIL import Image,ImageDraw,ImageFont,ImageChops
from preview_tutorials_468 import ROOT,digest
out=ROOT/'translation/previews_512';out.mkdir(exist_ok=True)
original=Image.open(ROOT/'export_base/battle/panel/btl.spr3.00.png').convert('RGBA');im=original.copy()
specs=[((351,260,417,280),'状态',12,False),((283,275,315,295),'返回',12,False),((472,275,505,294),'清除',12,False),((138,747,209,770),'委托分析',15,True),((213,747,302,770),'委托分析中',15,True)]
for box,text,size,inverted in specs:
    l,t,r,bottom=box
    patch=Image.new('RGBA',((r-l)*4,(bottom-t)*4));d=ImageDraw.Draw(patch)
    f=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',size*4);b=d.textbbox((0,0),text,font=f)
    assert b[2]-b[0]+8<=patch.width
    d.text(((patch.width-b[2]+b[0])/2-b[0],(patch.height-b[3]+b[1])/2-b[1]),text,font=f,fill='white' if inverted else '#333333',stroke_width=0 if inverted else 4,stroke_fill='white')
    im.paste(patch.resize((r-l,bottom-t),Image.Resampling.LANCZOS),box[:2])
check=im.copy()
for box,*_ in specs:check.paste(original.crop(box),box[:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,original).split())
target=out/'btl.spr3.00.png';im.save(target)
pair=Image.new('RGBA',(1032,1024),'#bbbbbb');pair.alpha_composite(original,(0,0));pair.alpha_composite(im,(520,0));pair.save(out/'battle_full_compare.png')
detail=Image.new('RGBA',(228,5*30),'#bbbbbb')
for row,(box,*_) in enumerate(specs):
    for col,source in enumerate([original,im]):detail.alpha_composite(source.crop(box),(col*114+5,row*30+3))
detail.resize((684,450),Image.Resampling.NEAREST).save(out/'battle_labels_compare.png')
(out/'review.json').write_text(json.dumps(dict(status='pending_user_visual_review',png=target.relative_to(ROOT).as_posix(),sha256=digest(target),edits=specs,outside_boxes_rgba_unchanged=True,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
