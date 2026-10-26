"""Review-only: current mixed glyphs vs 586 unified CJK glyphs, laid out with real widths."""
import json,sys
from PIL import Image,ImageDraw
from font_unify_586 import ROOT,FONTS,read,is_cjk,original_target,render_cell
OUT=ROOT/'translation/previews_586';OUT.mkdir(exist_ok=True)
LINES=['不可思议之国的你 第１章','要读取哪个存档？','伊丽莎白：欢迎来到天鹅绒房间。','攻击力上升了！ＨＰ１２０']
JP=['不思議の国のキミ 第１章','どのデータをロードしますか？']
ONLY=sys.argv[2].split(',') if len(sys.argv)>2 else None
S=int(sys.argv[3]) if len(sys.argv)>3 else 3
mapping=read(ROOT/'translation/font_encoding.hex.json')
weight=float(sys.argv[1]) if len(sys.argv)>1 else 0
def load(name):
    d=ROOT/f'full_work/font_aligned_544/verify/{name}';m=read(d/f'{name}_manifest.json')
    return d,m
def glyph_lookup(name,d,m,cache):
    tx=m['textureInfo'];si=tx['sheetInfo'];cw=tx['glyph']['width']+1;ch=tx['glyph']['height']+1;per=si['cols']*si['rows']
    def get(c):
        enc=mapping.get(c) or c.encode('cp932').hex().upper()
        code=chr(int(enc,16));idx=m['glyphMap'][code];s,slot=divmod(idx,per)
        if s not in cache:cache[s]=Image.open(d/f'{name}_sheet{s}.png').convert('RGBA')
        x=slot%si['cols']*cw+1;y=slot//si['cols']*ch+2
        w=m['glyphWidths'].get(str(idx));dw=m['fontInfo']['defaultWidth']
        w=w or dict(char=dw['charWidth'],glyph=dw['glyphWidth'],left=dw['left'])
        return cache[s].crop((x,y,x+cw,y+ch)),w
    return get,(cw,ch)
def line(get,text,cell,new=None):
    width=sum(get(c)[1]['char'] for c in text)+4
    im=Image.new('RGBA',(width,cell[1]+4),(40,40,48,255));x=2
    for c in text:
        g,w=get(c)
        if new and is_cjk(c):g=new(c)
        im.alpha_composite(g,(x+w['left'],2));x+=w['char']
    return im
rows=[]
for name in (ONLY or FONTS):
    d,m=load(name);get,cell=glyph_lookup(name,d,m,{});target,_=original_target(name)
    new=lambda c:render_cell(c,target,cell,weight)[0]
    for t in JP:rows.append((name+' JP',line(get,t,cell),Image.new('RGBA',(1,1))))
    for t in LINES[:2] if name!='humming_d_14' else LINES:
        rows.append((name,line(get,t,cell),line(get,t,cell,new)))
W=max(a.width+b.width for _,a,b in rows)*S+260;H=sum(max(a.height,b.height)*S+10 for _,a,b in rows)+30
sheet=Image.new('RGB',(W,H),(24,24,28));dr=ImageDraw.Draw(sheet);y=30
dr.text((10,8),'font',fill='white');dr.text((150,8),'current (544)',fill='white');dr.text((150+W//2-130,8),'586 unified',fill='white')
colw=max(a.width for _,a,_ in rows)*S+20
for name,a,b in rows:
    dr.text((10,y+8),name,fill=(200,200,200))
    sheet.paste(a.resize((a.width*S,a.height*S),Image.Resampling.NEAREST),(150,y))
    sheet.paste(b.resize((b.width*S,b.height*S),Image.Resampling.NEAREST),(150+colw,y))
    y+=a.height*S+10
p=OUT/(f'compare_w{weight}'+('_'+'_'.join(ONLY) if ONLY else '')+'.png');sheet.save(p);print(p)
