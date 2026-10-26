"""Battle affinity label strip only; approved 541 controls remain identical."""
import hashlib
from PIL import Image,ImageDraw,ImageFont,ImageChops
from compile_translation import ROOT,read,write
out=ROOT/'translation/previews_542';out.mkdir(exist_ok=True)
src=ROOT/'translation/feedback_541/decoded/camp_c_main.spr3.tex1.ctpk.00.png'
basepath=ROOT/'translation/previews_541/c_main.second.ctpk.00.png'
review=read(ROOT/'translation/previews_541/review.json')
assert review['status']=='approved_by_user'
assert hashlib.sha256(basepath.read_bytes()).hexdigest()==review['sha256']
original=Image.open(src).convert('RGBA');base=Image.open(basepath).convert('RGBA');im=base.copy()
specs=[((1,238,18,255),'斩'),((18,238,35,255),'坏'),((71,238,88,255),'冰'),
       ((105,238,122,255),'风'),((140,238,156,255),'暗')]
edits=[]
for box,text in specs:
    l,t,r,b=box;w,h=r-l,b-t
    old=original.crop(box);ink=old.getchannel('A').getbbox()
    patch=Image.new('RGBA',(w*4,h*4));d=ImageDraw.Draw(patch)
    font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',56)
    bb=d.textbbox((0,0),text,font=font)
    cx=(ink[0]+ink[2])*2;cy=(ink[1]+ink[3])*2
    x=cx-(bb[0]+bb[2])/2;y=cy-(bb[1]+bb[3])/2
    assert x+bb[0]>=0 and x+bb[2]<=w*4 and y+bb[1]>=0 and y+bb[3]<=h*4
    d.text((x,y),text,font=font,fill='white')
    im.paste(patch.resize((w,h),Image.Resampling.LANCZOS),(l,t))
    edits.append(dict(box=box,text=text,font_size=14,original_ink_bbox=ink))
check=im.copy()
for box,_ in specs:check.paste(base.crop(box),box[:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,base).split())
for e in review['edits']:assert im.crop(e['box']).tobytes()==base.crop(e['box']).tobytes()
target=out/'c_main.second.ctpk.00.png';im.save(target)
crop=(1,238,156,255)
pair=Image.new('RGBA',(326,27),'#555555')
for x,source in [(4,original),(167,im)]:pair.alpha_composite(source.crop(crop),(x,5))
pair.resize((1304,108),Image.Resampling.NEAREST).save(out/'attributes_compare.png')
full=Image.new('RGBA',(1032,256),'#555555');full.alpha_composite(original);full.alpha_composite(im,(520,0));full.save(out/'full_compare.png')
write(out/'review.json',dict(status='pending_user_visual_review',source=src.relative_to(ROOT).as_posix(),
    approved_base=basepath.relative_to(ROOT).as_posix(),container='data/camp/c_main.spr3',texture_offset=344624,
    png=target.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),edits=edits,
    unchanged_characters='突火雷光',approved_541_controls_unchanged=True,outside_boxes_rgba_unchanged=True,
    encoded=False,packaged=False,colored_icons_unchanged=True))
