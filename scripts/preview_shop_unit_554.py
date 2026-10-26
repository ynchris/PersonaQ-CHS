"""Only replace the storage counter, keeping the original decorative logo."""
import hashlib
from PIL import Image,ImageDraw,ImageFont
from compile_translation import ROOT,write
out=ROOT/'translation/previews_554';out.mkdir(exist_ok=True)
base=Image.open(ROOT/'translation/previews_545/14.ctpk.00.png').convert('RGBA')
original=Image.open(ROOT/'translation/feedback_543/secondary_decoded/14.ctpk.00.png').convert('RGBA')
im=base.copy();box=(177,215,203,229);w,h=26,14
patch=Image.new('RGBA',(w*4,h*4));d=ImageDraw.Draw(patch)
f=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',44);bb=d.textbbox((0,0),'格',font=f)
d.text(((w*4-bb[2]+bb[0])/2-bb[0],(h*4-bb[3]+bb[1])/2-bb[1]),'格',font=f,fill='#ffc8bf')
im.paste(patch.resize((w,h),Image.Resampling.LANCZOS),box[:2])
check=im.copy();check.paste(base.crop(box),box[:2]);assert check.tobytes()==base.tobytes()
assert im.crop((1,1,170,149)).tobytes()==original.crop((1,1,170,149)).tobytes()
im.save(out/'shop_texture_1.png')
pair=Image.new('RGBA',(520,256),'#444444');pair.alpha_composite(original);pair.alpha_composite(im,(264,0));pair.resize((1040,512),Image.Resampling.NEAREST).save(out/'full_compare.png')
pair=Image.new('RGBA',(80,22),'#444444');pair.alpha_composite(original.crop(box),(4,4));pair.alpha_composite(im.crop(box),(48,4));pair.resize((400,110),Image.Resampling.NEAREST).save(out/'unit_compare.png')
write(out/'review.json',dict(status='pending_user_visual_review',png='translation/previews_554/shop_texture_1.png',sha256=hashlib.sha256((out/'shop_texture_1.png').read_bytes()).hexdigest(),text='格',box=box,outside_box_unchanged=True,original_logo_unchanged=True,encoded=False,packaged=False))
