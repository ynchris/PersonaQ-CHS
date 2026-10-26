"""587: produce FZ-font versions of every UI label texture + per-texture review sheets.

Generic units come from sprite records (translation/inventory_587/label_texts.json).
Script-replica units reproduce the approved Codex background reconstruction and only
swap the text rendering to the FZ face. Nothing is encoded here.
"""
import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import redraw_labels_587 as RL
from redraw_labels_587 import ROOT,FZ,read,diff_bbox
from label_units_587 import final_textures
OUT=ROOT/'translation/previews_587/final';OUT.mkdir(parents=True,exist_ok=True)
U=read(ROOT/'translation/inventory_587/sprite_units.json')
TEXTS=read(ROOT/'translation/inventory_587/label_texts.json')

def fz_text(text,ink_h,fill,outline=None,ow=0,italic=False,bold=0):
    st=dict(fill=tuple(fill)+(255,) if len(fill)==3 else tuple(fill),outline=(tuple(outline)+(255,)) if outline else None,width=ow)
    im,_=RL.render_text(text,ink_h,st,10**6,italic,bold);return im
def put_center(img,box,glyph,dx=0,dy=0):
    l,t,r,b=box;img.alpha_composite(glyph,(round((l+r-glyph.width)/2)+dx,round((t+b-glyph.height)/2)+dy))

