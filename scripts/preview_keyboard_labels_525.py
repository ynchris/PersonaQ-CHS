"""Keyboard labels only; original key glyphs and geometry stay unchanged."""
import json, hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops
ROOT=Path(__file__).resolve().parent
out=ROOT/'translation/previews_525';out.mkdir(exist_ok=True)
source='export_base/init/nameentry.arc_key_board_button.ctpk.00.png'
original=Image.open(ROOT/source).convert('RGBA');im=original.copy()
specs=[((49,249,99,264),'随机',11),((419,269,454,286),'确定',16),
       ((419,289,506,309),'取消',16),((251,211,280,228),'符号',14),
       ((1,255,23,269),'删除',11)]
for box,text,size in specs:
    # Small labels render at native resolution: avoid downsampling halos
    # and loss of opacity around strokes on the transparent atlas.
    scale=1 if text in ['删除','随机'] else 4
    l,t,r,b=box;patch=Image.new('RGBA',((r-l)*scale,(b-t)*scale))
    d=ImageDraw.Draw(patch)
    face='msyhbd.ttc' if text in ['确定','取消','删除','随机'] else 'msyh.ttc'
    font=ImageFont.truetype('C:/Windows/Fonts/'+face,size*scale)
    bb=d.multiline_textbbox((0,0),text,font=font,spacing=0)
    assert bb[2]-bb[0]<=patch.width and bb[3]-bb[1]<=patch.height,(text,bb)
    # User-requested 2px right shift: visible left edge matches 确定.
    x=2*scale-bb[0] if text=='取消' else (patch.width-bb[2]+bb[0])/2-bb[0]
    y=(patch.height-bb[3]+bb[1])/2-bb[1]
    d.multiline_text((x,y),text,font=font,fill='white',spacing=0,align='center')
    if scale==1:
        # Keep core strokes fully white; native antialiasing needs no
        # additional sharpening or contrast operation.
        im.paste(patch,box[:2])
    else:
        im.paste(patch.resize((r-l,b-t),Image.Resampling.LANCZOS),box[:2])
check=im.copy()
for box,*_ in specs:check.paste(original.crop(box),box[:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,original).split())
def ink_left(box):
    bounds=im.crop(box).getchannel('A').point(lambda v:255 if v>=128 else 0).getbbox()
    return box[0]+bounds[0]
assert ink_left((419,269,454,286))==ink_left((419,289,506,309))
target=out/'nameentry.arc_key_board_button.ctpk.00.png';im.save(target)
for color,name in [('#222222','dark'),('#cccccc','light')]:
    canvas=Image.new('RGBA',(1032,512),color);canvas.alpha_composite(original);canvas.alpha_composite(im,(520,0));canvas.save(out/f'keyboard_full_{name}.png')
crop=(0,208,512,312)
detail=Image.new('RGBA',(1032,104),'#222222');detail.alpha_composite(original.crop(crop));detail.alpha_composite(im.crop(crop),(520,0))
detail.resize((2064,208),Image.Resampling.NEAREST).save(out/'labels_compare.png')
focus=(0,245,114,289)
panel=Image.new('RGBA',(238,44),'#222222')
panel.alpha_composite(original.crop(focus));panel.alpha_composite(im.crop(focus),(124,0))
panel.resize((1190,220),Image.Resampling.NEAREST).save(out/'small_labels_compare.png')
focus=(415,264,512,312)
panel=Image.new('RGBA',(204,48),'#222222')
panel.alpha_composite(original.crop(focus));panel.alpha_composite(im.crop(focus),(107,0))
panel.resize((1020,240),Image.Resampling.NEAREST).save(out/'confirm_cancel_compare.png')
sources=[]
for p in sorted((ROOT/'export_base/init').glob('*key_board_button.ctpk.00.png')):
    sources.append(dict(source=p.relative_to(ROOT).as_posix(),identical_pixels=Image.open(p).convert('RGBA').tobytes()==original.tobytes()))
(out/'review.json').write_text(json.dumps(dict(status='pending_user_visual_review',source=source,png=target.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),edits=specs,related_textures=sources,outside_boxes_rgba_unchanged=True,pinyin_implemented=False,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
print('Five labels previewed; unchanged kana keyboard. Related texture matches:',sources)
