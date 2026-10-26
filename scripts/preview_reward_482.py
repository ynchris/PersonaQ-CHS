"""Resolve provisional quest reward against the actual item-name draft."""
import json
from PIL import Image,ImageChops
import preview_tutorials_468 as render
from preview_tutorials_468 import ROOT,label,digest
from equipment_names import load_drafts

_,_,names,rows=load_drafts()
assert names[1181]=='ローグロウ' and rows[1181]=='初级成长'
out=ROOT/'translation/previews_482';out.mkdir(exist_ok=True)
records=[]
render.FONT='C:/Windows/Fonts/msyhbd.ttc'
for n in (26,27):
    old=Image.open(ROOT/f'translation/previews_481/t{n:03}.ctpk.00.png').convert('RGBA')
    source=Image.open(ROOT/f'export_base/tutorial/t{n:03}.ctpk.00.png').convert('RGBA')
    im=old.copy();box=(140,160,191,172)
    label(im,box,rows[1181],'white' if n==26 else '#929292',source.getpixel((280,140)),size=9)
    check=im.copy();check.paste(old.crop(box),box[:2])
    assert ImageChops.difference(check,old).convert('RGB').getbbox() is None
    target=out/f't{n:03}.ctpk.00.png';im.save(target)
    pair=Image.new('RGBA',(592,184),'black');pair.paste(source.crop((0,0,296,184)),(0,0));pair.paste(im.crop((0,0,296,184)),(296,0))
    pair.resize((1184,368),Image.Resampling.NEAREST).save(out/f't{n:03}_compare.png')
    records.append(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),reward='初级成长',item_index=1181,original='ローグロウ',status='pending_user_review',outside_reward_box_unchanged=True))
(out/'review.json').write_text(json.dumps(dict(images=records,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
Image.open(ROOT/'export_base/tutorial/t022.ctpk.00.png').crop((0,0,296,184)).resize((1184,736),Image.Resampling.NEAREST).save(out/'t022_source_inspection.png')
