"""Enlarge only the two reviewed tutorial arrow labels, keeping old previews."""
import json
from PIL import Image, ImageChops
from preview_skills_478 import clean_light,overlay
from preview_tutorials_468 import ROOT,digest

out=ROOT/'translation/previews_479'
out.mkdir(exist_ok=True)
box=(235,13,268,45)
records=[]
for n in (4,30):
    old=Image.open(ROOT/f'translation/previews_478/t{n:03}.ctpk.00.png').convert('RGBA')
    original=Image.open(ROOT/f'export_base/tutorial/t{n:03}.ctpk.00.png').convert('RGBA')
    im=old.copy()
    im.paste(original.crop(box),box[:2])
    clean_light(im,box)
    overlay(im,box,'强化',13,45)
    check=im.copy();check.paste(old.crop(box),box[:2])
    assert ImageChops.difference(check,old).convert('RGB').getbbox() is None
    target=out/f't{n:03}.ctpk.00.png';im.save(target)
    pair=Image.new('RGBA',(592,184),'black')
    pair.paste(original.crop((0,0,296,184)),(0,0));pair.paste(im.crop((0,0,296,184)),(296,0))
    pair.resize((1184,368),Image.Resampling.NEAREST).save(out/f't{n:03}_compare.png')
    records.append(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),change='强化字号11→13，角度45度及中心不变',outside_arrow_box_unchanged=True,status='pending_user_review'))
(out/'review.json').write_text(json.dumps(dict(images=records,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