# ---------- script replicas ----------
def skip_btn(cur):
    original=Image.open(ROOT/'export_base/event/skip_btn.spr3.00.png').convert('RGBA');im=cur.copy()
    specs=[((35,63,94,78),'对话回顾',33),((109,63,181,77),'快速跳过',107),((199,63,254,78),'A键',196),
       ((340,20,414,33),'快速跳过',338),((425,20,496,33),'快速跳过',423),((36,151,93,166),'全部跳过',33),
       ((123,144,183,160),'全部跳过',122),((193,144,255,160),'对话回顾',193),((265,144,340,160),'快速跳过',264),
       ((350,144,410,160),'A键',350),((123,219,183,234),'全部跳过',122),((193,219,255,234),'对话回顾',193),
       ((265,219,340,234),'快速跳过',264),((350,219,410,234),'A键',350)]
    hide=[((107,25,182,40),(145,24),106),((265,106,340,121),(302,105),264),((265,181,340,196),(302,180),264)]
    from inpaint_587 import relative_text_mask,rebuild_overlay,LUM
    import numpy as np
    A=np.asarray(original).astype(float)
    def shape_mask(box,sx):
        x0,y0,x1,y1=box;return (LUM(A[y0:y1,x0:x1])-LUM(A[y0:y1,sx])[:,None])>10
    # reference geometry (x relative to text box x0, y relative to text box y0), measured on the bright buttons
    REF={'快速跳过':dict(box=(109,63,181,77),sx=107,polys=[[(24-5,56-63),(35.5-5,60.5-63),(26.6-5,69.3-63)],[(38-5,53-63),(49.5-5,56.5-63),(41.2-5,66-63)]]),
         '隐藏窗口':dict(box=(107,25,182,40),sx=106,polys=[[(x-3,y-25) for x,y in [(24,16),(28,16),(38,22),(36,28),(34,33),(31,37),(26,37),(25,30)]],
                                                            [(x-107,y-25) for x,y in [(146.5,23.5),(152.5,27.5),(144,32.5)]]])}
    def rebuild(box,text,sx):
        ref=REF[text];rb=ref['box'];x0,y0,x1,y1=box
        up=16;rm=shape_mask((rb[0],rb[1]-up,rb[2],rb[1]),ref['sx']);best=None
        for dy in range(-3,4):
            for dx in range(-3,4):
                tb=(x0+dx,y0+dy-up,x0+dx+(rb[2]-rb[0]),y0+dy)
                if tb[1]<0:continue
                tm=shape_mask(tb,sx)
                if tm.shape!=rm.shape:continue
                sc=(tm==rm).mean()
                if best is None or sc>best[0]:best=(sc,dx,dy)
        _,dx,dy=best
        # widen by up to 4px each side (stay inside the opaque button) so the old text glow is fully covered
        yy=(y0+y1)//2;wl=x0;wr=x1
        if y0<40 and x0>=340:  # only the two top-right dark buttons have glow beyond the text box
            while wl>x0-4 and A[yy,wl-1,3]>200 and A[yy,wl-3,3]>200:wl-=1
            while wr<x1+4 and A[yy,wr,3]>200 and A[yy,wr+2,3]>200:wr+=1
        region=(wl,max(0,y0-up),wr,y1)
        m=relative_text_mask(original,region,sx,grow=2);m[:y0-1-region[1]]=False
        polys=[[(px+dx+x0-region[0],py+dy+y0-region[1]) for px,py in P] for P in ref['polys']]
        # glow cleanup starts one row above the real text ink (Codex text boxes start higher than the glyphs)
        strong=relative_text_mask(original,region,sx,grow=0);rows=[i for i in range(strong.shape[0]) if strong[i].any() and i>=y0-region[1]-1]
        gf=max(0,rows[0]-3) if rows else y0-1-region[1]
        m[:gf]=False
        if y0<40 and x0>=340:
            # top-right dark buttons: their background behind the text is lit by the original glow;
            # fill from nearby clean pixels so the brightness matches the surroundings
            m3=m.copy();m3[:,1:]|=m[:,:-1];m3[:,:-1]|=m[:,1:]  # extra 1px only sideways (old glow edge)
            return rebuild_overlay(original,region,m3,polys,radius=3,local_bg=4).crop(region),region
        return rebuild_overlay(original,region,m,polys,radius=3,glow_from=gf,glow_thr=8).crop(region),region
    for box,text,sx in specs:
        x0,y0,x1,y1=box
        if text=='快速跳过':
            # user 587: keep the triangle graphics behind the text (overlay-space rebuild + extended triangle tips)
            patch,region=rebuild(box,text,sx);im.paste(patch,region[:2])
        else:
            for y in range(y0,y1):
                c=original.getpixel((sx,y))
                for x in range(x0,x1):im.putpixel((x,y),c)
        put_center(im,box,fz_text(text,10,(255,255,255)))
    for box,(cx,cy),sample in hide:  # user 587: inpaint the old strokes so the crossed icon stays as in the original
        patch,region=rebuild(box,'隐藏窗口',sample);im.paste(patch,region[:2])
        put_center(im,box,fz_text('隐藏窗口',10,(255,255,255)),dy=1)  # original text starts 1 row lower
    return im,[s[:2] for s in specs]+[(h[0],'隐藏窗口') for h in hide]
    for box,(cx,cy),sample in hide:  # (old 493 symmetry method, unused)
        x0,y0,x1,y1=box
        for y in range(y0,y1):
            bg=original.getpixel((sample,y))
            for x in range(x0,x1):
                color=bg
                if cx-17<=x<=cx+17 and y<=cy+14:
                    donor=original.getpixel((2*cx-x,2*cy-y));donor_bg=original.getpixel((sample,2*cy-y))
                    if donor[0]>donor_bg[0]+8:color=tuple(max(0,min(255,bg[k]+donor[k]-donor_bg[k])) for k in range(3))+(bg[3],)
                im.putpixel((x,y),color)
        put_center(im,box,fz_text('隐藏窗口',10,(255,255,255)),dy=1)  # original text starts 1 row lower
    return im,[s[:2] for s in specs]+[(h[0],'隐藏窗口') for h in hide]

def info_ctpk(cur):
    original=Image.open(ROOT/'export_base/battle/panel/info.ctpk.00.png').convert('RGBA');im=cur.copy()
    box=(111,107,148,124);plate=Image.new('RGBA',(37,17),'white');plate.putalpha(original.crop(box).getchannel('A'))
    g=fz_text('返回',10,(51,51,51));plate.alpha_composite(g,(3,round((17-g.height)/2)));im.paste(plate,box[:2])
    box=(162,85,234,103);cell=Image.new('RGBA',(72,18));g=fz_text('切换地图显示',10,(51,51,51),(255,255,255),1)
    cell.alpha_composite(g,(1,round((18-g.height)/2)));im.paste(cell,box[:2])
    return im,[((111,107,148,124),'返回'),((162,85,234,103),'切换地图显示')]

