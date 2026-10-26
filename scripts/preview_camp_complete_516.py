"""Camp atlas follow-up, PNG review only. Start from approved 501."""
import json,struct
from PIL import Image,ImageDraw,ImageFont,ImageChops
from preview_tutorials_468 import ROOT,digest
out=ROOT/'translation/previews_516';out.mkdir(exist_ok=True)
original=Image.open(ROOT/'export_base/camp/c_main.spr3.00.png').convert('RGBA')
base=Image.open(ROOT/'translation/previews_501/c_main.spr3.00.png').convert('RGBA')
im=base.copy()
raw=(ROOT/'data/camp/c_main.spr3').read_bytes();table=struct.unpack_from('<I',raw,28)[0]
def rect(index):
    p=struct.unpack_from('<I',raw,table+8*index+4)[0]
    return struct.unpack_from('<4i',raw,p+84)
arcana=json.loads((ROOT/'translation/code_extra_458.review.json').read_text(encoding='utf-8'))['files'][0]['rows'][:22]
specs=[]
for i,row in enumerate(arcana,1):
    if row['original']!=row['translation']:
        specs.append((i,row['translation'],13,'arcana'))
specs += [(i,text,size,'labels') for i,text,size in [
    (225,'攻击力',11.5),(226,'防御力',11.5),
    (360,'道具',12),(361,'关键道具',12),(355,'个',13),
]]
specs += [(i,text,14,'symbols') for i,text in [(73,'斩'),(74,'坏'),(77,'冰'),(79,'风'),(81,'暗'),(92,'远'),(468,'无')]]
edits=[]
for i,text,size,group in specs:
    box=rect(i);l,t,r,b=box
    patch=Image.new('RGBA',((r-l)*4,(b-t)*4));d=ImageDraw.Draw(patch)
    f=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',int(size*4))
    bb=d.textbbox((0,0),text,font=f)
    assert bb[2]-bb[0]<=patch.width and bb[3]-bb[1]<=patch.height,(i,text,box)
    x=(patch.width-bb[2]+bb[0])/2-bb[0]
    y=(patch.height-bb[3]+bb[1])/2-bb[1]
    d.text((x,y),text,font=f,fill='white')
    im.paste(patch.resize((r-l,b-t),Image.Resampling.LANCZOS),(l,t))
    edits.append(dict(index=i,box=box,text=text,size=size,group=group))
check=im.copy()
for e in edits:check.paste(base.crop(e['box']),e['box'][:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,base).split())
for e in json.loads((ROOT/'translation/previews_501/review.json').read_text(encoding='utf-8'))['edits']:
    assert im.crop(e['box']).tobytes()==base.crop(e['box']).tobytes()
target=out/'c_main.spr3.00.png';im.save(target)
for bg,name in [('black','dark'),('#cccccc','light')]:
    pair=Image.new('RGBA',(1032,512),bg);pair.alpha_composite(original);pair.alpha_composite(im,(520,0));pair.save(out/f'camp_full_{name}.png')
for group in ['arcana','labels','symbols']:
    selected=[e for e in edits if e['group']==group]
    if group=='arcana':
        selected=[dict(box=rect(i)) for i in range(1,23)]
    details=Image.new('RGBA',(300,42*len(selected)),'#222222')
    for row,e in enumerate(selected):
        for col,source in enumerate([original,im]):details.alpha_composite(source.crop(e['box']),(col*150+5,row*42+3))
    details.resize((600,details.height*2),Image.Resampling.NEAREST).save(out/f'{group}_compare.png')
(out/'review.json').write_text(json.dumps(dict(status='pending_user_visual_review',png=target.relative_to(ROOT).as_posix(),sha256=digest(target),base_png='translation/previews_501/c_main.spr3.00.png',edits=edits,approved_501_labels_unchanged=True,outside_boxes_rgba_unchanged=True,encoded=False,packaged=False,english_policy='User explicitly requested retaining all English; this revision starts from 501 and discards all unapproved English edits.',notes=['User requires single-cell 壊 to use 坏; full attribute name remains 破坏属性.','Arcana translations follow code_extra_458; identical names retained pixel-for-pixel.','Any earlier titles_compare.png is obsolete and is not an import asset.']),ensure_ascii=False,indent=2),encoding='utf-8')
print('New edits:',len(edits))
