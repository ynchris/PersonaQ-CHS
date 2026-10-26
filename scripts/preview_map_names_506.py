import json
from PIL import Image,ImageDraw,ImageFont,ImageChops
from preview_tutorials_468 import ROOT,digest
out=ROOT/'translation/previews_506';out.mkdir(exist_ok=True)
previous=Image.open(ROOT/'translation/previews_504/map_plt_icon.ctpk.00.png').convert('RGBA')
im=previous.copy()
lines=[['不可思议','之国的你'],['联谊','咖啡厅'],['放学后','恶灵俱乐部'],['稻羽','乡土展'],['时钟塔']]
specs=[]
for i,y in enumerate([3,38,73,108,143]):
    specs.extend([(i,(259,y,319,y+30),False),(i,(324,y,384,y+30),True)])
specs.extend([(0,(147,383,207,413),False),(3,(210,383,270,413),False),
 (1,(147,418,207,448),False),(4,(210,418,270,448),False),(2,(147,452,207,482),False),
 (0,(59,447,119,477),True),(1,(263,479,323,509),True),(2,(326,479,386,509),True),
 (3,(389,479,449,509),True),(4,(452,479,512,509),True)])
edits=[]
for index,outer,blue in specs:
    l,t,r,bottom=outer;box=(l+2,t+3,r-2,bottom-3)
    x0,y0,x1,y1=box
    for y in range(y0,y1):
        color=previous.getpixel((330 if blue else 265,143+y-t))
        for x in range(x0,x1):im.putpixel((x,y),color)
    patch=Image.new('RGBA',((x1-x0)*4,(y1-y0)*4))
    d=ImageDraw.Draw(patch);font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',(10 if index==2 else 11)*4)
    textlines=lines[index];step=12*4
    for row,text in enumerate(textlines):
        b=d.textbbox((0,0),text,font=font);h=b[3]-b[1]
        assert b[2]-b[0]<=patch.width
        top=(patch.height-((len(textlines)-1)*step+h))/2+row*step
        d.text(((patch.width-b[2]+b[0])/2-b[0],top-b[1]),text,font=font,fill='white' if blue else '#888888')
    im.alpha_composite(patch.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS),box[:2])
    edits.append(dict(name=''.join(textlines),box=box))
check=im.copy()
for e in edits:check.paste(previous.crop(e['box']),e['box'][:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,previous).split())
target=out/'map_plt_icon.ctpk.00.png';im.save(target)
original=Image.open(ROOT/'export_base/mapdat/tex/map_plt_icon.ctpk.00.png').convert('RGBA')
pair=Image.new('RGBA',(1032,512),'#cccccc');pair.alpha_composite(original,(0,0));pair.alpha_composite(im,(520,0));pair.save(out/'map_names_full_compare.png')
detail=Image.new('RGBA',(260,175),'#cccccc')
for i,y in enumerate([3,38,73,108,143]):
    for j,source in enumerate([original,im]):detail.alpha_composite(source.crop((259,y,384,y+30)),(j*130,i*35))
detail.resize((780,525),Image.Resampling.NEAREST).save(out/'map_names_compare.png')
(out/'review.json').write_text(json.dumps(dict(status='pending_user_visual_review',png=target.relative_to(ROOT).as_posix(),sha256=digest(target),edits=edits,outside_boxes_rgba_unchanged=True,decorative_logos_unchanged=True,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
