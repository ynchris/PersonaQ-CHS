"""Review-only: redraw party help labels in two candidate styles.
A: white fill + dark outline (user request). B: thin dark-gray strokes + thick white outline (matches original pixels).
Keeps 584's extra spacing for 卸下 and clears whole sprite rects (removes the stray dot above 状态)."""
import json
from PIL import Image,ImageChops,ImageDraw,ImageFont
from preview_tutorials_468 import ROOT,digest
import sys
STYLE=sys.argv[1] if len(sys.argv)>1 else 'A'
SIZE=float(sys.argv[2]) if len(sys.argv)>2 else None  # optional uniform size override (original kanji strokes are ~10px)
out=ROOT/('translation/previews_585/'+STYLE+(f'_{SIZE:g}' if SIZE else ''));out.mkdir(parents=True,exist_ok=True)
original=Image.open(ROOT/'export_base/facility/party.spr3.00.png').convert('RGBA')
base=Image.open(ROOT/'translation/previews_584/party.spr3.00.png').convert('RGBA');im=base.copy()
# original: strokes ~(59,59,59), outline white ~2px
FONT,FILL,EDGE,STROKE={'A':('C:/Windows/Fonts/msyhbd.ttc',(255,255,255,255),(58,58,58,255),1),
                       'B':('C:/Windows/Fonts/msyh.ttc',(59,59,59,255),(255,255,255,255),2),
                       # C/D: darker strokes; antialiasing lightens thin strokes, so pure black lands near the original's mean ~80
                       'C':('C:/Windows/Fonts/msyh.ttc',(0,0,0,255),(255,255,255,255),2),
                       'D':('C:/Windows/Fonts/msyh.ttc',(0,0,0,255),(255,255,255,255),2)}[STYLE]
S=1 if STYLE=='D' else 4  # D: native-size rendering (crisper, no supersampling)
# party.spr3 sprite rects (操作ヘルプ 49-52); left = ink start column inside rect, sizes as approved in 488
specs=[(49,(469,86,500,104),'卸下',12,3),(50,(441,105,497,123),'状态',11,2),
       (51,(441,124,498,142),'切换语音',11,2),(52,(441,143,470,161),'删除',11,2)]
edits=[]
for idx,box,text,size,left in specs:
    size=SIZE or size
    w,h=box[2]-box[0],box[3]-box[1]
    big=Image.new('RGBA',(w*S*2,h*S*2));d=ImageDraw.Draw(big);f=ImageFont.truetype(FONT,round(size*S))
    d.text((S*4,S*4),text,font=f,fill=FILL,stroke_width=S*STROKE,stroke_fill=EDGE)
    small=big.resize((w*2,h*2),Image.Resampling.LANCZOS) if S>1 else big;small=small.crop(small.getchannel('A').point(lambda v:255 if v>8 else 0).getbbox())
    o=original.crop(box).getchannel('A').getbbox();top=round((o[1]+o[3])/2-small.height/2)
    assert left+small.width<=w and 0<=top and top+small.height<=h,(text,small.size,box)
    cell=Image.new('RGBA',(w,h));cell.alpha_composite(small,(left,top));im.paste(cell,box[:2])
    edits.append(dict(sprite=idx,box=box,text=text,size=size,ink=[left,top,left+small.width,top+small.height]))
check=im.copy()
for _,box,*_ in specs:check.paste(base.crop(box),box[:2])
assert not any(c.getbbox() for c in ImageChops.difference(check,base).split())
target=out/'party.spr3.00.png';im.save(target)
crop=(438,84,502,162);sheet=Image.new('RGBA',(3*68,80),'#303030')
for i,img in enumerate((original,base,im)):sheet.alpha_composite(img.crop(crop),(i*68+2,1))
sheet.resize((sheet.width*5,sheet.height*5),Image.Resampling.NEAREST).save(out/'compare.png')
(out/'review.json').write_text(json.dumps(dict(status='pending_user_visual_review',png=target.relative_to(ROOT).as_posix(),sha256=digest(target),
    base_png='translation/previews_584/party.spr3.00.png',style=STYLE,font=FONT,fill=FILL[:3],outline=EDGE[:3],outline_px=STROKE,edits=edits,uv_update_required=False,
    outside_sprite_rects_unchanged=True,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(edits,ensure_ascii=False))
