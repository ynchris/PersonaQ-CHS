"""User-requested outlined text instead of solid plates for detail/back."""
import hashlib
from PIL import Image,ImageDraw,ImageFont,ImageChops
from compile_translation import ROOT,read,write
out=ROOT/'translation/previews_550';out.mkdir(exist_ok=True)
source=ROOT/'translation/previews_549/camp_texture_1.png'
before=Image.open(source).convert('RGBA');after=before.copy()
records={r['index']:r for r in read(ROOT/'translation/feedback_541/camp_sprite_records.json')}
edits=[]
for index,text in [(604,'详细'),(220,'返回')]:
    box=records[index]['box'];l,t,r,b=box;w,h=r-l,b-t
    patch=Image.new('RGBA',(w*4,h*4));d=ImageDraw.Draw(patch)
    font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',48)
    bb=d.textbbox((0,0),text,font=font,stroke_width=4)
    assert bb[2]-bb[0]<=w*4 and bb[3]-bb[1]<=h*4
    d.text(((w*4-bb[2]+bb[0])/2-bb[0],(h*4-bb[3]+bb[1])/2-bb[1]),text,font=font,
           fill='#333333',stroke_width=4,stroke_fill='white')
    after.paste(patch.resize((w,h),Image.Resampling.LANCZOS),(l,t))
    edits.append(dict(box=box,text=text,font_size=12,white_outline_pixels=1,solid_backplate=False))
check=after.copy()
for e in edits:check.paste(before.crop(e['box']),e['box'][:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,before).split())
target=out/'camp_texture_1.png';after.save(target)
pair=Image.new('RGBA',(230,90),'#444444')
for row,box in enumerate([(151,214,227,234),records[604]['box'],records[220]['box']]):
    for col,im in enumerate([before,after]):pair.alpha_composite(im.crop(box),(col*115+5,row*30+4))
pair.resize((920,360),Image.Resampling.NEAREST).save(out/'before_after.png')
write(out/'review.json',dict(status='pending_user_visual_review',base=source.relative_to(ROOT).as_posix(),
    png=target.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),edits=edits,
    outside_boxes_rgba_unchanged=True,arrow_549_unchanged=True,encoded=False,packaged=False))
