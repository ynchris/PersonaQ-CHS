"""Save-menu atlas text only. Preserve dimensions, alpha outside labels, portraits."""
import json
from PIL import Image,ImageChops
import preview_tutorials_468 as render
from preview_tutorials_468 import ROOT,label,digest

out=ROOT/'translation/previews_487';out.mkdir(exist_ok=True)
src=ROOT/'export_base/memcard/save_load.spr3.00.png'
original=Image.open(src).convert('RGBA');im=original.copy()
render.FONT='C:/Windows/Fonts/msyhbd.ttc'
boxes=[((260,68,320,81),'切换存档槽',10),((123,349,150,364),'确定',11)]
for box,text,size in boxes:
    bg=original.getpixel((box[0],box[1]))
    print(text,'background',bg)
    label(im,box,text,(0,0,0,255),bg,size=size,align='center')
check=im.copy()
for box,_,_ in boxes:check.paste(original.crop(box),box[:2])
assert ImageChops.difference(check,original).convert('RGB').getbbox() is None
assert ImageChops.difference(check.getchannel('A'),original.getchannel('A')).getbbox() is None
target=out/'save_load.spr3.00.png';im.save(target)
sheet=Image.new('RGBA',(240,84),'white')
for i,(box,_,_) in enumerate(boxes):
    x0,y0,x1,y1=box
    crop=(x0-5,y0-5,x1+5,y1+5)
    for j,source in enumerate((original,im)):
        part=source.crop(crop)
        sheet.alpha_composite(part,(j*120+10,i*42+8))
sheet.resize((960,336),Image.Resampling.NEAREST).save(out/'save_labels_compare.png')
(out/'review.json').write_text(json.dumps(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),source=src.relative_to(ROOT).as_posix(),edits=boxes,outside_labels_and_alpha_unchanged=True,status='pending_user_review',encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
approved=[2,4,6,7,8,10,11,12,20,22,23,24,25,26,27,29,30,32,33,34,35,36,37,38,43,44]
excluded=[13,14,16,17,21,39,40,41,42]
(out/'tutorial_status.json').write_text(json.dumps(dict(approved_preview_tutorials=approved,logo_only_keep_original=excluded,placeholder_requires_review=[3],english_ui_retained=[1,5,9,15,28,31,45,46],no_text=[18,19],note='46 exported tutorials only; no claim of complete game coverage or packaging.'),ensure_ascii=False,indent=2),encoding='utf-8')
