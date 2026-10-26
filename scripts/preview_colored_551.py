"""Review-only colored glyph substitutions; preserve original outer frames."""
import hashlib
from statistics import median
from PIL import Image, ImageDraw, ImageFont, ImageChops
from compile_translation import ROOT, read, write

out=ROOT/'translation/previews_552';out.mkdir(exist_ok=True)
base=Image.open(ROOT/'translation/previews_550/camp_texture_1.png').convert('RGBA')
original=Image.open(ROOT/'translation/feedback_543/secondary_decoded/00.ctpk.00.png').convert('RGBA')
after=base.copy()
records={r['index']:r for r in read(ROOT/'translation/feedback_541/camp_sprite_records.json')}
specs=[(380,'斩'),(381,'坏'),(384,'冰'),(386,'风'),(388,'暗'),(391,'咒'),(408,'运')]
edits=[]
for idx,text in specs:
    l,t,r,b=records[idx]['box']; box=(l+3,t+3,l+17,t+17)
    src=original.crop(box)
    # The glyph and background use separate luminance bands. Reconstruct only
    # the 14px interior, row by row, retaining the original vertical shading.
    bg=Image.new('RGBA',(14,14)); fg=Image.new('RGBA',(14,14))
    lum=lambda p: .2126*p[0]+.7152*p[1]+.0722*p[2]
    allpx=sorted(list(src.getdata()),key=lum)
    bright=allpx[-20:]
    color=tuple(round(median(p[c] for p in bright)) for c in range(3))+(255,)
    for y in range(14):
        row=sorted([src.getpixel((x,y)) for x in range(14)],key=lum)
        dark=row[:5]
        shade=tuple(round(median(p[c] for p in dark)) for c in range(3))+(255,)
        for x in range(14): bg.putpixel((x,y),shade)
    if idx==386:
        # Row-wise sampling can retain bright horizontal strokes from 風.
        # Use a smooth gradient from the darkest original background pixels.
        anchors=[]
        for ya,yb in [(0,5),(9,14)]:
            pixels=sorted([src.getpixel((x,y)) for y in range(ya,yb) for x in range(14)],key=lum)[:12]
            anchors.append(tuple(round(median(p[c] for p in pixels)) for c in range(3)))
        for y in range(14):
            shade=tuple(round(anchors[0][c]*(1-y/13)+anchors[1][c]*y/13) for c in range(3))+(255,)
            for x in range(14):bg.putpixel((x,y),shade)
    mask=Image.new('L',(56,56));d=ImageDraw.Draw(mask)
    f=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',56)
    bb=d.textbbox((0,0),text,font=f)
    d.text(((56-bb[2]+bb[0])/2-bb[0],(56-bb[3]+bb[1])/2-bb[1]),text,font=f,fill=255)
    mask=mask.resize((14,14),Image.Resampling.LANCZOS)
    fg.paste(color,(0,0,14,14));bg=Image.composite(fg,bg,mask)
    after.paste(bg,box[:2]);edits.append(dict(index=idx,text=text,box=box,color=color))
check=after.copy()
for e in edits:check.paste(base.crop(e['box']),e['box'][:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,base).split())
target=out/'camp_texture_1.png';after.save(target)
ball_box=records[390]['box']
assert after.crop(ball_box).tobytes()==original.crop(ball_box).tobytes(), 'Black orb must remain original'
comparison_specs=specs[:5]+[(390,'')]+specs[5:]
pair=Image.new('RGBA',(100,len(comparison_specs)*25),'#444444')
for i,(idx,text) in enumerate(comparison_specs):
    box=records[idx]['box']
    pair.alpha_composite(original.crop(box),(10,i*25+2))
    pair.alpha_composite(after.crop(box),(65,i*25+2))
pair.resize((400,len(comparison_specs)*100),Image.Resampling.NEAREST).save(out/'icons_compare.png')
full=Image.new('RGBA',(1032,256),'#444444');full.alpha_composite(original);full.alpha_composite(after,(520,0));full.save(out/'full_compare.png')
write(out/'review.json',dict(status='pending_user_visual_review',png=str(target.relative_to(ROOT)),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),edits=edits,outside_boxes_rgba_unchanged=True,black_orb_rgba_identical_to_original=True,wind_background='smooth_gradient_no_row_sampling',encoded=False,packaged=False,shop_logo_pending='手工工坊'))
