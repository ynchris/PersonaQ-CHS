"""Align replacement pink glyphs to the original row metrics, not slot centres."""
import hashlib
from PIL import Image,ImageDraw,ImageFont
from compile_translation import ROOT,write
out=ROOT/'translation/previews_559';out.mkdir(exist_ok=True)
original=Image.open(ROOT/'translation/feedback_543/secondary_decoded/13.ctpk.00.png').convert('RGBA')
before=Image.open(ROOT/'translation/previews_546/pink.ctpk.00.png').convert('RGBA');after=before.copy()
specs=[(90,0,'斩'),(124,0,'坏'),(158,0,'冰'),(175,0,'风'),(124,17,'暗'),(175,17,'无'),(210,34,'运')]
metrics=[]
for x,y,text in specs:
    box=(x,y,x+17,y+17)
    oldbox=original.crop(box).getchannel('A').point(lambda v:255 if v>=128 else 0).getbbox()
    # Common row baseline and 12px ink height; retain original horizontal centre.
    width=min(14,oldbox[2]-oldbox[0]);height=12
    left=round((oldbox[0]+oldbox[2]-width)/2);top=oldbox[3]-height
    mask=Image.new('L',(100,100));d=ImageDraw.Draw(mask);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',64)
    bb=d.textbbox((0,0),text,font=font);d.text((4-bb[0],4-bb[1]),text,font=font,fill=255)
    mask=mask.crop(mask.getbbox()).resize((width,height),Image.Resampling.LANCZOS)
    patch=Image.new('RGBA',(17,17));glyph=Image.new('RGBA',(width,height),'#ff7e7c');glyph.putalpha(mask);patch.alpha_composite(glyph,(left,top));after.paste(patch,(x,y))
    metrics.append(dict(text=text,box=box,original_ink_bbox=oldbox,previous_ink_bbox=before.crop(box).getchannel('A').point(lambda v:255 if v>=128 else 0).getbbox(),new_ink_bbox=patch.getchannel('A').point(lambda v:255 if v>=128 else 0).getbbox(),target_baseline=oldbox[3]))
check=after.copy()
for m in metrics:check.paste(original.crop(m['box']),m['box'][:2])
assert check.tobytes()==original.tobytes()
target=out/'pink.ctpk.00.png';after.save(target)
pair=Image.new('RGBA',(520,256),'#444444');pair.alpha_composite(original);pair.alpha_composite(after,(264,0));pair.resize((1040,512),Image.Resampling.NEAREST).save(out/'full_compare.png')
strip=Image.new('RGBA',(520,54),'#444444');strip.alpha_composite(original.crop((0,0,256,54)));strip.alpha_composite(after.crop((0,0,256,54)),(264,0));strip.resize((1560,162),Image.Resampling.NEAREST).save(out/'rows_compare.png')
write(out/'review.json',dict(status='pending_user_visual_review',png=target.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),metrics=metrics,outside_glyph_boxes_unchanged=True,encoded=False,packaged=False))
print(metrics)
