"""Remove only the neighboring-glyph fleck at the arrow's upper right."""
import hashlib
from PIL import Image,ImageChops
from compile_translation import ROOT,write
out=ROOT/'translation/previews_549';out.mkdir(exist_ok=True)
source=ROOT/'translation/previews_548/camp_texture_1.png'
before=Image.open(source).convert('RGBA');after=before.copy()
boxes=[(199,219,201,222),(200,222,201,224)]
for box in boxes:after.paste((0,0,0,0),box)
check=after.copy()
for box in boxes:check.paste(before.crop(box),box[:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,before).split())
changed=sum(a!=b for a,b in zip(before.getdata(),after.getdata()))
assert changed>0
target=out/'camp_texture_1.png';after.save(target)
crop=(151,214,227,234)
pair=Image.new('RGBA',(170,28),'#444444')
pair.alpha_composite(before.crop(crop),(4,4));pair.alpha_composite(after.crop(crop),(90,4))
pair.resize((1020,168),Image.Resampling.NEAREST).save(out/'before_after.png')
write(out/'review.json',dict(status='pending_user_visual_review',base=source.relative_to(ROOT).as_posix(),png=target.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),boxes=boxes,changed_pixels=changed,outside_boxes_rgba_unchanged=True,encoded=False,packaged=False))
print('Changed pixels:',changed)
