"""Isolated cursor-label font correction; PNG review only, no ROM changes."""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'translation/previews_573'
OUT.mkdir(exist_ok=True)
source=ROOT/'translation/previews_552/camp_texture_1.png'
old=Image.open(source).convert('RGBA');new=old.copy()
box=(67,183,157,198);w,h=90,15
hi=Image.new('RGBA',(w*4,h*4))
d=ImageDraw.Draw(hi)
font=ImageFont.truetype(str(ROOT/'fonts/SourceHanSansSC-Medium.otf'),52)
label='记忆光标位置'
bb=d.textbbox((0,0),label,font=font)
d.text(((w*4-(bb[2]-bb[0]))/2-bb[0],(h*4-(bb[3]-bb[1]))/2-bb[1]),label,font=font,fill='white')
patch=hi.resize((w,h),Image.Resampling.LANCZOS)
new.paste(patch,box[:2])
check=new.copy();check.paste(old.crop(box),box[:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,old).split())
target=OUT/'camp_texture_1.png';new.save(target)
pair=Image.new('RGB',(204,23),'#ffff00')
for x,atlas in [(4,old),(106,new)]:
    ink=atlas.crop(box).getchannel('A')
    pair.paste((30,30,30),(x,4,x+w,4+h),ink)
pair.resize((816,92),Image.Resampling.NEAREST).save(OUT/'cursor_compare.png')
(OUT/'review.json').write_text(json.dumps(dict(status='pending_user_visual_review',source=str(source.relative_to(ROOT)),png=str(target.relative_to(ROOT)),box=box,text=label,font='SourceHanSansSC-Medium.otf',size=13,previous_font='Microsoft YaHei Bold',outside_box_unchanged=True,encoded=False,packaged=False,sha256=hashlib.sha256(target.read_bytes()).hexdigest()),ensure_ascii=False,indent=2),encoding='utf-8')
print(target)
