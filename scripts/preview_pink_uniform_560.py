"""One font, one size, shared baseline per row; no per-character rescaling."""
import hashlib
from PIL import Image,ImageDraw,ImageFont
from compile_translation import ROOT,write
out=ROOT/'translation/previews_560';out.mkdir(exist_ok=True)
original=Image.open(ROOT/'translation/feedback_543/secondary_decoded/13.ctpk.00.png').convert('RGBA')
after=original.copy();font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',52)
specs=[]
for y,text in [(0,'斩突坏炎冰风'),(17,'雷光暗弱耐无')]:
    for i,c in enumerate(text):specs.append(((90+i*17,y,107+i*17,y+17),c,13))
for box,c in zip([(130,34,149,51),(149,34,169,51),(170,34,189,51),(189,34,209,51),(209,34,229,51)],'力魔耐速运'):
    specs.append((box,c,12))
metrics=[]
for box,c,baseline in specs:
    l,t,r,b=box;w,h=r-l,b-t
    patch=Image.new('RGBA',(w*4,h*4));d=ImageDraw.Draw(patch)
    advance=d.textlength(c,font=font)
    # Baselines differ only with original row placement, never by character.
    d.text(((w*4-advance)/2,baseline*4),c,font=font,anchor='ls',fill='#ff7e7c')
    patch=patch.resize((w,h),Image.Resampling.LANCZOS)
    after.paste(patch,(l,t))
    metrics.append(dict(text=c,box=box,font_size=13,baseline=baseline,ink_bbox=patch.getchannel('A').point(lambda v:255 if v>=128 else 0).getbbox()))
check=after.copy()
for box,*_ in specs:check.paste(original.crop(box),box[:2])
assert check.tobytes()==original.tobytes()
target=out/'pink.ctpk.00.png';after.save(target)
for name,height,scale in [('full_compare',256,2),('rows_compare',52,3)]:
    pair=Image.new('RGBA',(520,height),'#444444');pair.alpha_composite(original.crop((0,0,256,height)));pair.alpha_composite(after.crop((0,0,256,height)),(264,0));pair.resize((520*scale,height*scale),Image.Resampling.NEAREST).save(out/f'{name}.png')
write(out/'review.json',dict(status='pending_user_visual_review',png=target.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),font='msyh.ttc',font_size=13,individual_glyph_scaling=False,metrics=metrics,outside_boxes_unchanged=True,encoded=False,packaged=False,supersedes='546 pink and 559'))
