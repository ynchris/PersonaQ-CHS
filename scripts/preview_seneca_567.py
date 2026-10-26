"""Precise, preview-only localization of the located Seneca texture."""
import hashlib,json,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parent
expanded='--original-spacing' in sys.argv
heavier='--heavier' in sys.argv or expanded
OUT=ROOT/('translation/previews_570' if expanded else 'translation/previews_568' if heavier else 'translation/previews_567');OUT.mkdir(exist_ok=True)
src=ROOT/'export_base/event/model/e020_001.pac_e020_001.bam_model.04.png'
original=Image.open(src).convert('RGBA')
assert original.size==(512,256)
after=original.copy()
# Clear the whole Japanese text region to transparent, including antialiasing.
box=(0,0,512,180)
after.paste((0,0,0,0),box)
scale=4
stroke=2 if heavier else 0
pad=4 if heavier else 0
font_size=30 if expanded else 28
font=ImageFont.truetype('C:/Windows/Fonts/simsun.ttc',font_size*scale)
rows=[('命运',(5,39)),('引导有志者',(35,84)),('拖拽无志者前行',(94,129))]
metrics=[]
for row_index,(text,(x,y)) in enumerate(rows):
    bb=font.getbbox(text)
    layer=Image.new('RGBA',(512*scale,(70+pad*2)*scale))
    draw=ImageDraw.Draw(layer)
    for i,char in enumerate(text):
        # Original uses ~33 1/3 px character pitch on rows 1/3, 30 px on row 2.
        # Preserve pitch rather than stretching the shorter Chinese sentences.
        pitch=[100/3,30,100/3][row_index] if expanded else None
        advance=i*pitch*scale if expanded else draw.textlength(text[:i],font=font)
        color=(255,0,0,255) if char=='命' else (255,255,255,255)
        draw.text((x*scale+advance-bb[0],pad*scale-bb[1]),char,font=font,
                  fill=color,stroke_width=stroke,stroke_fill=color)
    layer=layer.resize((512,70+pad*2),Image.Resampling.LANCZOS)
    after.alpha_composite(layer,(0,y-pad))
    metrics.append(dict(text=text,position=[x,y],font_size=font_size,character_pitch=pitch,ink_bbox=layer.getchannel('A').getbbox()))
assert after.crop((0,180,512,256)).tobytes()==original.crop((0,180,512,256)).tobytes()
dst=OUT/'seneca.png';after.save(dst)
pair=Image.new('RGBA',(1040,256),(0,0,0,255))
pair.alpha_composite(original,(0,0));pair.alpha_composite(after,(528,0))
pair.convert('RGB').save(OUT/'compare.png')
if heavier:
    previous=Image.open(ROOT/('translation/previews_568/seneca.png' if expanded else 'translation/previews_567/seneca.png')).convert('RGBA')
    pair=Image.new('RGBA',(1040,256),(0,0,0,255))
    pair.alpha_composite(previous,(0,0));pair.alpha_composite(after,(528,0))
    pair.convert('RGB').save(OUT/'weight_compare.png')
review=dict(status='pending_user_visual_review',source=src.relative_to(ROOT).as_posix(),
            source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
            output=dst.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),
            size=list(after.size),font='simsun.ttc',rows=metrics,stroke_width_native_pixels=stroke/scale,
            signature_pixels_unchanged=True,original_resources_modified=False,encoded=False,packaged=False)
(OUT/'review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
if expanded:
    prior=ROOT/'translation/previews_568/review.json'
    old=json.loads(prior.read_text(encoding='utf-8'))
    old.update(status='superseded_do_not_encode',superseded_by='translation/previews_570/seneca.png',
               revision_reason='用户要求增大中文字面并保持日文原字距；570需重新审核。')
    prior.write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(review,ensure_ascii=False,indent=2))
