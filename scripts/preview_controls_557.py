"""Revision 558: user prefers centered labels within the text region."""
import hashlib
from PIL import Image,ImageDraw,ImageFont
from compile_translation import ROOT,read,write
out=ROOT/'translation/previews_558';out.mkdir(exist_ok=True)
assets=[]
for unit,specs in [('05',[((24,18,123,35),'切换分类',12),((17,36,95,53),'道具info',12)]),('10',[((18,1,52,17),'确定',12),((71,1,106,17),'返回',12),((18,18,114,34),'关闭HELP',12),((18,35,96,51),'打开HELP',12),((18,52,85,68),'出战',12),((18,69,52,85),'候补',12)])]:
    original=Image.open(ROOT/f'translation/feedback_543/secondary_decoded/{unit}.ctpk.00.png').convert('RGBA')
    base=Image.open(ROOT/f'translation/previews_545/{unit}.ctpk.00.png').convert('RGBA');im=base.copy()
    for box,text,size in specs:
        l,t,r,b=box;w,h=r-l,b-t
        patch=Image.new('RGBA',(w*4,h*4));d=ImageDraw.Draw(patch);font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',size*4)
        bb=d.textbbox((0,0),text,font=font)
        assert bb[2]-bb[0] <= w*4-8
        d.text(((w*4-bb[2]+bb[0])/2-bb[0],(h*4-bb[3]+bb[1])/2-bb[1]),text,font=font,fill='#444444')
        patch=patch.resize((w,h),Image.Resampling.LANCZOS)
        plate=Image.new('RGBA',(w,h),'white');plate.putalpha(original.crop(box).getchannel('A'));plate.alpha_composite(patch)
        im.paste(plate,box[:2])
    check=im.copy()
    for box,*_ in specs:check.paste(base.crop(box),box[:2])
    assert check.tobytes()==base.tobytes()
    path=out/f'{unit}.ctpk.00.png';im.save(path)
    pair=Image.new('RGBA',(264,128),'#444444');pair.alpha_composite(original);pair.alpha_composite(im,(136,0));pair.resize((792,384),Image.Resampling.NEAREST).save(out/f'{unit}_full_compare.png')
    assets.append(dict(unit=unit,png=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),edits=specs,outside_boxes_unchanged=True))
write(out/'review.json',dict(status='pending_user_visual_review',alignment='center_in_text_region_excluding_button_icon',supersedes='previews_557',assets=assets,encoded=False,packaged=False))
