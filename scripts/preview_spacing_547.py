"""Correct tested control spacing, arrow residue, and text backplates; PNG only."""
import hashlib
from PIL import Image,ImageDraw,ImageFont,ImageChops
from compile_translation import ROOT,read,write
OUT=ROOT/'translation/previews_547';OUT.mkdir(exist_ok=True)
records={r['index']:r for r in read(ROOT/'translation/feedback_541/camp_sprite_records.json')}
first=ROOT/'translation/previews_516/c_main.spr3.00.png'
second=ROOT/'translation/previews_546/camp.ctpk.00.png'
a=Image.open(first).convert('RGBA');b=Image.open(second).convert('RGBA');aa=a.copy();bb=b.copy();edits=[]
for index,text in [(208,'详细说明'),(210,'丢弃')]:
    box=records[index]['box'];patch=a.crop(box);w,h=patch.size
    alpha=patch.getchannel('A');ink=alpha.getbbox();dx=2
    assert ink[2]+dx<=w,(text,ink,w)
    shifted=Image.new('RGBA',(w,h));shifted.paste(patch,(dx,0));aa.paste(shifted,box[:2])
    assert shifted.getchannel('A').getbbox()[0]==ink[0]+dx
    edits.append(dict(texture=0,box=box,text=text,shift_x=dx,unchanged_sprite_rect=True))
for index,text in [(604,'详细'),(220,'返回')]:
    box=records[index]['box'];l,t,r,bottom=box;w,h=r-l,bottom-t
    patch=Image.new('RGBA',(w*4,h*4));d=ImageDraw.Draw(patch)
    font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',48)
    bounds=d.textbbox((0,0),text,font=font)
    tw,th=bounds[2]-bounds[0],bounds[3]-bounds[1]
    x=(w*4-tw)/2-bounds[0];y=(h*4-th)/2-bounds[1]
    d.rounded_rectangle((0,1,w*4-1,h*4-2),radius=8,fill='white')
    d.text((x,y),text,font=font,fill='#333333')
    assert x+bounds[0]>=4 and x+bounds[2]<=w*4-4
    bb.paste(patch.resize((w,h),Image.Resampling.LANCZOS),(l,t))
    edits.append(dict(texture=1,box=box,text=text,backplate='Full rounded white plate within unchanged sprite rectangle',font_size=12))
# The old crop preserved pixels from サ on the arrow's right. Mirror only the
# clean left half of this symmetric arrow, retaining its native pixel style.
arrowbox=(186,214,201,234);arrow=b.crop(arrowbox);clean=arrow.copy()
clean.paste(arrow.crop((0,0,7,20)).transpose(Image.Transpose.FLIP_LEFT_RIGHT),(8,0))
assert clean.crop((0,0,7,20)).tobytes()==arrow.crop((0,0,7,20)).tobytes()
bb.paste(clean,arrowbox[:2]);edits.append(dict(texture=1,box=arrowbox,text='主副切换箭头',symmetric_arrow_cleanup=True))
assets=[]
for n,prior,new,path in [(0,a,aa,first),(1,b,bb,second)]:
    check=new.copy()
    for e in edits:
        if e['texture']==n:check.paste(prior.crop(e['box']),e['box'][:2])
    assert not any(c.getbbox() for c in ImageChops.difference(check,prior).split())
    p=OUT/f'camp_texture_{n}.png';new.save(p)
    assets.append(dict(texture=n,base=path.relative_to(ROOT).as_posix(),png=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),outside_boxes_rgba_unchanged=True))
crops=[(0,records[208]['box']),(0,records[210]['box']),(1,(151,214,227,234)),(1,records[604]['box']),(1,records[220]['box'])]
pair=Image.new('RGBA',(230,len(crops)*30),'#444444')
for row,(n,box) in enumerate(crops):
    for col,im in enumerate(([a,aa] if n==0 else [b,bb])):pair.alpha_composite(im.crop(box),(col*115+5,row*30+4))
pair.resize((920,pair.height*4),Image.Resampling.NEAREST).save(OUT/'before_after.png')
originals=[Image.open(ROOT/'export_base/camp/c_main.spr3.00.png').convert('RGBA'),Image.open(ROOT/'translation/feedback_543/secondary_decoded/00.ctpk.00.png').convert('RGBA')]
reference=Image.new('RGBA',(230,len(crops)*30),'#444444')
for row,(n,box) in enumerate(crops):
    for col,im in enumerate([originals[n],[aa,bb][n]]):reference.alpha_composite(im.crop(box),(col*115+5,row*30+4))
reference.resize((920,reference.height*4),Image.Resampling.NEAREST).save(OUT/'original_corrected.png')
write(OUT/'review.json',dict(status='pending_user_visual_review',assets=assets,edits=edits,encoded=False,packaged=False,
    comparison='Left previous Chinese version; right corrected Chinese version.',
    alignment_note='Comparison sheets are not runtime layouts. Sprite UV rectangles remain unchanged; shifting ink inside a rectangle affects the runtime padding.'))
