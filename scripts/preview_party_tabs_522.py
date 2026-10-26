"""Second battle/dungeon tab pair; retain approved 490 edits."""
import json
from PIL import Image,ImageDraw,ImageFont,ImageChops
from preview_tutorials_468 import ROOT,digest
out=ROOT/'translation/previews_522';out.mkdir(exist_ok=True)
original=Image.open(ROOT/'export_base/facility/party.spr3.00.png').convert('RGBA')
base=Image.open(ROOT/'translation/previews_490/party.spr3.00.png').convert('RGBA');im=base.copy()
specs=[((444,162,479,180),'战斗'),((444,181,479,201),'迷宫')]
for box,text in specs:
    l,t,r,b=box;patch=Image.new('RGBA',((r-l)*4,(b-t)*4));d=ImageDraw.Draw(patch)
    font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',56);bb=d.textbbox((0,0),text,font=font)
    assert bb[2]-bb[0]<=patch.width and bb[3]-bb[1]<=patch.height
    d.text(((patch.width-bb[2]+bb[0])/2-bb[0],(patch.height-bb[3]+bb[1])/2-bb[1]),text,font=font,fill='white')
    im.paste(patch.resize((r-l,b-t),Image.Resampling.LANCZOS),box[:2])
check=im.copy()
for box,_ in specs:check.paste(base.crop(box),box[:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,base).split())
for box,*_ in json.loads((ROOT/'translation/previews_490/review.json').read_text(encoding='utf-8'))['edits']:
    assert im.crop(box).tobytes()==base.crop(box).tobytes()
target=out/'party.spr3.00.png';im.save(target)
for bg,name in [('#222222','dark'),('#cccccc','light')]:
    full=Image.new('RGBA',(1032,512),bg);full.alpha_composite(original);full.alpha_composite(im,(520,0));full.save(out/f'party_full_{name}.png')
crop=(440,160,483,203);detail=Image.new('RGBA',(100,43),'#222222')
detail.alpha_composite(original.crop(crop),(2,0));detail.alpha_composite(im.crop(crop),(54,0))
detail.resize((500,215),Image.Resampling.NEAREST).save(out/'tabs_compare.png')
(out/'review.json').write_text(json.dumps(dict(status='pending_user_visual_review',png=target.relative_to(ROOT).as_posix(),sha256=digest(target),base_png='translation/previews_490/party.spr3.00.png',edits=specs,outside_boxes_rgba_unchanged=True,approved_490_labels_unchanged=True,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
