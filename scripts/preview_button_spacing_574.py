"""Review-only spacing fix. Relocated sprite 218 needs UV update at encoding."""
import json,hashlib
from pathlib import Path
from PIL import Image,ImageChops
R=Path(__file__).resolve().parent;O=R/'translation/previews_574';O.mkdir(exist_ok=True)
src=R/'translation/previews_548/camp_texture_0.png'
a=Image.open(src).convert('RGBA');b=a.copy()
records={r['index']:r for r in json.loads((R/'translation/feedback_541/camp_sprite_records.json').read_text(encoding='utf-8'))}
edits=[];boxes=[]
pair=Image.new('RGBA',(224,6*25),'#444444')
for row,(idx,label) in enumerate([(216,'角色状态'),(206,'技能说明'),(218,'切换人格面具'),(213,'人格面具状态'),(217,'切换角色'),(211,'保存')]):
    box=records[idx]['box'];p=a.crop(box);w,h=p.size
    dest=box
    if idx==218:
        dest=[160,350,160+w+3,350+h]
        assert all(px[:3]==(255,255,255) for px in a.crop(dest).getdata())
        q=Image.new('RGBA',(w+3,h))
        b.paste(Image.new('RGBA',(w,h)),box[:2]);boxes.append(box)
    else:
        assert p.getchannel('A').getbbox()[2]+3<=w
        q=Image.new('RGBA',(w,h))
    q.paste(p,(3,0));b.paste(q,dest[:2]);boxes.append(dest)
    # Vertical marker shows each sprite's fixed origin, not a game decoration.
    for x,c in [(8,p),(120,q)]:
        pair.paste('#00b7cc',(x-3,row*25+3,x-2,row*25+21))
        pair.alpha_composite(c,(x,row*25+3))
    edits.append(dict(index=idx,text=label,old_box=box,new_box=dest,shift_x=3,uv_update_required=dest!=box,font_and_pixels_unchanged=True))
check=b.copy()
for box in boxes:check.paste(a.crop(box),box[:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,a).split())
target=O/'camp_texture_0.png';b.save(target)
pair.resize((896,600),Image.Resampling.NEAREST).save(O/'spacing_compare.png')
(O/'review.json').write_text(json.dumps(dict(status='pending_user_visual_review',source=str(src.relative_to(R)),png=str(target.relative_to(R)),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),edits=edits,outside_boxes_unchanged=True,encoded=False,packaged=False,warning='Sprite 218 must update SPR3 UV rectangle; PNG alone is not sufficient.'),ensure_ascii=False,indent=2),encoding='utf-8')