def map_plt(cur):
    previous=Image.open(ROOT/'translation/previews_504/map_plt_icon.ctpk.00.png').convert('RGBA');im=cur.copy()
    original=Image.open(ROOT/'export_base/mapdat/tex/map_plt_icon.ctpk.00.png').convert('RGBA')
    # user 587: per-character sizes follow the Japanese layout (small kana/particles -> small Chinese chars)
    lines=[[[('不可思议',10)],[('之',7),('国',10),('的',7),('你',10)]],
           [[('联谊',10)],[('咖啡厅',10)]],
           [[('放学后',9)],[('恶灵',11),('俱乐部',9)]],
           [[('稻羽',10)],[('乡土展',10)]],
           [[('时钟塔',11)]]]
    specs=[]
    for i,y in enumerate([3,38,73,108,143]):specs+=[(i,(259,y,319,y+30),False),(i,(324,y,384,y+30),True)]
    specs+=[(0,(147,383,207,413),False),(3,(210,383,270,413),False),(1,(147,418,207,448),False),(4,(210,418,270,448),False),
            (2,(147,452,207,482),False),(0,(59,447,119,477),True),(1,(263,479,323,509),True),(2,(326,479,386,509),True),
            (3,(389,479,449,509),True),(4,(452,479,512,509),True)]
    L=lambda c:0.299*c[0]+0.587*c[1]+0.114*c[2]
    done=[]
    for index,outer,blue in specs:
        l,t,r,b=outer;box=(l+2,t+3,r-2,b-3);x0,y0,x1,y1=box
        oc=original.crop(outer)
        pressed=(not blue) and any(L(oc.getpixel((x,y)))<100 for y in range(3,27) for x in range(8,52))
        # original Japanese line bottoms (text rows only, between the 2px borders)
        if blue:ink=[y for y in range(3,27) if any(L(oc.getpixel((x,y)))>215 and oc.getpixel((x,y))[2]>200 and abs(oc.getpixel((x,y))[0]-oc.getpixel((x,y))[2])<60 for x in range(8,52))]
        else:ink=[y for y in range(3,27) if any(L(oc.getpixel((x,y)))<(120 if pressed else 165) for x in range(8,52))]
        groups=[];
        for y in ink:
            if groups and y-groups[-1][-1]<=2:groups[-1].append(y)
            else:groups.append([y])
        bottoms=[t+g[-1]+1 for g in groups if len(g)>=3]
        # background: a clean column of the 時計塔 button in the same group/state (single centred line)
        ref={(259,False):(259,143),(324,True):(324,143)}.get((l,blue))
        if ref is None:ref=(210,418) if not blue else (452,479)
        for y in range(y0,y1):
            c=original.getpixel((ref[0]+6,ref[1]+(y-t)))
            for x in range(x0,x1+1):im.putpixel((x,y),c)  # +1 column: old text reached past the box
        color=(255,255,255) if blue else ((85,85,85) if pressed else (105,105,105))
        spec=lines[index]
        if len(bottoms)!=len(spec):bottoms=[t+14,t+26] if len(spec)==2 else [t+21]
        for row,segs in enumerate(spec):
            parts=[fz_text(tx,h,color,bold=0.3) for tx,h in segs]
            W=sum(g.width for g in parts)+(len(parts)-1);H=max(g.height for g in parts)
            if W>x1-x0:parts=[g.resize((max(1,int(g.width*(x1-x0)/W)),g.height),Image.Resampling.LANCZOS) for g in parts];W=sum(g.width for g in parts)+(len(parts)-1)
            x=round((x0+x1-W)/2);base=bottoms[row]
            for g in parts:im.alpha_composite(g,(x,base-g.height));x+=g.width+1
        done.append((box,'/'.join(''.join(t for t,_ in segs) for segs in spec)+(' (pressed)' if pressed else '')))
    rows=[(['第1章','第2章','第3章','最终章'],(255,0,255)),(['第1场','第2场','第3场','第4场','终点'],(255,0,255)),
          (['第一怪','第二怪','第三怪','第四怪','最终怪'],(255,51,0)),(['第一夜','第二夜','第三夜','第四夜','最终夜'],(255,255,0)),
          (['1层','2层','3层','4层','5层'],(51,51,51)),(['6层','7层','8层','9层','顶层'],(51,51,51))]
    im.paste(Image.new('RGBA',(484-313,476-390)),(313,390))  # clear the whole floor-label area (old 最終階 etc. were wider than their cells)
    for row,(texts,color) in enumerate(rows):
        for col,text in enumerate(texts):
            x=315+31*col;y=391+14*row;width=46 if row==1 and col==4 else 30;box=(x,y,x+width,y+13)
            im.paste(Image.new('RGBA',(width,13)),box[:2])
            g=fz_text(text,8,color)
            if g.width>width:g=g.resize((width,g.height),Image.Resampling.LANCZOS)
            put_center(im,box,g);done.append((box,text))
    # 504 list labels on yellow plates
    for box,sx in [((251,180,299,191),249),((313,180,361,191),311)]:
        x0,y0,x1,y1=box
        for y in range(y0,y1):
            c=previous.getpixel((sx,y))
            for x in range(x0,x1):im.putpixel((x,y),c)
        g=fz_text('迷宫列表',8,(51,51,51));put_center(im,box,g);done.append((box,'迷宫列表'))
    return im,done

