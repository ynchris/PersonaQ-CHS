"""PNG-only corrections for the newly discovered second camp texture."""
import hashlib,json
from PIL import Image,ImageDraw,ImageFont,ImageChops
from compile_translation import ROOT,read,write
OUT=ROOT/'translation/previews_541'
OUT.mkdir(exist_ok=True)
source=ROOT/'translation/feedback_541/decoded/camp_c_main.spr3.tex1.ctpk.00.png'
original=Image.open(source).convert('RGBA');im=original.copy()
records={r['index']:r for r in read(ROOT/'translation/feedback_541/camp_sprite_records.json')}
specs=[(578,'记忆光标位置',13,'white'),(342,'技能',11,'white'),(341,'队长技能',11,'white'),
       (487,'切换显示',11,'plate'),(220,'返回',12,'plate')]
edits=[]
def render(box,text,size,mode):
    l,t,r,b=box;w,h=r-l,b-t
    patch=Image.new('RGBA',(w*4,h*4));d=ImageDraw.Draw(patch)
    font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',size*4)
    stroke=4 if mode in ('plate','outline') else 0
    bb=d.textbbox((0,0),text,font=font,stroke_width=stroke)
    assert bb[2]-bb[0]<=w*4 and bb[3]-bb[1]<=h*4,(text,box,bb)
    d.text(((w*4-bb[2]+bb[0])/2-bb[0],(h*4-bb[3]+bb[1])/2-bb[1]),text,font=font,
           fill='#333333' if mode in ('plate','outline') else 'white',stroke_width=stroke,stroke_fill='white')
    patch=patch.resize((w,h),Image.Resampling.LANCZOS)
    if mode=='plate':
        plate=Image.new('RGBA',(w,h),'white');plate.putalpha(original.crop(box).getchannel('A'))
        plate.alpha_composite(patch);patch=plate
    im.paste(patch,(l,t));edits.append(dict(box=box,text=text,size=size,mode=mode))
for index,text,size,mode in specs:render(records[index]['box'],text,size,mode)
# Preserve the original bidirectional arrow between these separate label regions.
render((120,144,166,162),'出战',12,'outline')
render((178,144,203,162),'候补',11,'outline')
assert im.crop((166,144,178,162)).tobytes()==original.crop((166,144,178,162)).tobytes()
check=im.copy()
for e in edits:check.paste(original.crop(e['box']),e['box'][:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,original).split())
target=OUT/'c_main.second.ctpk.00.png';im.save(target)
crops=[records[i]['box'] for i in [578,342,341,487,220]]+[(120,144,203,162)]
pair=Image.new('RGBA',(230,26*len(crops)),'#555555')
for row,box in enumerate(crops):
    for col,src in enumerate([original,im]):pair.alpha_composite(src.crop(box),(col*115+5,row*26+4))
pair.resize((690,pair.height*3),Image.Resampling.NEAREST).save(OUT/'labels_compare.png')
full=Image.new('RGBA',(1032,256),'#555555');full.alpha_composite(original);full.alpha_composite(im,(520,0));full.save(OUT/'full_compare.png')
write(OUT/'review.json',dict(status='pending_user_visual_review',source=source.relative_to(ROOT).as_posix(),
    container='data/camp/c_main.spr3',texture_offset=344624,png=target.relative_to(ROOT).as_posix(),
    sha256=hashlib.sha256(target.read_bytes()).hexdigest(),edits=edits,outside_boxes_rgba_unchanged=True,
    original_arrow_unchanged=True,encoded=False,packaged=False,
    pending='Other Japanese labels and colored attribute icons in this second texture still require review.'))
