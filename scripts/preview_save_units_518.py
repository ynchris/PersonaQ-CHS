"""Save time unit and damaged marker, PNG-only review."""
import json
from PIL import Image,ImageDraw,ImageFont,ImageChops
from preview_tutorials_468 import ROOT,digest
out=ROOT/'translation/previews_518';out.mkdir(exist_ok=True)
original=Image.open(ROOT/'export_base/memcard/save_load.spr3.00.png').convert('RGBA')
base=Image.open(ROOT/'translation/previews_487/save_load.spr3.00.png').convert('RGBA')
im=base.copy()
specs=[((213,480,236,493),'小时',11),((258,103,287,118),'破损',12),((256,65,322,83),'切换存档槽',12),((122,346,153,365),'确定',13)]
for box,text,size in specs:
    l,t,r,b=box
    layer=Image.new('RGBA',((r-l)*4,(b-t)*4));d=ImageDraw.Draw(layer)
    f=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',size*4)
    outlined=text in ('切换存档槽','确定')
    bb=d.textbbox((0,0),text,font=f,stroke_width=4 if outlined else 0)
    assert bb[2]-bb[0]<=layer.width and bb[3]-bb[1]<=layer.height
    d.text(((layer.width-bb[2]+bb[0])/2-bb[0],(layer.height-bb[3]+bb[1])/2-bb[1]),text,font=f,fill='#333333' if outlined else 'white',stroke_width=4 if outlined else 0,stroke_fill='white')
    if text=='破损':
        # Right-leaning italic: shear at 4x, retaining the same rectangle/centre.
        slope=0.24
        layer=layer.transform(layer.size,Image.Transform.AFFINE,(1,slope,-slope*layer.height/2,0,1,0),resample=Image.Resampling.BICUBIC)
        ink=layer.getbbox()
        assert ink and ink[0]>0 and ink[2]<layer.width,'Italic must not clip'
    im.paste(layer.resize((r-l,b-t),Image.Resampling.LANCZOS),box[:2])
check=im.copy()
for box,*_ in specs:check.paste(base.crop(box),box[:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,base).split())
assert im.crop((287,102,331,119)).tobytes()==base.crop((287,102,331,119)).tobytes(),'DATA must be preserved'
target=out/'save_load.spr3.00.png';im.save(target)
for bg,name in [('#222222','dark'),('#cccccc','light')]:
    pair=Image.new('RGBA',(1032,512),bg);pair.alpha_composite(original);pair.alpha_composite(im,(520,0));pair.save(out/f'save_full_{name}.png')
detail=Image.new('RGBA',(200,104),'#222222')
for row,box in enumerate([(213,480,236,493),(256,102,331,119),(256,65,322,83),(122,346,153,365)]):
    for col,source in enumerate([original,im]):detail.alpha_composite(source.crop(box),(col*100+4,row*26+3))
detail.resize((800,416),Image.Resampling.NEAREST).save(out/'save_units_compare.png')
(out/'review.json').write_text(json.dumps(dict(status='pending_user_visual_review',png=target.relative_to(ROOT).as_posix(),sha256=digest(target),base_png='translation/previews_487/save_load.spr3.00.png',edits=specs,outside_boxes_rgba_unchanged=True,english_DATA_unchanged=True,notes=['分 is valid Chinese and retains original pixels.','User correction: 破损 in right-leaning italic, not 损坏.','切换存档槽 enlarged 10 to 12px; 确定 11 to 13px. White outlines and fixed sprite rectangles retained.'],encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
