import json, struct
from PIL import Image, ImageDraw, ImageFont, ImageChops
from preview_tutorials_468 import ROOT,digest
out=ROOT/'translation/previews_499';out.mkdir(exist_ok=True)
raw=(ROOT/'data/facility/noffice.spr3').read_bytes()
table=struct.unpack_from('<I',raw,28)[0]
original=Image.open(ROOT/'export_base/facility/noffice.spr3.00.png').convert('RGBA')
im=original.copy()
translations=['治疗','查看委托','听取说明','离开房间','接受委托','报告委托','放弃委托','取消']
edits=[]
for index,text in enumerate(translations,17):
    offset=struct.unpack_from('<I',raw,table+8*index+4)[0]
    box=struct.unpack_from('<4i',raw,offset+84)
    x0,y0,x1,y1=box
    patch=Image.new('RGBA',((x1-x0)*4,(y1-y0)*4))
    d=ImageDraw.Draw(patch);font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',56)
    b=d.textbbox((0,0),text,font=font)
    d.text(((patch.width-b[2]+b[0])/2-b[0],(patch.height-b[3]+b[1])/2-b[1]),text,font=font,fill='white')
    im.paste(patch.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS),box[:2])
    edits.append(dict(index=index,box=box,text=text))
check=im.copy()
for e in edits:check.paste(original.crop(e['box']),e['box'][:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,original).split())
target=out/'noffice.spr3.00.png';im.save(target)
sheet=Image.new('RGBA',im.size,'#666666');sheet.alpha_composite(im)
sheet.resize((1024,512),Image.Resampling.NEAREST).save(out/'noffice_full_preview.png')
(out/'review.json').write_text(json.dumps(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),status='pending_user_visual_review',edits=edits,outside_boxes_rgba_unchanged=True,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
