"""Opening caution translation preview; preserve original frame and padding."""
import json,hashlib
from collections import Counter
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops
ROOT=Path(__file__).resolve().parent
out=ROOT/'translation/previews_527';out.mkdir(exist_ok=True)
src=ROOT/'translation/opening_526/caution.tmx.png'
original=Image.open(src).convert('RGBA');im=original.copy()
title_box=(174,56,230,71);body_box=(31,79,373,155)
title_bg=Counter(original.crop(title_box).getdata()).most_common(1)[0][0]
body_bg=Counter(original.crop(body_box).getdata()).most_common(1)[0][0]
specs=[(title_box,['注意事项'],title_bg,13,0),
       (body_box,['未经权利人许可，通过互联网传播、分发游戏软件，',
                  '以及明知属于非法网络传播仍下载的行为，',
                  '均为法律所严禁。',
                  '敬请各位理解与配合。'],body_bg,13,19)]
for box,lines,bg,size,step in specs:
    l,t,r,b=box;patch=Image.new('RGBA',((r-l)*4,(b-t)*4),bg)
    d=ImageDraw.Draw(patch);f=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',size*4)
    for i,line in enumerate(lines):
        bb=d.textbbox((0,0),line,font=f)
        assert bb[2]-bb[0]<patch.width
        y=(patch.height-bb[3]+bb[1])/2-bb[1] if len(lines)==1 else (5+i*step)*4-bb[1]
        assert y+bb[3]<=patch.height
        d.text(((patch.width-bb[2]+bb[0])/2-bb[0],y),line,font=f,fill=(204,204,204,255))
    im.paste(patch.resize((r-l,b-t),Image.Resampling.LANCZOS),box[:2])
check=im.copy()
for box,*_ in specs:check.paste(original.crop(box),box[:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,original).split())
target=out/'caution.tmx.png';im.save(target)
canvas=Image.new('RGBA',(1032,256),'black');canvas.alpha_composite(original);canvas.alpha_composite(im,(520,0));canvas.save(out/'caution_full_compare.png')
# Actual top-screen viewport; unused 512px texture padding excluded only here.
canvas=Image.new('RGBA',(808,240),'black');canvas.alpha_composite(original.crop((0,0,400,240)));canvas.alpha_composite(im.crop((0,0,400,240)),(408,0));canvas.resize((1616,480),Image.Resampling.NEAREST).save(out/'caution_screen_compare.png')
(out/'review.json').write_text(json.dumps(dict(status='pending_user_visual_review',container='data/title/logo.bin',member='caution.tmx',source=src.relative_to(ROOT).as_posix(),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),png=target.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),edits=specs,outside_boxes_rgba_unchanged=True,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
print('Caution preview ready; frame unchanged; not encoded or packaged.')
