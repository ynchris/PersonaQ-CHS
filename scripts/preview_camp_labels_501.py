import json,struct
from PIL import Image,ImageDraw,ImageFont,ImageChops
from preview_tutorials_468 import ROOT,digest
out=ROOT/'translation/previews_501';out.mkdir(exist_ok=True)
raw=(ROOT/'data/camp/c_main.spr3').read_bytes()
table=struct.unpack_from('<I',raw,28)[0]
original=Image.open(ROOT/'export_base/camp/c_main.spr3.00.png').convert('RGBA')
im=original.copy()
texts=['技能说明','卸下','详细说明','简要列表','丢弃','保存','删除','人格面具状态','播放','状态','角色状态','切换角色','切换人格面具','装备人格面具']
edits=[]
for index,text in enumerate(texts,206):
    offset=struct.unpack_from('<I',raw,table+8*index+4)[0]
    name=raw[offset+4:offset+24].split(b'\0')[0].decode('cp932')
    box=struct.unpack_from('<4i',raw,offset+84)
    x0,y0,x1,y1=box
    patch=Image.new('RGBA',((x1-x0)*4,(y1-y0)*4))
    d=ImageDraw.Draw(patch);font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',44)
    b=d.textbbox((0,0),text,font=font)
    assert b[2]-b[0]+8<=patch.width
    left=(patch.width-b[2]+b[0])/2-b[0] if index==215 else 4-b[0]
    d.text((left,(patch.height-b[3]+b[1])/2-b[1]),text,font=font,fill='#333333',stroke_width=4,stroke_fill='white')
    im.paste(patch.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS),box[:2])
    edits.append(dict(index=index,source_name=name,box=box,text=text))
check=im.copy()
for e in edits:check.paste(original.crop(e['box']),e['box'][:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,original).split())
target=out/'c_main.spr3.00.png';im.save(target)
pair=Image.new('RGBA',(1032,512),'#cccccc')
pair.alpha_composite(original,(0,0));pair.alpha_composite(im,(520,0))
pair.save(out/'camp_full_compare.png')
details=Image.new('RGBA',(260,14*24),'#eeeeee')
for row,e in enumerate(edits):
    details.alpha_composite(original.crop(e['box']),(8,row*24+3))
    details.alpha_composite(im.crop(e['box']),(138,row*24+3))
details.resize((780,1008),Image.Resampling.NEAREST).save(out/'camp_labels_compare.png')
(out/'review.json').write_text(json.dumps(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),status='pending_user_visual_review',edits=edits,outside_boxes_rgba_unchanged=True,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
