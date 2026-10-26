"""Revise status-label size and restore source tutorial emphasis colors only."""
import json
from collections import Counter
from PIL import Image,ImageDraw,ImageFont,ImageChops
import preview_tutorials_468 as render
from preview_tutorials_468 import ROOT,label,digest

out=ROOT/'translation/previews_481'
out.mkdir(exist_ok=True)
records=[]
render.FONT='C:/Windows/Fonts/msyhbd.ttc'
for n in (26,27):
    old=Image.open(ROOT/f'translation/previews_480/t{n:03}.ctpk.00.png').convert('RGBA')
    original=Image.open(ROOT/f'export_base/tutorial/t{n:03}.ctpk.00.png').convert('RGBA')
    im=old.copy();boxes=[]
    if n==26:
        for box in [(32,45,59,57),(32,59,59,71)]:
            label(im,box,'受理中','#00383c','#00d6e5',size=9)
            boxes.append(box)
        note='受理中7→9像素，位置不变'
    else:
        pixels=list(original.crop((83,54,134,65)).getdata())
        colors=Counter(p for p in pixels if p[0]>p[1]+12 and p[0]>80)
        assert colors,'Source emphasis color not found'
        accent=colors.most_common(1)[0][0]
        for box,parts in [((35,52,239,65),[('从菜单的“',False),('校内漫步',True),('”中选择',False)]),
                          ((35,65,239,78),[('“',False),('以物易物对决',True),('”进行挑战。',False)])]:
            x0,y0,x1,y1=box
            patch=Image.new('RGBA',((x1-x0)*4,(y1-y0)*4),original.getpixel((245,78)))
            d=ImageDraw.Draw(patch);f=ImageFont.truetype(render.FONT,36)
            full=''.join(t for t,_ in parts);b=d.textbbox((0,0),full,font=f)
            x=-b[0];y=(patch.height-(b[3]-b[1]))//2-b[1]
            for text,emphasis in parts:
                d.text((x,y),text,font=f,fill=accent if emphasis else '#325052')
                x+=d.textlength(text,font=f)
            im.paste(patch.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS),(x0,y0));boxes.append(box)
        note=f'校内漫步、以物易物对决使用原图强调色{accent}'
        print(note)
    check=im.copy()
    for box in boxes:check.paste(old.crop(box),box[:2])
    assert ImageChops.difference(check,old).convert('RGB').getbbox() is None
    target=out/f't{n:03}.ctpk.00.png';im.save(target)
    pair=Image.new('RGBA',(592,184),'black')
    pair.paste(original.crop((0,0,296,184)),(0,0));pair.paste(im.crop((0,0,296,184)),(296,0))
    pair.resize((1184,368),Image.Resampling.NEAREST).save(out/f't{n:03}_compare.png')
    records.append(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),change=note,outside_edit_boxes_unchanged=True,status='pending_user_review',reward_name_still_pending_cross_check=True))
(out/'review.json').write_text(json.dumps(dict(images=records,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
