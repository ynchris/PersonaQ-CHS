"""PNG-only review: reconstruct the crossed circular icon by 180-degree symmetry."""
import json
from PIL import Image, ImageDraw, ImageFont, ImageChops
from preview_tutorials_468 import ROOT,digest
out=ROOT/'translation/previews_493';out.mkdir(exist_ok=True)
src=ROOT/'export_base/event/skip_btn.spr3.00.png'
original=Image.open(src).convert('RGBA')
approved=Image.open(ROOT/'translation/previews_492/skip_btn.spr3.00.png').convert('RGBA')
im=approved.copy()
specs=[((107,25,182,40),(145,24),106),((265,106,340,121),(302,105),264),((265,181,340,196),(302,180),264)]
for box,(cx,cy),sample in specs:
    x0,y0,x1,y1=box
    for y in range(y0,y1):
        bg=original.getpixel((sample,y))
        for x in range(x0,x1):
            color=bg
            if cx-17<=x<=cx+17 and y<=cy+14:
                donor=original.getpixel((2*cx-x,2*cy-y))
                donor_bg=original.getpixel((sample,2*cy-y))
                if donor[0]>donor_bg[0]+8:
                    color=tuple(max(0,min(255,bg[k]+donor[k]-donor_bg[k])) for k in range(3))+(bg[3],)
            im.putpixel((x,y),color)
    patch=Image.new('RGBA',((x1-x0)*4,(y1-y0)*4))
    d=ImageDraw.Draw(patch);font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',40)
    b=d.textbbox((0,0),'隐藏窗口',font=font)
    d.text(((patch.width-(b[2]-b[0]))/2-b[0],(patch.height-(b[3]-b[1]))/2-b[1]),'隐藏窗口',font=font,fill='white')
    im.alpha_composite(patch.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS),(x0,y0))
check=im.copy()
for box,*_ in specs:check.paste(approved.crop(box),box[:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,approved).split())
assert im.getchannel('A').tobytes()==approved.getchannel('A').tobytes()
target=out/'skip_btn.spr3.00.png';im.save(target)
canvas=Image.new('RGB',(688,472),'#eeeeee');draw=ImageDraw.Draw(canvas)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
draw.text((12,4),'原图',font=font,fill='black');draw.text((356,4),'汉化预览',font=font,fill='black')
for row,box in enumerate([(104,8,187,42),(261,89,344,123),(261,164,344,198)]):
    for col,source in enumerate([original,im]):
        crop=source.crop(box).resize((332,136),Image.Resampling.NEAREST)
        canvas.paste(crop,(col*344+6,30+row*146))
canvas.save(out/'hide_window_compare.png')
(out/'review.json').write_text(json.dumps(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),status='pending_user_review',changed_boxes=[s[0] for s in specs],approved_492_outside_boxes_unchanged=True,alpha_unchanged=True,icon_reconstruction='180-degree symmetry of unobscured upper icon; requires visual review',encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
