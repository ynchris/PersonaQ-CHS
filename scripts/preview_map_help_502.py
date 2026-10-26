import json,struct
from PIL import Image,ImageDraw,ImageFont,ImageChops
from preview_tutorials_468 import ROOT,digest
out=ROOT/'translation/previews_502';out.mkdir(exist_ok=True)
original=Image.open(ROOT/'export_base/mapdat/tex/map_tutorial.spr3.00.png').convert('RGBA')
bg=Image.new('RGBA',original.size,'#555555');bg.alpha_composite(original)
bg.resize((1024,256),Image.Resampling.NEAREST).save(out/'inspect.png')
raw=(ROOT/'data/mapdat/tex/map_tutorial.spr3').read_bytes()
table=struct.unpack_from('<I',raw,28)[0]
im=original.copy()
specs=[(3,'返回目录',12,'#ffff00'),(4,'关闭',12,'#ffff00'),
       (55,'绘制和擦除墙壁',13,'white'),(56,'填涂和擦除地面',13,'white'),
       (57,'放置和删除图标',13,'white'),(58,'更改图标颜色和类型',13,'white'),
       (59,'图标类型',13,'white'),(60,'切换显示楼层',13,'white'),
       (61,'旋转地图',13,'white'),(62,'撤销操作',13,'white'),
       (63,'自动行走的使用方法',13,'white')]
edits=[]
for index,text,size,color in specs:
    offset=struct.unpack_from('<I',raw,table+index*8+4)[0]
    box=struct.unpack_from('<4i',raw,offset+84)
    x0,y0,x1,y1=box
    patch=Image.new('RGBA',((x1-x0)*4,(y1-y0)*4))
    d=ImageDraw.Draw(patch);f=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',size*4)
    b=d.textbbox((0,0),text,font=f)
    assert b[2]-b[0]<patch.width and b[3]-b[1]<patch.height
    d.text(((patch.width-b[2]+b[0])/2-b[0],(patch.height-b[3]+b[1])/2-b[1]),text,font=f,fill=color)
    im.paste(patch.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS),box[:2])
    edits.append(dict(index=index,box=box,text=text))
check=im.copy()
for e in edits:check.paste(original.crop(e['box']),e['box'][:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,original).split())
target=out/'map_tutorial.spr3.00.png';im.save(target)
pair=Image.new('RGBA',(1032,128),'#555555')
pair.alpha_composite(original,(0,0));pair.alpha_composite(im,(520,0))
pair.resize((1548,192),Image.Resampling.NEAREST).save(out/'map_full_compare.png')
details=Image.new('RGBA',(436,len(edits)*27),'#555555')
for row,e in enumerate(edits):
    details.alpha_composite(original.crop(e['box']),(4,row*27+2))
    details.alpha_composite(im.crop(e['box']),(224,row*27+2))
details.resize((872,len(edits)*54),Image.Resampling.NEAREST).save(out/'map_labels_compare.png')
(out/'review.json').write_text(json.dumps(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),status='pending_user_visual_review',edits=edits,outside_boxes_rgba_unchanged=True,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
