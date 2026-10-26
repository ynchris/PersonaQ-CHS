"""Review-only arrow isolation and playback spacing; retain pending earlier edits."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont,ImageChops
R=Path(__file__).resolve().parent;O=R/'translation/previews_576';O.mkdir(exist_ok=True)
original=Image.open(R/'translation/feedback_541/decoded/camp_c_main.spr3.tex1.ctpk.00.png').convert('RGBA')
a=Image.open(R/'translation/previews_575/camp_texture_1.png').convert('RGBA');b=a.copy()
box=(120,144,203,162);patch=Image.new('RGBA',(83,18))
# Isolate only the original arrow silhouette. The adjacent Japanese glyphs
# overlap its bounding rectangle, so a rectangular crop alone retains debris.
arrow=Image.new('RGBA',(15,11))
for y,width in enumerate([7,9,11,13,15,15,15,13,11,9,7]):
    left=(15-width)//2
    for x in range(left,left+width):arrow.putpixel((x,y),original.getpixel((162+x,148+y)))
patch.paste(arrow,(34,4))
font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',44)
for text,x in [('出战',7),('候补',51)]:
    hi=Image.new('RGBA',(100,72));d=ImageDraw.Draw(hi);bb=d.textbbox((0,0),text,font=font,stroke_width=4)
    d.text(((100-bb[2]+bb[0])/2-bb[0],(72-bb[3]+bb[1])/2-bb[1]),text,font=font,fill='#333333',stroke_width=4,stroke_fill='white')
    patch.alpha_composite(hi.resize((25,18),Image.Resampling.LANCZOS),(x,0))
b.paste(patch,box[:2]);b.save(O/'camp_texture_1.png')
check=b.copy();check.paste(a.crop(box),box[:2]);assert not any(c.getbbox() for c in ImageChops.difference(a,check).split())
pair=Image.new('RGBA',(180,28),'#444444')
pair.alpha_composite(original.crop(box),(2,4));pair.alpha_composite(patch,(94,4))
pair.resize((1080,168),Image.Resampling.NEAREST).save(O/'arrow_compare.png')
records={r['index']:r for r in json.loads((R/'translation/feedback_541/camp_sprite_records.json').read_text(encoding='utf-8'))}
first=Image.open(R/'translation/previews_574/camp_texture_0.png').convert('RGBA');before=first.copy()
playbox=records[214]['box'];p=first.crop(playbox);w,h=p.size
assert p.getchannel('A').getbbox()[2]+3<=w
q=Image.new('RGBA',p.size);q.paste(p,(3,0));first.paste(q,playbox[:2]);first.save(O/'camp_texture_0.png')
check=first.copy();check.paste(before.crop(playbox),playbox[:2]);assert not any(c.getbbox() for c in ImageChops.difference(before,check).split())
# Use the user's actual button crop for a spacing mock-up, not a claimed game capture.
screen=Image.open('C:/Users/ynChr/AppData/Local/Temp/codex-clipboard-772093dc-7d7a-41c3-9b00-b71890c16216.png').convert('RGB')
sim=Image.new('RGB',(screen.width+6,screen.height),'black');sim.paste(screen.crop((0,0,31,screen.height)),(0,0));sim.paste(screen.crop((31,0,screen.width,screen.height)),(37,0))
view=Image.new('RGB',(screen.width+sim.width+16,screen.height),'black');view.paste(screen);view.paste(sim,(screen.width+16,0));view.resize((view.width*3,view.height*3),Image.Resampling.NEAREST).save(O/'playback_spacing_mockup.png')
report=dict(status='pending_user_visual_review',arrow_box=box,arrow_source='original pixels, neighboring Japanese removed using silhouette mask',playback_index=214,playback_box=playbox,playback_shift_x=3,includes_pending_revisions=[573,574],requires_574_sprite_218_uv_update=True,encoded=False,packaged=False)
report['outputs']=[dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [O/'camp_texture_0.png',O/'camp_texture_1.png']]
(O/'review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
