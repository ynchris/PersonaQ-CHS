"""Pink quest tutorial preview, script-authored text only, no encoding."""
import json
from PIL import Image,ImageDraw,ImageFont,ImageChops
import preview_tutorials_468 as render
from preview_tutorials_468 import ROOT,label,digest

out=ROOT/'translation/previews_485';out.mkdir(exist_ok=True)
original=Image.open(ROOT/'export_base/tutorial/t022.ctpk.00.png').convert('RGBA')
im=original.copy();boxes=[]
render.FONT='C:/Windows/Fonts/msyhbd.ttc'
def put(b,text,size,color,bg):
    label(im,b,text,color,bg,size=size);boxes.append(b)
put((173,16,274,27),'要接受哪个委托？',8,'#895c7c',original.getpixel((165,20)))
put((57,37,225,50),'帮忙参加以物易物对决',9,'#875a78',original.getpixel((210,43)))
put((57,51,141,65),'创造獬豸',9,'#9d6686',original.getpixel((151,57)))
put((126,119,179,131),'校内漫步',9,'#504d00',original.getpixel((178,123)))
put((114,132,262,144),'想和小熊进行以物易物对决，',9,'#55434d',original.getpixel((265,135)))
put((114,144,262,155),'让玲吃到美味的食物。',9,'#55434d',original.getpixel((265,146)))
put((114,155,134,166),'报酬',9,'#973764',original.getpixel((216,160)))
put((147,155,200,166),'初级成长',9,'#55434d',original.getpixel((210,160)))
# The lower-left tutorial menu is clipped by the screenshot edge.
# Work on its text area only; preserve all colored polygons outside it.
b=(9,128,83,175);boxes.append(b)
region=Image.new('L',im.size,0);d=ImageDraw.Draw(region)
d.polygon([(18,128),(82,174),(9,174),(9,146)],fill=255)
for y in range(128,175):
    for x in range(9,83):
        if not region.getpixel((x,y)):continue
        r,g,bl,a=original.getpixel((x,y))
        # Preserve violet decorative panel and the magenta stripe by position.
        line_y=130+(x-18)*.74
        if abs(y-line_y)<6:
            im.putpixel((x,y),(143,59,108,255))
        elif y>line_y+6:
            im.putpixel((x,y),(147,139,145,255))
def angled(text,xy,color):
    tile=Image.new('RGBA',(100*4,14*4))
    ImageDraw.Draw(tile).text((0,-4),text,font=ImageFont.truetype(render.FONT,9*4),fill=color)
    tile=tile.rotate(-37,Image.Resampling.BICUBIC,expand=True)
    tile=tile.resize((tile.width//4,tile.height//4),Image.Resampling.LANCZOS)
    layer=Image.new('RGBA',im.size);layer.alpha_composite(tile,xy)
    alpha=layer.getchannel('A')
    # Limit translated slanted text to the same clipped screenshot panel.
    import PIL.ImageChops
    alpha=PIL.ImageChops.multiply(alpha,region)
    layer.putalpha(alpha);im.alpha_composite(layer)
angled('接受委托',(21,130),'#b4a0ae')
angled('选择要接受的委托',(14,146),'#3f3540')
check=im.copy()
for b in boxes:check.paste(original.crop(b),b[:2])
assert ImageChops.difference(check,original).convert('RGB').getbbox() is None
target=out/'t022.ctpk.00.png';im.save(target)
pair=Image.new('RGBA',(592,184),'black');pair.paste(original.crop((0,0,296,184)),(0,0));pair.paste(im.crop((0,0,296,184)),(296,0))
pair.resize((1184,368),Image.Resampling.NEAREST).save(out/'t022_compare.png')
(out/'review.json').write_text(json.dumps(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),status='pending_user_review',encoded=False,packaged=False,outside_edit_boxes_unchanged=True),ensure_ascii=False,indent=2),encoding='utf-8')
