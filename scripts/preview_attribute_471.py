"""User terminology correction, one PNG only; no encoding."""
import json
from PIL import Image, ImageChops
from preview_tutorials_468 import ROOT, label, digest

out=ROOT/'translation/previews_471'
out.mkdir(exist_ok=True)
source=ROOT/'translation/previews_470/t034.ctpk.00.png'
before=Image.open(source).convert('RGBA')
im=before.copy()
box=(188,81,251,99)
label(im,box,'破坏属性','black','white',size=12)
check=im.copy()
check.paste(before.crop(box),(box[0],box[1]))
assert ImageChops.difference(check,before).convert('RGB').getbbox() is None
target=out/'t034.ctpk.00.png'
im.save(target)
original=Image.open(ROOT/'export_base/tutorial/t034.ctpk.00.png').convert('RGBA')
pair=Image.new('RGBA',(592,184),'black')
pair.paste(original.crop((0,0,296,184)),(0,0))
pair.paste(im.crop((0,0,296,184)),(296,0))
pair.resize((1184,368),Image.Resampling.NEAREST).save(out/'t034_compare.png')
(out/'review.json').write_text(json.dumps(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),change='打击属性 → 破坏属性；保留坏字图标',outside_label_unchanged=True,status='pending_user_review',encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
print('Updated one label; other pixels unchanged; not encoded.')
