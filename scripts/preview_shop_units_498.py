"""Shop storage-unit and equipment-label review; no encoding or packaging."""
import json
import struct
from PIL import Image, ImageDraw, ImageFont, ImageChops
from preview_tutorials_468 import ROOT,digest

out=ROOT/'translation/previews_498'
out.mkdir(exist_ok=True)
raw_path=ROOT/'data/facility/shop.spr3'
raw=raw_path.read_bytes()
count=struct.unpack_from('<H',raw,22)[0]
table=struct.unpack_from('<I',raw,28)[0]
assert count==125 and table==48
def entry(index):
    offset=struct.unpack_from('<I',raw,table+index*8+4)[0]
    name=raw[offset+4:offset+24].split(b'\0')[0].decode('cp932')
    rect=struct.unpack_from('<4i',raw,offset+84)
    return dict(index=index,offset=offset,name=name,texture_rect=rect)
evidence=[entry(i) for i in [92,93,94,95,96,97,98,99,117]]
assert entry(96)['name']=='枠'
assert entry(97)['name']=='個'
assert entry(98)['name']=='預かり枠下地'
assert entry(99)['name']=='cursor預かり枠'
assert entry(117)['name']=='装備品'

previous=Image.open(ROOT/'translation/previews_497/shop.spr3.00.png').convert('RGBA')
im=previous.copy()
specs=[(96,'格',12,'#ffcccc'),(97,'个',12,'#ffcccc'),(117,'装备',13,'white')]
for index,text,size,color in specs:
    x0,y0,x1,y1=entry(index)['texture_rect']
    patch=Image.new('RGBA',((x1-x0)*4,(y1-y0)*4))
    d=ImageDraw.Draw(patch)
    font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',size*4)
    b=d.textbbox((0,0),text,font=font)
    assert b[2]-b[0]+8<=patch.width and b[3]-b[1]+8<=patch.height
    d.text(((patch.width-(b[2]-b[0]))/2-b[0],(patch.height-(b[3]-b[1]))/2-b[1]),text,font=font,fill=color)
    im.paste(patch.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS),(x0,y0))
check=im.copy()
for index,*_ in specs:
    box=entry(index)['texture_rect']
    check.paste(previous.crop(box),box[:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,previous).split())
target=out/'shop.spr3.00.png'
im.save(target)
sheet=Image.new('RGBA',im.size,'#666666')
sheet.alpha_composite(im)
sheet.resize((768,768),Image.Resampling.NEAREST).save(out/'shop_full_preview.png')
(out/'review.json').write_text(json.dumps(dict(
    png=target.relative_to(ROOT).as_posix(),sha256=digest(target),
    status='pending_user_visual_review',edits=specs,
    evidence_source=raw_path.relative_to(ROOT).as_posix(),
    evidence_source_sha256=digest(raw_path),sprite_evidence=evidence,
    interpretation='枠 is grouped with storage background and storage-slot cursor; translate as 格. Resource evidence, not runtime verification.',
    unchanged_outside_three_sprite_rects=True,
    supersedes='translation/previews_497/shop.spr3.00.png',
    preview_has_no_added_text=True,encoded=False,packaged=False,runtime_verified=False
),ensure_ascii=False,indent=2),encoding='utf-8')
