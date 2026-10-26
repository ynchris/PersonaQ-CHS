"""Velvet room white-label follow-up; PNG only."""
import json
from PIL import Image,ImageDraw,ImageFont,ImageChops
from preview_tutorials_468 import ROOT,digest
out=ROOT/'translation/previews_519';out.mkdir(exist_ok=True)
original=Image.open(ROOT/'export_base/facility/velvet.spr3.00.png').convert('RGBA')
base=Image.open(ROOT/'translation/previews_489/velvet.spr3.00.png').convert('RGBA');im=base.copy()
specs=[((1,347,62,365),'公开',11),((63,347,124,365),'不公开',11),((123,384,180,397),'等级限制',11),((187,369,211,383),'小时',11),((27,367,69,383),'最新优先',10),((122,366,174,383),'保护优先',11),((182,108,245,125),'阿尔卡那顺序',10.5),((105,109,129,123),'顺序',11)]
for box,text,size in specs:
    l,t,r,b=box;patch=Image.new('RGBA',((r-l)*4,(b-t)*4));d=ImageDraw.Draw(patch)
    f=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',int(size*4));bb=d.textbbox((0,0),text,font=f)
    assert bb[2]-bb[0]<=patch.width and bb[3]-bb[1]<=patch.height
    d.text(((patch.width-bb[2]+bb[0])/2-bb[0],(patch.height-bb[3]+bb[1])/2-bb[1]),text,font=f,fill='white')
    im.paste(patch.resize((r-l,b-t),Image.Resampling.LANCZOS),box[:2])
check=im.copy()
for box,*_ in specs:check.paste(base.crop(box),box[:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,base).split())
for box,*_ in json.loads((ROOT/'translation/previews_489/review.json').read_text(encoding='utf-8'))['edits']:
    assert base.crop(box).tobytes()==im.crop(box).tobytes()
target=out/'velvet.spr3.00.png';im.save(target)
for bg,name in [('#222222','dark'),('#cccccc','light')]:
    full=Image.new('RGBA',(520,512),bg);full.alpha_composite(original);full.alpha_composite(im,(264,0));full.save(out/f'velvet_full_{name}.png')
detail=Image.new('RGBA',(210,26*len(specs)),'#222222')
for row,(box,*_) in enumerate(specs):
    for col,src in enumerate([original,im]):detail.alpha_composite(src.crop(box),(col*105+4,row*26+3))
detail.resize((630,detail.height*3),Image.Resampling.NEAREST).save(out/'white_labels_compare.png')
(out/'review.json').write_text(json.dumps(dict(status='pending_user_visual_review',png=target.relative_to(ROOT).as_posix(),sha256=digest(target),base_png='translation/previews_489/velvet.spr3.00.png',edits=specs,outside_boxes_rgba_unchanged=True,approved_489_buttons_unchanged=True,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
