"""Revise two ordinary labels only, keeping other atlas pixels identical."""
import hashlib
from PIL import Image,ImageDraw,ImageFont
from compile_translation import ROOT,read,write
out=ROOT/'translation/previews_556';out.mkdir(exist_ok=True)
original=Image.open(ROOT/'translation/feedback_543/secondary_decoded/17.ctpk.00.png').convert('RGBA')
base=Image.open(ROOT/'translation/previews_545/17.ctpk.00.png').convert('RGBA');im=base.copy()
records={r['index']:r for r in read(ROOT/'translation/previews_545/velvet_records.json')}
edits=[]
for idx,text in [(212,'更换人格面具'),(213,'分享人格面具')]:
    box=records[idx]['box'];l,t,r,b=box;w,h=r-l,b-t
    patch=Image.new('RGBA',(w*4,h*4));d=ImageDraw.Draw(patch);font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',44)
    bb=d.textbbox((0,0),text,font=font)
    assert bb[2]-bb[0]<=w*4 and bb[3]-bb[1]<=h*4
    d.text(((w*4-bb[2]+bb[0])/2-bb[0],(h*4-bb[3]+bb[1])/2-bb[1]),text,font=font,fill='white')
    im.paste(patch.resize((w,h),Image.Resampling.LANCZOS),box[:2]);edits.append(dict(index=idx,text=text,box=box,font_size=11))
check=im.copy()
for e in edits:check.paste(base.crop(e['box']),e['box'][:2])
assert check.tobytes()==base.tobytes()
target=out/'velvet_texture_2.png';im.save(target)
pair=Image.new('RGBA',(520,128),'#444444');pair.alpha_composite(original);pair.alpha_composite(im,(264,0));pair.resize((1040,256),Image.Resampling.NEAREST).save(out/'full_compare.png')
detail=Image.new('RGBA',(230,50),'#444444')
for row,e in enumerate(edits):
    detail.alpha_composite(original.crop(e['box']),(3,row*25+4));detail.alpha_composite(im.crop(e['box']),(120,row*25+4))
detail.resize((920,200),Image.Resampling.NEAREST).save(out/'labels_compare.png')
write(out/'review.json',dict(status='pending_user_visual_review',png=target.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),edits=edits,outside_boxes_unchanged=True,encoded=False,packaged=False))
