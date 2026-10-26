"""Review-only: shift party sprite 49 (卸下) right 2px, away from the X button. Fits sprite box; no UV change."""
import json
from PIL import Image,ImageChops
from preview_tutorials_468 import ROOT,digest
out=ROOT/'translation/previews_584';out.mkdir(exist_ok=True)
original=Image.open(ROOT/'export_base/facility/party.spr3.00.png').convert('RGBA')
base=Image.open(ROOT/'translation/previews_522/party.spr3.00.png').convert('RGBA');im=base.copy()
box=(469,86,500,104);shift=2  # party.spr3 sprite 49 操作ヘルプ
patch=base.crop(box);ink=patch.getchannel('A').getbbox()
assert ink[2]+shift<=patch.width,('clipping',ink)
moved=Image.new('RGBA',patch.size);moved.paste(patch.crop((0,0,patch.width-shift,patch.height)),(shift,0))
im.paste(moved,box[:2])
check=im.copy();check.paste(base.crop(box),box[:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,base).split())
target=out/'party.spr3.00.png';im.save(target)
crop=(436,84,502,124);detail=Image.new('RGBA',(3*70,40),'#303030')
for i,img in enumerate((original,base,im)):detail.alpha_composite(img.crop(crop),(i*70+2,0))
detail.resize((detail.width*6,detail.height*6),Image.Resampling.NEAREST).save(out/'unload_compare.png')
(out/'review.json').write_text(json.dumps(dict(status='pending_user_visual_review',png=target.relative_to(ROOT).as_posix(),sha256=digest(target),
    base_png='translation/previews_522/party.spr3.00.png',sprite=49,box=box,shift_x=shift,ink_before=ink,uv_update_required=False,
    outside_box_rgba_unchanged=True,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
print('ok',ink)
