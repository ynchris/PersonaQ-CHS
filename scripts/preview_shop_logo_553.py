"""Script-painted workshop logo candidate, original sprite bounds retained."""
import hashlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from compile_translation import ROOT, write

OUT=ROOT/'translation/previews_553';OUT.mkdir(exist_ok=True)
original=Image.open(ROOT/'translation/feedback_543/secondary_decoded/14.ctpk.00.png').convert('RGBA')
base=Image.open(ROOT/'translation/previews_545/14.ctpk.00.png').convert('RGBA')
after=base.copy()
box=(1,1,170,149)
# Tight polygons around the two lettering runs. Decorative strawberry and
# top bow / small pastry are kept outside these masks.
polys=[[(10,56),(48,45),(57,42),(69,40),(77,45),(88,40),(92,33),(108,28),(114,32),(118,25),(132,20),(143,20),(150,27),(155,53),(151,64),(140,70),(126,68),(121,63),(119,72),(103,73),(88,68),(80,68),(78,73),(62,81),(53,81),(49,86),(33,92),(19,87),(12,76)],
       [(27,98),(43,90),(56,89),(62,98),(71,94),(83,90),(94,83),(94,79),(109,74),(120,76),(130,80),(143,73),(154,72),(164,78),(164,85),(159,93),(141,97),(129,96),(130,101),(123,106),(114,108),(108,112),(99,114),(94,105),(84,107),(77,109),(65,110),(66,117),(61,124),(49,130),(37,128),(30,121),(28,111)]]
mask=Image.new('L',original.size);d=ImageDraw.Draw(mask)
for p in polys:d.polygon(p,fill=255)
doily=Image.new('L',original.size)
ImageDraw.Draw(doily).polygon([(4,63),(8,48),(18,36),(34,32),(45,28),(56,31),(64,39),(81,29),(86,18),(98,13),(108,4),(119,4),(128,12),(138,13),(147,17),(151,26),(158,36),(163,46),(164,59),(155,72),(151,87),(145,100),(137,112),(123,129),(112,139),(99,141),(84,134),(78,125),(62,126),(54,123),(40,118),(27,110),(19,98),(12,89),(7,75)],fill=255)
protect=Image.new('L',original.size);pd=ImageDraw.Draw(protect)
pd.polygon([(68,35),(73,25),(80,29),(85,32),(94,40),(90,48),(75,49),(68,44)],fill=255)
pd.polygon([(118,66),(123,61),(132,61),(137,65),(141,72),(137,77),(130,81),(120,77),(116,73)],fill=255)
pd.polygon([(112,119),(124,109),(139,101),(149,104),(156,107),(153,116),(155,125),(149,133),(138,142),(124,145),(117,139)],fill=255)
mask=mask.filter(ImageFilter.MaxFilter(17))
for y in range(149):
    for x in range(170):
        if not mask.getpixel((x,y)) or protect.getpixel((x,y)):continue
        rr,gg,bb,aa=original.getpixel((x,y))
        # Leave the original white/aqua lace untouched; erase colored lettering
        # and its brown/gray shadow, including pixels beyond the paper edge.
        lace=(gg>rr+10 and bb>rr+10 and abs(gg-bb)<16 and gg>140 and bb>140) or (min(rr,gg,bb)>245)
        if not lace:after.putpixel((x,y),(255,255,255,255))
interior=Image.new('L',original.size)
ImageDraw.Draw(interior).polygon([(20,62),(48,46),(73,52),(91,35),(143,29),(152,67),(141,91),(123,124),(82,125),(38,114),(19,92)],fill=255)
for y in range(149):
    for x in range(170):
        if interior.getpixel((x,y)) and not protect.getpixel((x,y)):
            after.putpixel((x,y),(255,255,255,255))
S=4
font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',37*S)
for text,cx,cy,color in [('手',43,63,'#a4dbbd'),('工',113,38,'#fbdba1'),('工',52,105,'#ff8b83'),('坊',111,98,'#cede8c')]:
    tile=Image.new('RGBA',(70*S,70*S));dt=ImageDraw.Draw(tile)
    bb=dt.textbbox((0,0),text,font=font)
    x=(70*S-bb[2]+bb[0])/2-bb[0];y=(70*S-bb[3]+bb[1])/2-bb[1]
    # Crisp nested biscuit edge and icing, not a blurred drop shadow.
    dt.text((x+S,y+2*S),text,font=font,fill='#b98c47',stroke_width=4*S,stroke_fill='#a5783c')
    dt.text((x,y),text,font=font,fill='#efd39b',stroke_width=3*S,stroke_fill='#e9c77e')
    dt.text((x,y),text,font=font,fill=color,stroke_width=S,stroke_fill='#c8ab69')
    tile=tile.rotate(15,resample=Image.Resampling.BICUBIC).resize((70,70),Image.Resampling.LANCZOS)
    after.alpha_composite(tile,(cx-35,cy-35))
# Bound changes to this sprite and explicitly retain all other atlas entries.
after.putalpha(original.getchannel('A'))
result=base.copy();result.paste(after.crop(box),box[:2])
check=result.copy();check.paste(base.crop(box),box[:2])
assert check.tobytes()==base.tobytes()
result.save(OUT/'shop_texture_1.png')
pair=Image.new('RGBA',(350,150),'#444444');pair.alpha_composite(original.crop(box),(2,1));pair.alpha_composite(result.crop(box),(179,1))
pair.resize((1050,450),Image.Resampling.NEAREST).save(OUT/'logo_compare.png')
full=Image.new('RGBA',(520,256),'#444444');full.alpha_composite(original);full.alpha_composite(result,(264,0));full.resize((1040,512),Image.Resampling.NEAREST).save(OUT/'full_compare.png')
write(OUT/'review.json',dict(status='pending_user_visual_review',text='手工工坊',png='translation/previews_553/shop_texture_1.png',sha256=hashlib.sha256((OUT/'shop_texture_1.png').read_bytes()).hexdigest(),sprite_box=box,outside_sprite_unchanged=True,encoded=False,packaged=False))
