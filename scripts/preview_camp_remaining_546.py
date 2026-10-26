"""Complete remaining monochrome camp labels; leave colored icons separate."""
import hashlib
from collections import Counter
from PIL import Image,ImageDraw,ImageFont,ImageChops
from compile_translation import ROOT,read,write
OUT=ROOT/'translation/previews_546';OUT.mkdir(exist_ok=True)
records={r['index']:r for r in read(ROOT/'translation/feedback_541/camp_sprite_records.json')}
specs=[(records[i]['box'],s,sz,mode) for i,s,sz,mode in [
 (485,'选择人格面具',11,'outline'),(486,'选择技能',12,'outline'),
 (586,'切换副人格面具',11,'outline'),(588,'替换技能',12,'outline'),
 (603,'简要',12,'outline'),(604,'详细',12,'plate'),
 (525,'受理中',12,'borderwhite'),(526,'可报告',12,'borderwhite')]]
specs += [((179,163,207,182),'完成',12,'cyanplate'),((224,163,268,182),'已过期',12,'cyanblack'),
          ((69,106,125,124),'无法分析',13,'white'),((429,1,478,17),'攻击力',14,'italic'),((429,17,478,33),'防御力',14,'italic'),
          ((65,59,83,77),'运',15,'white'),((151,214,186,234),'主',13,'outline'),((201,214,227,234),'副',13,'outline')]
assets=[]
for unit,basepath,originalpath,edits in [
 ('camp',ROOT/'translation/previews_542/c_main.second.ctpk.00.png',ROOT/'translation/feedback_543/secondary_decoded/00.ctpk.00.png',specs),
 ('pink',ROOT/'translation/feedback_543/secondary_decoded/13.ctpk.00.png',ROOT/'translation/feedback_543/secondary_decoded/13.ctpk.00.png',
 [((x,y,x+17,y+17),s,14,'pink') for x,y,s in [(90,0,'斩'),(124,0,'坏'),(158,0,'冰'),(175,0,'风'),(124,17,'暗'),(175,17,'无'),(210,34,'运')]])]:
    original=Image.open(originalpath).convert('RGBA');base=Image.open(basepath).convert('RGBA');im=base.copy()
    for box,text,size,mode in edits:
        l,t,r,b=box;w,h=r-l,b-t
        patch=Image.new('RGBA',(w*4,h*4));d=ImageDraw.Draw(patch)
        font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc' if mode=='pink' else 'C:/Windows/Fonts/msyhbd.ttc',size*4)
        stroke=4 if mode=='outline' else 0;bb=d.textbbox((0,0),text,font=font,stroke_width=stroke)
        assert bb[2]-bb[0]<=w*4 and bb[3]-bb[1]<=h*4,(text,box,bb)
        color='#333333' if mode in ('plate','outline') else '#00cfe5' if mode.startswith('cyan') else '#ff7e7c' if mode=='pink' else 'white'
        d.text(((w*4-bb[2]+bb[0])/2-bb[0],(h*4-bb[3]+bb[1])/2-bb[1]),text,font=font,fill=color,stroke_width=stroke,stroke_fill='white')
        if mode=='italic':patch=patch.transform(patch.size,Image.Transform.AFFINE,(1,0.2,-h*0.4,0,1,0),resample=Image.Resampling.BICUBIC)
        patch=patch.resize((w,h),Image.Resampling.LANCZOS)
        if mode=='borderwhite':
            frame=original.crop(box);fb=frame.getchannel('A').getbbox()
            frame.paste((0,0,0,0),(fb[0]+2,fb[1]+2,fb[2]-2,fb[3]-2));frame.alpha_composite(patch);patch=frame
        if mode in ('plate','cyanplate','cyanblack'):
            plate=Image.new('RGBA',(w,h),'black' if mode=='cyanblack' else 'white');plate.putalpha(original.crop(box).getchannel('A'));plate.alpha_composite(patch);patch=plate
        im.paste(patch,(l,t))
    check=im.copy()
    for box,*_ in edits:check.paste(base.crop(box),box[:2])
    assert not any(c.getbbox() for c in ImageChops.difference(check,base).split())
    target=OUT/f'{unit}.ctpk.00.png';im.save(target)
    pair=Image.new('RGBA',(im.width*2+8,im.height),'#444444');pair.alpha_composite(original);pair.alpha_composite(im,(im.width+8,0));pair.save(OUT/f'{unit}_full_compare.png')
    detail=Image.new('RGBA',(240,len(edits)*26),'#444444')
    for row,(box,*_) in enumerate(edits):
        for col,src in enumerate([original,im]):detail.alpha_composite(src.crop(box),(col*120+4,row*26+3))
    detail.resize((720,detail.height*3),Image.Resampling.NEAREST).save(OUT/f'{unit}_labels_compare.png')
    if unit=='camp':
        strip=Image.new('RGBA',(180,30),'#444444')
        strip.alpha_composite(original.crop((151,214,227,234)),(3,5));strip.alpha_composite(im.crop((151,214,227,234)),(95,5))
        strip.resize((720,120),Image.Resampling.NEAREST).save(OUT/'main_sub_compare.png')
    assets.append(dict(unit=unit,png=target.relative_to(ROOT).as_posix(),base=basepath.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),edits=edits,outside_boxes_rgba_unchanged=True))
write(OUT/'review.json',dict(status='pending_user_visual_review',assets=assets,encoded=False,packaged=False))
