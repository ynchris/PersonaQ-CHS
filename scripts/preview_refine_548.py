"""Tight text backplates and pixel-exact original arrow; preserve history."""
import hashlib
from PIL import Image,ImageDraw,ImageFont,ImageChops
from compile_translation import ROOT,read,write
OUT=ROOT/'translation/previews_548';OUT.mkdir(exist_ok=True)
records={r['index']:r for r in read(ROOT/'translation/feedback_541/camp_sprite_records.json')}
original=Image.open(ROOT/'translation/feedback_543/secondary_decoded/00.ctpk.00.png').convert('RGBA')
prior=Image.open(ROOT/'translation/previews_547/camp_texture_1.png').convert('RGBA');im=prior.copy();boxes=[]
for index,text in [(604,'详细'),(220,'返回')]:
    box=records[index]['box'];l,t,r,b=box;w,h=r-l,b-t
    patch=Image.new('RGBA',(w*4,h*4));d=ImageDraw.Draw(patch);font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',48)
    bb=d.textbbox((0,0),text,font=font);tw,th=bb[2]-bb[0],bb[3]-bb[1]
    lx=(w*4-tw)/2;ty=(h*4-th)/2
    # 0.75 native pixel padding around ink, not the whole sprite rectangle.
    d.rounded_rectangle((lx-3,ty-3,lx+tw+2,ty+th+2),radius=5,fill='white')
    d.text((lx-bb[0],ty-bb[1]),text,font=font,fill='#333333')
    im.paste(patch.resize((w,h),Image.Resampling.LANCZOS),(l,t));boxes.append(box)
arrow=(186,214,201,234)
im.paste(original.crop(arrow),arrow[:2]);boxes.append(arrow)
assert im.crop(arrow).tobytes()==original.crop(arrow).tobytes()
check=im.copy()
for box in boxes:check.paste(prior.crop(box),box[:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,prior).split())
path=OUT/'camp_texture_1.png';im.save(path)
pair=Image.new('RGBA',(230,90),'#444444')
for row,box in enumerate([(151,214,227,234),records[604]['box'],records[220]['box']]):
    for col,src in enumerate([original,im]):pair.alpha_composite(src.crop(box),(col*115+5,row*30+4))
pair.resize((920,360),Image.Resampling.NEAREST).save(OUT/'original_corrected.png')
first=Image.open(ROOT/'translation/previews_547/camp_texture_0.png').convert('RGBA');first_before=first.copy()
for index in [208,210]:
    box=records[index]['box'];crop=first.crop(box);w,h=crop.size
    assert crop.getchannel('A').getbbox()[2]+2<=w
    shifted=Image.new('RGBA',(w,h));shifted.paste(crop,(2,0));first.paste(shifted,box[:2])
first_path=OUT/'camp_texture_0.png';first.save(first_path)
check=first.copy()
for index in [208,210]:
    box=records[index]['box'];check.paste(first_before.crop(box),box[:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,first_before).split())
sources=[Image.open(ROOT/p).convert('RGBA') for p in ['export_base/camp/c_main.spr3.00.png','translation/previews_501/c_main.spr3.00.png','translation/previews_548/camp_texture_0.png']]
history=Image.new('RGBA',(240,56),'#444444');metrics=[]
for row,index in enumerate([208,210]):
    box=records[index]['box']
    for col,src in enumerate(sources):
        crop=src.crop(box);history.alpha_composite(crop,(col*80+3,row*28+4))
        alpha=crop.getchannel('A').point(lambda x:255 if x>=128 else 0)
        dark=Image.new('L',crop.size)
        dark.putdata([255 if a>=128 and max(r,g,b)<150 else 0 for r,g,b,a in crop.getdata()])
        if col==2:assert dark.getbbox()[0]==5
        metrics.append(dict(sprite=index,version=['original','501','548'][col],alpha_bbox=alpha.getbbox(),dark_ink_bbox=dark.getbbox()))
history.resize((960,224),Image.Resampling.NEAREST).save(OUT/'history_spacing_compare.png')
write(OUT/'review.json',dict(status='pending_user_visual_review',png=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    first_texture_png=first_path.relative_to(ROOT).as_posix(),first_texture_sha256=hashlib.sha256(first_path.read_bytes()).hexdigest(),
    edits=boxes,original_arrow_rgba_identical=True,white_padding_pixels=0.75,outside_boxes_rgba_unchanged=True,metrics=metrics,encoded=False,packaged=False))
print(metrics)
