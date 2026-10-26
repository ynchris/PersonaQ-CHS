"""Dialogue button atlas, all visible duplicate states; PNG-only review."""
import json
from PIL import Image,ImageDraw,ImageFont,ImageChops,ImageFilter
from preview_tutorials_468 import ROOT,digest

out=ROOT/'translation/previews_492';out.mkdir(exist_ok=True)
src=ROOT/'export_base/event/skip_btn.spr3.00.png'
original=Image.open(src).convert('RGBA');im=original.copy()
specs=[((35,63,94,78),'对话回顾',11,33),((107,25,182,40),'隐藏窗口',10,106),
       ((109,63,181,77),'快速跳过',11,107),((199,63,254,78),'A键',11,196),
       ((340,20,414,33),'快速跳过',10,338),((425,20,496,33),'快速跳过',10,423),
       ((36,151,93,166),'全部跳过',10,33),((123,144,183,160),'全部跳过',10,122),
       ((193,144,255,160),'对话回顾',11,193),((265,105,340,121),'隐藏窗口',10,264),
       ((265,144,340,160),'快速跳过',11,264),((350,144,410,160),'A键',11,350),
       ((123,219,183,234),'全部跳过',10,122),((193,219,255,234),'对话回顾',11,193),
       ((265,180,340,196),'隐藏窗口',10,264),((265,219,340,234),'快速跳过',11,264),
       ((350,219,410,234),'A键',11,350)]
# Overlapping icon/text backgrounds need a separate reconstruction pass.
# Keep these three buttons original rather than shipping residual kana or damaged icons.
specs=[s for s in specs if s[1]!='隐藏窗口']
for box,text,size,sample_x in specs:
    x0,y0,x1,y1=box
    for y in range(y0,y1):
        color=original.getpixel((sample_x,y))
        for x in range(x0,x1):im.putpixel((x,y),color)
    if text=='隐藏窗口':
        # Preserve the pale-blue icon wherever it does not intersect old white text.
        old=original.crop(box);mask=Image.new('L',old.size)
        for yy in range(old.height):
            for xx in range(old.width):
                r,g,b,a=old.getpixel((xx,yy))
                if r>170 and g>180 and b>180:mask.putpixel((xx,yy),255)
        mask=mask.filter(ImageFilter.MaxFilter(3))
        clean=old.copy()
        for yy in range(old.height):
            for xx in range(old.width):
                if not mask.getpixel((xx,yy)):continue
                candidates=[]
                for cy in range(max(0,yy-5),min(old.height,yy+6)):
                    for cx in range(max(0,xx-5),min(old.width,xx+6)):
                        if not mask.getpixel((cx,cy)):
                            candidates.append(((cx-xx)**2+(cy-yy)**2,cx,cy))
                if candidates:
                    _,cx,cy=min(candidates);clean.putpixel((xx,yy),old.getpixel((cx,cy)))
                else:clean.putpixel((xx,yy),original.getpixel((sample_x,y0+yy)))
        im.paste(clean,box[:2])
    patch=Image.new('RGBA',((x1-x0)*4,(y1-y0)*4))
    d=ImageDraw.Draw(patch);f=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',size*4)
    b=d.textbbox((0,0),text,font=f)
    assert b[2]-b[0]<=patch.width
    d.text(((patch.width-b[2]+b[0])//2-b[0],(patch.height-b[3]+b[1])//2-b[1]),text,font=f,fill='white')
    im.alpha_composite(patch.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS),(x0,y0))
check=im.copy()
for box,*_ in specs:check.paste(original.crop(box),box[:2])
assert ImageChops.difference(check,original).convert('RGB').getbbox() is None
assert ImageChops.difference(check.getchannel('A'),original.getchannel('A')).getbbox() is None
target=out/'skip_btn.spr3.00.png';im.save(target)
pair=Image.new('RGBA',(1024,256),'#eeeeee')
pair.alpha_composite(original,(0,0));pair.alpha_composite(im,(512,0))
pair.resize((1536,384),Image.Resampling.NEAREST).save(out/'dialogue_buttons_compare.png')
(out/'review.json').write_text(json.dumps(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),edits=specs,status='pending_user_review',outside_labels_and_alpha_unchanged=True,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