def pink(cur):
    im=cur.copy();done=[]
    specs=[]
    for y,text in [(0,'斩突坏炎冰风'),(17,'雷光暗弱耐无')]:
        for i,c in enumerate(text):specs.append(((90+i*17,y,107+i*17,y+17),c))
    specs+=list(zip([(130,34,149,51),(149,34,169,51),(170,34,189,51),(189,34,209,51),(209,34,229,51)],'力魔耐速运'))
    for box,c in specs:
        l,t,r,b=box;im.paste(Image.new('RGBA',(r-l,b-t)),(l,t))
        put_center(im,box,fz_text(c,12,(255,126,124)));done.append((box,c))
    return im,done


def info_codex_plate(cur):
    """User: keep Codex 513 text, but restore the white pill under 切换地图显示."""
    original=Image.open(ROOT/'export_base/battle/panel/info.ctpk.00.png').convert('RGBA');im=cur.copy()
    box=(162,85,234,103);l,t,r,b=box
    patch=Image.new('RGBA',((r-l)*4,(b-t)*4));d=ImageDraw.Draw(patch)
    font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',40);bb=d.textbbox((0,0),'切换地图显示',font=font)
    d.text((8-bb[0],(patch.height-bb[3]+bb[1])/2-bb[1]),'切换地图显示',font=font,fill='#333333',stroke_width=6,stroke_fill='white')
    rendered=patch.resize((r-l,b-t),Image.Resampling.LANCZOS)
    pa=original.crop(box).getchannel('A')
    plate=Image.new('RGBA',(r-l,b-t),'white');plate.putalpha(pa)
    lifted=Image.new('RGBA',rendered.size);lifted.alpha_composite(rendered,(0,-1))  # text up 1px
    plate.alpha_composite(lifted);plate.putalpha(pa)  # clip to the original flat pill silhouette
    im.paste(plate,box[:2])
    return im,[(box,'切换地图显示(Codex字上移1px+白底按原版轮廓裁切)')]

REPLICA={('event/skip_btn.spr3',3184):skip_btn,('battle/panel/info.ctpk',0):info_codex_plate,
         ('mapdat/tex/map_plt_icon.ctpk',0):map_plt,('camp/partyinfo.spr3',271552):pink}

