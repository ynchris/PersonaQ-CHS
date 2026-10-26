"""PNG-only result and facility prompts; no repacking."""
import json
from PIL import Image, ImageDraw, ImageFont, ImageChops
from preview_tutorials_468 import ROOT, digest

out=ROOT/'translation/previews_514'
out.mkdir(exist_ok=True)
specs=[
    ('battle/result/persona_get.bin_card.spr3.00.png',(169,279,225,297),'获得',10,None,(160,275,232,302)),
    ('facility/root_image.spr3.00.png',(354,216,398,232),'选择',14,'white',(300,209,400,240)),
]
records=[]
for rel,box,text,size,bg,crop in specs:
    original=Image.open(ROOT/'export_base'/rel).convert('RGBA')
    im=original.copy()
    l,t,r,b=box
    layer=Image.new('RGBA',((r-l)*4,(b-t)*4),bg)
    d=ImageDraw.Draw(layer)
    font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',size*4)
    bb=d.textbbox((0,0),text,font=font)
    x=8 if bg is None else 0
    assert bb[2]-bb[0]+x+8<=layer.width
    d.text((x-bb[0],(layer.height-bb[3]+bb[1])/2-bb[1]),text,font=font,fill='#333333',stroke_width=6 if bg is None else 0,stroke_fill='white')
    im.paste(layer.resize((r-l,b-t),Image.Resampling.LANCZOS),(l,t))
    check=im.copy();check.paste(original.crop(box),(l,t))
    assert not any(c.getbbox() for c in ImageChops.difference(check,original).split())
    if rel.startswith('facility/'):
        assert im.crop((326,216,354,232)).tobytes() == original.crop((326,216,354,232)).tobytes(), 'Original 上下 must remain pixel-identical'
    target=out/rel.split('/')[-1];im.save(target)
    full=Image.new('RGBA',(im.width*2+8,im.height),'#bbbbbb')
    full.alpha_composite(original,(0,0));full.alpha_composite(im,(im.width+8,0))
    full.save(out/(target.stem+'.full.png'))
    w,h=crop[2]-crop[0],crop[3]-crop[1]
    pair=Image.new('RGBA',(w*2+8,h),'#bbbbbb')
    pair.alpha_composite(original.crop(crop),(0,0));pair.alpha_composite(im.crop(crop),(w+8,0))
    pair.resize((pair.width*3,pair.height*3),Image.Resampling.NEAREST).save(out/(target.stem+'.detail.png'))
    records.append(dict(source='export_base/'+rel,png=target.relative_to(ROOT).as_posix(),sha256=digest(target),box=box,text=text,size=size,outside_boxes_rgba_unchanged=True))
(out/'review.json').write_text(json.dumps(dict(status='pending_user_visual_review',assets=records,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
