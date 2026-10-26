"""Three PNG-only tutorial previews, preserving non-text source pixels."""
import json
import preview_tutorials_468 as rendering
from PIL import Image, ImageDraw, ImageChops
from preview_tutorials_468 import ROOT, label, digest

OUT=ROOT/'translation/previews_469'

def main():
    OUT.mkdir(exist_ok=True)
    records=[]
    approved=ROOT/'translation/previews_468/t002.ctpk.00.png'
    assert digest(approved)=='997c8abadb9e2315a118fcf1406bd492e17042b61f9b86725fc399b978d3107a'
    for n in (29,35,37):
        src=ROOT/f'export_base/tutorial/t{n:03}.ctpk.00.png'
        original=Image.open(src).convert('RGBA')
        im=original.copy()
        boxes=[]
        labels=[]
        if n==29:
            donor=Image.open(approved).convert('RGBA')
            for box in [(38,47,132,63),(160,47,260,63),(54,63,116,80),(179,63,242,80)]:
                im.paste(donor.crop(box),(box[0],box[1]))
                boxes.append(box)
            labels=['角色的','副人格面具的','HP与SP']
        else:
            if n==35:
                specs=[((23,20,120,38),'异常状态效果',14,'#980000'),
                       ((59,53,99,71),'即死',12,'black'),
                       ((131,53,168,71),'石化',12,'black'),
                       ((59,75,99,93),'诅咒',12,'black'),
                       ((131,75,168,93),'中毒',12,'black'),
                       ((59,97,99,114),'睡眠',12,'black'),
                       ((131,97,168,114),'混乱',12,'black'),
                       ((59,117,99,135),'麻痹',12,'black'),
                       ((204,53,246,71),'力封',12,'black'),
                       ((204,75,246,93),'速封',12,'black'),
                       ((204,97,246,114),'魔封',12,'black')]
            else:
                specs=[((51,48,149,67),'范围攻击效果',14,'#980000'),
                       ((73,79,137,99),'贯通效果',12,'black'),
                       ((178,79,242,99),'扩散效果',12,'black')]
            for box,text,size,color in specs:
                rendering.FONT='C:/Windows/Fonts/msyhbd.ttc' if size==14 else 'C:/Windows/Fonts/msyh.ttc'
                label(im,box,text,color,'white',size=size)
                boxes.append(box)
                labels.append(text)
            if n==35:
                rendering.FONT='C:/Windows/Fonts/msyh.ttc'
                # 呪 is a Japanese glyph inside the curse icon; retain its border.
                box=(43,78,55,89)
                label(im,box,'咒','black',(235,69,70,255),size=10,align='center')
                boxes.append(box)
        mask=Image.new('L',im.size,0)
        for x0,y0,x1,y1 in boxes:
            ImageDraw.Draw(mask).rectangle((x0,y0,x1-1,y1-1),fill=255)
        diff=ImageChops.difference(original,im)
        assert Image.composite(diff,Image.new('RGBA',im.size),(ImageChops.invert(mask))).getbbox() is None
        # Check RGB separately: alpha differences must not hide RGB changes.
        assert Image.composite(diff.convert('RGB'),Image.new('RGB',im.size),ImageChops.invert(mask)).getbbox() is None
        target=OUT/f't{n:03}.ctpk.00.png'
        im.save(target)
        compare=Image.new('RGBA',(592,184),'black')
        compare.paste(original.crop((0,0,296,184)),(0,0))
        compare.paste(im.crop((0,0,296,184)),(296,0))
        compare.resize((1184,368),Image.Resampling.NEAREST).save(OUT/f't{n:03}_compare.png')
        records.append(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),source=src.relative_to(ROOT).as_posix(),labels=labels,edit_boxes=boxes,outside_boxes_unchanged=True,status='pending_user_review'))
    (OUT/'review.json').write_text(json.dumps(dict(images=records,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
    print('3 PNG-only previews; outside edit rectangles unchanged.')

if __name__=='__main__':
    main()