def main():
    T=final_textures();report=[]
    for key,r in sorted(T.items()):
        orig=Image.open(ROOT/r['source']).convert('RGBA');cur=Image.open(ROOT/r['png']).convert('RGBA');new=cur.copy();log=[]
        keep=[tuple(k) for k in read(ROOT/'translation/inventory_587/decisions.json')['keep_codex_textures']]
        if key in keep:
            name=key[0].replace('/','_')+f'_{key[1]}.png';cur.save(OUT/name)
            report.append(dict(container=key[0],texture_offset=key[1],source=r['source'],approved=r['png'],png=(OUT/name).relative_to(ROOT).as_posix(),
                sha256=hashlib.sha256((OUT/name).read_bytes()).hexdigest(),decision='keep_codex',edits=[],errors=[]))
            cmp=OUT/('compare_'+name)
            if cmp.exists():cmp.unlink()
            print(name,'kept Codex version');continue
        if key in REPLICA:
            new,done=REPLICA[key](new);log+= [dict(box=list(b),text=t,method='replica') for b,t in done]
        if key==('camp/c_main.spr3',82336):
            # undo 574 relocation of sprite 218: restore bar texels, label goes back to its own box
            new.paste(orig.crop((160,350,232,368)),(160,350))
        for i,u in enumerate(U):
            if (u['container'],u['texture_offset'])!=key:continue
            cfg=TEXTS.get(str(i))
            if not cfg or cfg=='skip':continue
            if isinstance(cfg,(str,list)):cfg={'text':cfg}
            try:res=RL.redraw_unit(new,orig,u,cfg)
            except Exception as e:log.append(dict(unit=i,error=repr(e)));continue
            if res:new,info=res;log.append(dict(unit=i,**info))
        if key==('facility/velvet.spr3',31616):
            # keep the original "LV" glyphs intact (Codex's 顺 had overwritten the right column of V)
            new.paste(orig.crop((61,108,105,125)),(61,108))
        name=key[0].replace('/','_')+f'_{key[1]}.png';p=OUT/name;new.save(p)
        # review sheet: original | current | FZ redraw (2x, on grey and on dark)
        bb=diff_bbox(orig,new) or (0,0,orig.width,orig.height);pad=4
        crop=(max(0,bb[0]-pad),max(0,bb[1]-pad),min(orig.width,bb[2]+pad),min(orig.height,bb[3]+pad))
        S=2 if crop[2]-crop[0]>300 else 3;w,h=(crop[2]-crop[0])*S,(crop[3]-crop[1])*S
        f=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16);panels=[('日文原版',orig),('当前版本（Codex）',cur),('方正轻吟体重绘（待验收）',new)]
        vertical=w>h*1.3
        sheet=Image.new('RGB',((w+16) if vertical else (w*3+40),(h*3+90) if vertical else (h+28)),(150,150,158));d=ImageDraw.Draw(sheet)
        for k,(lab,im) in enumerate(panels):
            bg=Image.new('RGBA',im.size,(110,110,120,255));bg.alpha_composite(im);tile=bg.crop(crop).resize((w,h),Image.Resampling.NEAREST)
            x,y=(8,k*(h+30)+26) if vertical else (k*(w+20),26)
            sheet.paste(tile,(x,y));d.text((x+2,y-23),lab,font=f,fill='black')
        sp=OUT/('compare_'+name);sheet.save(sp)
        report.append(dict(container=key[0],texture_offset=key[1],source=r['source'],approved=r['png'],png=p.relative_to(ROOT).as_posix(),
            sha256=hashlib.sha256(p.read_bytes()).hexdigest(),compare=sp.relative_to(ROOT).as_posix(),edits=log,
            errors=[x for x in log if 'error' in x]))
        print(name,len(log),'edits',len([x for x in log if 'error' in x]),'errors',flush=True)
    (OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=1),encoding='utf-8')
if __name__=='__main__':main()
