"""DLC standalone white labels, retain approved 491 panel labels."""
import json
from PIL import Image,ImageDraw,ImageFont,ImageChops
from preview_tutorials_468 import ROOT,digest
out=ROOT/'translation/previews_521';out.mkdir(exist_ok=True)
original=Image.open(ROOT/'export_base/title/dlc.spr3.00.png').convert('RGBA')
base=Image.open(ROOT/'translation/previews_491/dlc.spr3.00.png').convert('RGBA');im=base.copy()
specs=[((80,98,156,115),'购买'),((80,116,156,133),'增加余额'),((80,134,156,151),'退出'),((1,173,77,190),'删除'),((1,191,126,208),'可下载')]
for box,text in specs:
    l,t,r,b=box;patch=Image.new('RGBA',((r-l)*4,(b-t)*4));d=ImageDraw.Draw(patch)
    f=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',52);bb=d.textbbox((0,0),text,font=f)
    assert bb[2]-bb[0]<=patch.width and bb[3]-bb[1]<=patch.height
    center_x=(39-l)*4 if text=='可下载' else patch.width/2
    d.text((center_x-(bb[2]-bb[0])/2-bb[0],(patch.height-bb[3]+bb[1])/2-bb[1]),text,font=f,fill='white')
    im.paste(patch.resize((r-l,b-t),Image.Resampling.LANCZOS),box[:2])
check=im.copy()
for box,_ in specs:check.paste(base.crop(box),box[:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,base).split())
for box,*_ in json.loads((ROOT/'translation/previews_491/review.json').read_text(encoding='utf-8'))['edits']:
    assert im.crop(box).tobytes()==base.crop(box).tobytes()
target=out/'dlc.spr3.00.png';im.save(target)
for bg,name in [('#222222','dark'),('#cccccc','light')]:
    full=Image.new('RGBA',(1032,256),bg);full.alpha_composite(original);full.alpha_composite(im,(520,0));full.save(out/f'dlc_full_{name}.png')
details=Image.new('RGBA',(280,26*len(specs)),'#222222')
for row,(box,_) in enumerate(specs):
    for col,src in enumerate([original,im]):details.alpha_composite(src.crop(box),(col*140+4,row*26+3))
details.resize((840,details.height*3),Image.Resampling.NEAREST).save(out/'dlc_white_compare.png')
(out/'review.json').write_text(json.dumps(dict(status='pending_user_visual_review',png=target.relative_to(ROOT).as_posix(),sha256=digest(target),base_png='translation/previews_491/dlc.spr3.00.png',edits=specs,outside_boxes_rgba_unchanged=True,approved_491_labels_unchanged=True,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
