from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;O=R/'translation/previews_575';O.mkdir(exist_ok=True)
original=Image.open(R/'translation/feedback_541/decoded/camp_c_main.spr3.tex1.ctpk.00.png').convert('RGBA')
before=Image.open(R/'translation/previews_573/camp_texture_1.png').convert('RGBA');after=before.copy()
box=(120,144,203,162);patch=Image.new('RGBA',(83,18))
arrow=(163,144,178,162)
patch.paste(original.crop(arrow),(43,0))
font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',44)
for text,x,w in [('出战',0,39),('候补',58,25)]:
    hi=Image.new('RGBA',(w*4,72));d=ImageDraw.Draw(hi);bb=d.textbbox((0,0),text,font=font,stroke_width=4)
    d.text(((w*4-bb[2]+bb[0])/2-bb[0],(72-bb[3]+bb[1])/2-bb[1]),text,font=font,fill='#333333',stroke_width=4,stroke_fill='white')
    patch.alpha_composite(hi.resize((w,18),Image.Resampling.LANCZOS),(x,0))
after.paste(patch,box[:2]);after.save(O/'camp_texture_1.png')
pair=Image.new('RGBA',(180,28),'#444444')
pair.alpha_composite(original.crop(box),(2,4));pair.alpha_composite(patch,(94,4))
pair.resize((1080,168),Image.Resampling.NEAREST).save(O/'compare.png')
(O/'review.json').write_text(json.dumps(dict(status='pending_user_visual_review',box=box,arrow_box=arrow,png='translation/previews_575/camp_texture_1.png',includes_pending_cursor_573=True,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
