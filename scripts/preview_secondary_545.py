"""PNG-only secondary-atlas menu translations; original left, revision right."""
import hashlib
from PIL import Image,ImageDraw,ImageFont,ImageChops
from compile_translation import ROOT,read,write
OUT=ROOT/'translation/previews_545';OUT.mkdir(exist_ok=True)
def box(name,index):return next(r['box'] for r in read(OUT/f'{name}_records.json') if r['index']==index)
assets=[]
shop=[(box('shop',i),text,14,'white') for i,text in [(2,'购买'),(3,'出售物品'),(4,'整理物品'),(5,'听取说明'),(6,'离开房间'),(7,'道具'),(10,'饰品'),(111,'寄存'),(112,'取出')]]
shop += [(box('shop',118),'菜单',13,'outline'),(box('shop',124),'处',11,'pink')]
velvet=[(box('velvet',i),text,11,'white') for i,text in [(208,'说明'),(209,'状态'),(210,'已登记数据'),(211,'当前状态'),(212,'变更人格面具'),(213,'分发人格面具')]]
item=[((24,18,123,35),'切换分类',12,'plate'),((17,36,95,53),'道具info',12,'plate'),(box('partyinfo',55),'使用',13,'white'),(box('partyinfo',56),'丢弃',13,'white')]
control=[((18,1,52,17),'确定',12,'plate'),((71,1,106,17),'返回',12,'plate'),((18,18,114,34),'关闭HELP',12,'plate'),((18,35,96,51),'打开HELP',12,'plate'),((18,52,85,68),'出战',12,'plate'),((18,69,52,85),'候补',12,'plate')]
for unit,specs in [('14',shop),('17',velvet),('05',item),('10',control)]:
    src=ROOT/f'translation/feedback_543/secondary_decoded/{unit}.ctpk.00.png'
    original=Image.open(src).convert('RGBA');im=original.copy()
    for b,text,size,mode in specs:
        l,t,r,bottom=b;w,h=r-l,bottom-t
        patch=Image.new('RGBA',(w*4,h*4));d=ImageDraw.Draw(patch);font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',size*4)
        stroke=4 if mode=='outline' else 0;bb=d.textbbox((0,0),text,font=font,stroke_width=stroke)
        assert bb[2]-bb[0]<=w*4 and bb[3]-bb[1]<=h*4,(unit,text,b,bb)
        color='#444444' if mode in ('plate','outline') else '#ffc8bf' if mode=='pink' else 'white'
        d.text(((w*4-bb[2]+bb[0])/2-bb[0],(h*4-bb[3]+bb[1])/2-bb[1]),text,font=font,fill=color,stroke_width=stroke,stroke_fill='white')
        patch=patch.resize((w,h),Image.Resampling.LANCZOS)
        if mode=='plate':
            plate=Image.new('RGBA',(w,h),'white');plate.putalpha(original.crop(b).getchannel('A'));plate.alpha_composite(patch);patch=plate
        im.paste(patch,(l,t))
    check=im.copy()
    for b,*_ in specs:check.paste(original.crop(b),b[:2])
    assert not any(c.getbbox() for c in ImageChops.difference(check,original).split())
    target=OUT/f'{unit}.ctpk.00.png';im.save(target)
    pair=Image.new('RGBA',(im.width*2+8,im.height),'#444444');pair.alpha_composite(original);pair.alpha_composite(im,(im.width+8,0))
    pair.resize((pair.width*2,pair.height*2),Image.Resampling.NEAREST).save(OUT/f'{unit}_full_compare.png')
    details=Image.new('RGBA',(270,len(specs)*25),'#444444')
    for row,(b,*_) in enumerate(specs):
        for col,p in enumerate([original,im]):details.alpha_composite(p.crop(b),(col*135+5,row*25+3))
    details.resize((810,details.height*3),Image.Resampling.NEAREST).save(OUT/f'{unit}_labels_compare.png')
    origin=next(r for r in read(ROOT/'translation/feedback_543/secondary_textures.json') if r['unit']==unit+'.ctpk')
    assets.append(dict(**origin,png=target.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),edits=specs,outside_boxes_rgba_unchanged=True))
write(OUT/'review.json',dict(status='pending_user_visual_review',assets=assets,encoded=False,packaged=False,notes='Shop logo unchanged; remaining camp secondary labels and colored icons are separate work.'))
print('Preview labels:',sum(len(a['edits']) for a in assets))
