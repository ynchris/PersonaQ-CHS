"""587: redraw UI label text with the FZ (Humming-family) face, styled from the original Japanese.

Per unit (sprite box): erase the current Chinese text, restore background row by row,
measure the original Japanese ink (height, fill, outline), and draw the Chinese with
the same metrics. Pixels outside each unit's erase area are kept from the approved texture.
"""
import json,sys,statistics
from collections import Counter
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw,ImageFilter,ImageFont
ROOT=Path(__file__).resolve().parent
FZ=str(ROOT.parent/'FZFWQingYinTiJWB.TTF');SHS=str(ROOT/'fonts/SourceHanSansSC-Medium.otf')
SS=8  # supersampling
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def diff_bbox(a,b):
    """bbox of any RGBA difference (getbbox on RGBA only looks at alpha)."""
    d=ImageChops.difference(a.convert('RGBA'),b.convert('RGBA')).split()
    m=d[0]
    for c in d[1:]:m=ImageChops.lighter(m,c)
    return m.getbbox()
def diff_mask(a,b,thr=0):
    d=ImageChops.difference(a.convert('RGBA'),b.convert('RGBA')).split();m=d[0]
    for c in d[1:]:m=ImageChops.lighter(m,c)
    return m.point(lambda v:255 if v>thr else 0)
def lum(c):return 0.299*c[0]+0.587*c[1]+0.114*c[2]
def cdist(a,b):return max(abs(a[i]-b[i]) for i in range(4))

def row_background(img,box,mask):
    """Per-row background from pixels not in mask; linear fill across masked runs."""
    x0,y0,x1,y1=box;px=img.load();m=mask.load();out={}
    for y in range(y0,y1):
        xs=[x for x in range(x0,x1) if not m[x-x0,y-y0]]
        for x in range(x0,x1):
            if not m[x-x0,y-y0]:continue
            L=[t for t in xs if t<x];R=[t for t in xs if t>x]
            if L and R:
                a=px[L[-1],y];b=px[R[0],y];t=(x-L[-1])/(R[0]-L[-1])
                out[(x,y)]=tuple(round(a[i]+(b[i]-a[i])*t) for i in range(4))
            elif L or R:out[(x,y)]=px[(L[-1] if L else R[0]),y]
            else:
                # whole row masked: interpolate vertically within the box column
                ys=[t for t in range(y0,y1) if not m[x-x0,t-y0]]
                U=[t for t in ys if t<y];D=[t for t in ys if t>y]
                if U and D:
                    a=px[x,U[-1]];b=px[x,D[0]];t=(y-U[-1])/(D[0]-U[-1])
                    out[(x,y)]=tuple(round(a[i]+(b[i]-a[i])*t) for i in range(4))
                elif U or D:out[(x,y)]=px[x,(U[-1] if U else D[0])]
                else:out[(x,y)]=(0,0,0,0)
    return out

def ink_mask(img,box,bg):
    """Text ink inside box: differs from estimated background (alpha-aware)."""
    x0,y0,x1,y1=box;px=img.load();m=Image.new('L',(x1-x0,y1-y0));mp=m.load()
    for y in range(y0,y1):
        for x in range(x0,x1):
            c=px[x,y];b=bg.get((x,y))
            if b is None:continue
            if (b[3]<40 and c[3]>40) or (b[3]>=40 and cdist(c,b)>48):mp[x-x0,y-y0]=255
    return m

def style_of(img,box,mask):
    """Fill/outline colours, outline width and stroke-ink height of the original text."""
    x0,y0,_,_=box;px=img.load();w,h=mask.size
    pts=[(x,y) for y in range(h) for x in range(w) if mask.getpixel((x,y)) and px[x+x0,y+y0][3]>160]
    if not pts:return None
    edge=mask.filter(ImageFilter.MinFilter(3))
    dark=[(x,y) for x,y in pts if lum(px[x+x0,y+y0])<128];light=[(x,y) for x,y in pts if lum(px[x+x0,y+y0])>=128]
    def med(ps):
        ps=sorted(ps,key=lambda q:lum(px[q[0]+x0,q[1]+y0]))
        if ps and lum(px[ps[0][0]+x0,ps[0][1]+y0])<128:ps=ps[:max(1,len(ps)//2)]  # dark text: ignore light AA
        else:ps=ps[len(ps)//2:]
        return tuple(round(statistics.median(px[x+x0,y+y0][i] for x,y in ps)) for i in range(3))+(255,)
    def edge_share(ps):return sum(1 for x,y in ps if not edge.getpixel((x,y)))/max(1,len(ps))
    if len(dark)<0.12*len(pts) or len(light)<0.12*len(pts):
        f=dark if len(dark)>len(light) else light
        fm=Image.new('L',mask.size)
        for x,y in f:fm.putpixel((x,y),255)
        bb=fm.getbbox();return dict(fill=med(f),outline=None,width=0,ink_h=bb[3]-bb[1])
    fill,out=(dark,light) if edge_share(dark)<edge_share(light) else (light,dark)
    fm=Image.new('L',mask.size)
    for x,y in fill:fm.putpixel((x,y),255)
    near=fm.filter(ImageFilter.MaxFilter(3))
    far=sum(1 for x,y in out if not near.getpixel((x,y)))/max(1,len(out))
    bb=fm.getbbox()
    return dict(fill=med(fill),outline=med(out),width=2 if far>0.2 else 1,ink_h=bb[3]-bb[1])

def segments(mask,gap):
    """Group ink columns/rows into reading-order word boxes (local coords)."""
    w,h=mask.size;px=mask.load()
    rows=[any(px[x,y] for x in range(w)) for y in range(h)];lines=[];y=0
    while y<h:
        if rows[y]:
            s=y
            while y<h and rows[y]:y+=1
            lines.append((s,y))
        else:y+=1
    # merge lines separated by <=1px (diacritics)
    merged=[]
    for l in lines:
        if merged and l[0]-merged[-1][1]<=0:merged[-1]=(merged[-1][0],l[1])
        else:merged.append(l)
    out=[]
    for a,b in merged:
        cols=[any(px[x,y] for y in range(a,b)) for x in range(w)];x=0;words=[]
        while x<w:
            if cols[x]:
                s=x;e=x;run=0
                while x<w and (cols[x] or run<gap):
                    run=0 if cols[x] else run+1
                    if cols[x]:e=x
                    x+=1
                words.append((s,a,e+1,b))
            else:x+=1
        out+=words
    return out

FACE_CACHE={}
def face(px):
    k=(px);
    if k not in FACE_CACHE:FACE_CACHE[k]=ImageFont.truetype(FZ,px)
    return FACE_CACHE[k]
def has_glyph(f,ch):
    return f.getmask(ch).getbbox() is not None and f.getmask(ch).tobytes()!=f.getmask('').tobytes()

def render_text(text,ink_h,style,max_w,italic=False,bold=0):
    """Render text whose CJK ink height (excl. outline) is ink_h px; returns RGBA, tight."""
    ow=style['width'] if style['outline'] else 0
    # find font px so that a reference kanji's ink height == ink_h
    size=ink_h*SS*1.18
    for _ in range(6):
        f=ImageFont.truetype(FZ,round(size));bb=f.getbbox('国')
        size*=ink_h*SS/max(1,bb[3]-bb[1])
    f=ImageFont.truetype(FZ,round(size))
    def draw(sx):
        W=int(f.getlength(text)*sx)+ow*SS*4+SS*8;H=int(size*1.6)+ow*SS*4
        big=Image.new('RGBA',(int(f.getlength(text))+ow*SS*4+SS*8,H))
        d=ImageDraw.Draw(big)
        if bold and not ow:d.text((ow*SS*2+SS*2,H*0.75),text,font=f,anchor='ls',fill=style['fill'],stroke_width=round(bold*SS),stroke_fill=style['fill'])
        else:d.text((ow*SS*2+SS*2,H*0.75),text,font=f,anchor='ls',fill=style['fill'],stroke_width=ow*SS,stroke_fill=style['outline'] or style['fill'])
        if sx!=1:big=big.resize((max(1,round(big.width*sx)),big.height),Image.Resampling.LANCZOS)
        if italic:big=big.transform(big.size,Image.Transform.AFFINE,(1,0.2,-0.2*H*0.75,0,1,0),Image.Resampling.BICUBIC)
        small=big.resize((max(1,round(big.width/SS)),max(1,round(big.height/SS))),Image.Resampling.LANCZOS)
        bb=small.getchannel('A').point(lambda v:255 if v>20 else 0).getbbox()
        return small.crop(bb)
    im=draw(1);sx=1
    while im.width>max_w and sx>0.72:
        sx-=0.04;im=draw(sx)
    return im,round(sx,2)

def redraw_unit(cur,orig,u,cfg):
    box=tuple(u['box']);x0,y0,x1,y1=box
    diff=diff_mask(orig.crop(box),cur.crop(box))
    if not diff.getbbox():return None
    # erase area: changed pixels' bbox, grown 1px, limited to box (keeps icons outside it intact)
    eb=cfg.get('erase') or list(diff.getbbox())
    eb=[max(0,eb[0]-1),max(0,eb[1]-1),min(x1-x0,eb[2]+1),min(y1-y0,eb[3]+1)]
    ob=orig.crop(box)
    ring=ImageChops.subtract(diff.filter(ImageFilter.MaxFilter(9)),diff.filter(ImageFilter.MaxFilter(3)))
    ra=[a for a,m in zip(ob.getchannel('A').getdata(),ring.getdata()) if m]
    zero=sum(1 for v in ob.getchannel('A').getdata() if v==0)/(ob.width*ob.height)
    transparent=cfg.get('mode')=='transparent' or (cfg.get('mode')!='opaque' and (not ra or zero>=0.3 or sum(1 for a in ra if a<128)>0.5*len(ra)))
    R=[eb[0],eb[1],eb[2],eb[3]] if (transparent or cfg.get('erase')) else [0,0,x1-x0,y1-y0]
    if transparent:
        emask=diff.filter(ImageFilter.MaxFilter(3))
        mp=emask.load()
        for y in range(emask.height):  # whole span between first/last changed pixel
            xs=[x for x in range(emask.width) if mp[x,y]]
            if xs:
                for x in range(xs[0],xs[-1]+1):mp[x,y]=255
        if cfg.get('erase_all'):emask=Image.new('L',emask.size,255);mp=emask.load()
        if cfg.get('erase'):
            rr=Image.new('L',emask.size);ImageDraw.Draw(rr).rectangle([eb[0],eb[1],eb[2]-1,eb[3]-1],fill=255);emask=ImageChops.multiply(emask,rr);mp=emask.load()
        bg_o={}
        for y in range(emask.height):
            for x in range(emask.width):
                if mp[x,y]:bg_o[(x+x0,y+y0)]=(0,0,0,0)
        jp=ink_mask(orig,box,bg_o)
        out=cur.copy();p=out.load()
        for k in bg_o:p[k]=(0,0,0,0)
        cn_ink=ink_mask(cur,box,bg_o).getbbox()
    else:
        # opaque: text = pixels far from the row's dominant colour inside the opaque interior.
        def text_pixels(img):
            ip=img.load();ia=img.crop(box).getchannel('A').point(lambda v:255 if v>200 else 0).filter(ImageFilter.MinFilter(5))
            rm={}
            for y in range(R[1],R[3]):
                cs=[ip[x+x0,y+y0] for x in range(R[0],R[2]) if ia.getpixel((x,y))]
                if not cs:continue
                q=Counter((c[0]//12,c[1]//12,c[2]//12) for c in cs).most_common(1)[0][0]
                sel=[c for c in cs if (c[0]//12,c[1]//12,c[2]//12)==q]
                rm[y]=tuple(round(statistics.median(c[i] for c in sel)) for i in range(4))
            m=Image.new('L',diff.size);mp=m.load()
            for y in rm:
                for x in range(R[0],R[2]):
                    c=ip[x+x0,y+y0]
                    if ia.getpixel((x,y)) and abs(lum(c)-lum(rm[y]))>70 and (cfg.get('colored_text') or max(c[:3])-min(c[:3])<70):mp[x,y]=255
            return m,rm
        jp,rowmode=text_pixels(orig)
        cnm,_=text_pixels(cur)
        cn_ink=cnm.getbbox()
        # erase the full rectangle around old+new text; fill rows from pixels just outside it
        jb=jp.getbbox();cb=cnm.getbbox()
        bs=[b for b in (cb,) if b] or [b for b in (jb,) if b]
        if not bs:bs=[R]
        rect=[min(b[0] for b in bs)-1,min(b[1] for b in bs)-1,max(b[2] for b in bs)+1,max(b[3] for b in bs)+1]
        if cfg.get('rect'):rect=cfg['rect'];cn_ink=tuple(rect)
        rect=[max(R[0],rect[0]),max(R[1],rect[1]),min(R[2],rect[2]),min(R[3],rect[3])]
        emask=Image.new('L',diff.size);ImageDraw.Draw(emask).rectangle([rect[0],rect[1],rect[2]-1,rect[3]-1],fill=255)
        # fill each erased pixel with the row's median non-text colour (keeps vertical gradients)
        cp=cur.load();ia=cur.crop(box).getchannel('A').point(lambda v:255 if v>200 else 0).filter(ImageFilter.MinFilter(5))
        txt=cnm.filter(ImageFilter.MaxFilter(3));out=cur.copy();p=out.load();bg_o={}
        meds={}
        for y in range(R[1],R[3]):
            cs=[cp[x+x0,y+y0] for x in range(R[0],R[2]) if ia.getpixel((x,y)) and not txt.getpixel((x,y))]
            if len(cs)>=max(4,(R[2]-R[0])//4):meds[y]=tuple(round(statistics.median(c[i] for c in cs)) for i in range(4))
        for y in range(rect[1],rect[3]):
            if not meds:break
            med=meds.get(y) or meds[min(meds,key=lambda t:abs(t-y))]
            for x in range(rect[0],rect[2]):p[x+x0,y+y0]=med;bg_o[(x+x0,y+y0)]=med
    if cfg.get('jp_ink'):  # explicit ink area for the original text
        keep=Image.new('L',jp.size);ImageDraw.Draw(keep).rectangle(cfg['jp_ink'],fill=255);jp=ImageChops.multiply(jp,keep)
    st=cfg.get('style') or style_of(orig,box,jp)
    if st is None:return None
    st=dict(st);st['fill']=tuple(st['fill']);st['outline']=tuple(st['outline']) if st.get('outline') else None
    if not transparent and st['outline'] and not cfg.get('style'):
        bgc=statistics.median(lum(c) for c in rowmode.values())
        if abs(lum(st['outline'])-bgc)<110:st['outline']=None;st['width']=0
    bb=jp.getbbox()
    ow=st['width'] if st['outline'] else 0
    texts=cfg['text'] if isinstance(cfg['text'],list) else [cfg['text']]
    segs=cfg.get('segments') or ([list(bb)] if len(texts)==1 else [list(s) for s in segments(jp,cfg.get('seg_gap') or max(3,(bb[3]-bb[1])//2))])
    assert len(segs)==len(texts),(u['container'],u['sprite'],len(segs),texts)
    placed=[]
    for t,s in zip(texts,segs):
        h=s[3]-s[1]-2*ow
        ink_h=cfg.get('ink_h') or (st.get('ink_h') if len(texts)==1 else None) or max(5,h)
        avail=cfg.get('max_w') or (eb[2]-eb[0] if len(texts)==1 else max(s[2]-s[0],int((s[3]-s[1])*len(t)*1.05)))
        im,sx=render_text(t,ink_h,st,avail,cfg.get('italic',False),cfg.get('bold',0))
        # Anchor on the approved Chinese ink (keeps user-approved spacing); fall back to the Japanese ink.
        ref=cn_ink if (len(texts)==1 and cn_ink) else s
        align=cfg.get('align') or ('left' if len(texts)==1 and cn_ink and bb and abs(cn_ink[0]-bb[0])<=1 else 'center')
        cx=(ref[0]+ref[2])/2;cy=(s[1]+s[3])/2
        if cfg.get('center_x') is not None:cx=cfg['center_x'];align='center'
        lx=(ref[0] if align=='left' else round(cx-im.width/2))+cfg.get('dx',0)
        ly=round(cy-im.height/2)+cfg.get('dy',0)
        lx=min(max(lx,eb[0]),eb[2]-im.width);ly=min(max(ly,0),(y1-y0)-im.height)
        out.alpha_composite(im,(x0+lx,y0+ly));eb=[min(eb[0],lx),min(eb[1],ly),max(eb[2],lx+im.width),max(eb[3],ly+im.height)];placed.append(dict(text=t,pos=[x0+lx,y0+ly],size=list(im.size),condense=sx,ink_h=ink_h))
    # nothing outside the erase rectangle may change
    assert diff_bbox(cur,out) is None or (lambda d:d[0]>=x0 and d[1]>=y0 and d[2]<=x1 and d[3]<=y1)(diff_bbox(cur,out)),'changed outside unit box'
    return out,dict(style=dict(fill=st['fill'][:3],outline=st['outline'][:3] if st['outline'] else None,width=st['width']),erase=[x0+eb[0],y0+eb[1],x0+eb[2],y0+eb[3]],placed=placed)

def fz_mask(text,w,h,ink_h=None,italic=False,pad=0):
    """FZ glyph mask (L) sized to w x h; ink height ink_h (default: fill h-2*pad)."""
    S=8;big=Image.new('L',(w*S*3,h*S*3));d=ImageDraw.Draw(big)
    target=(ink_h or h-2*pad)*S;size=target*1.15
    for _ in range(6):
        f=ImageFont.truetype(FZ,max(4,round(size)));bb=f.getbbox('国');size*=target/max(1,bb[3]-bb[1])
    f=ImageFont.truetype(FZ,max(4,round(size)));bb=d.textbbox((0,0),text,font=f)
    tw=bb[2]-bb[0];sx=min(1,(w-2*pad)*S/max(1,tw))
    d.text((w*S-bb[0],h*S-bb[1]),text,font=f,fill=255)
    m=big.crop(big.getbbox())
    if sx<1:m=m.resize((max(1,round(m.width*sx)),m.height),Image.Resampling.LANCZOS)
    if italic:m=m.transform((m.width+m.height//5,m.height),Image.Transform.AFFINE,(1,0.2,-m.height*0.2,0,1,0),Image.Resampling.BICUBIC)
    m=m.resize((max(1,round(m.width/S)),max(1,round(m.height/S))),Image.Resampling.LANCZOS)
    out=Image.new('L',(w,h));out.paste(m,((w-m.width)//2,(h-m.height)//2));return out

def redraw_icon14(cur,orig,u,cfg):
    """Codex 551 method (row-darkest background, brightest text colour) with the FZ face."""
    l,t,_,_=u['box'];box=(l+3,t+3,l+17,t+17);src=orig.crop(box)
    allpx=sorted(src.getdata(),key=lum);bright=allpx[-20:]
    color=tuple(round(statistics.median(p[c] for p in bright)) for c in range(3))+(255,)
    bg=Image.new('RGBA',(14,14))
    if cfg.get('gradient'):
        anchors=[]
        for ya,yb in [(0,5),(9,14)]:
            px=sorted([src.getpixel((x,y)) for y in range(ya,yb) for x in range(14)],key=lum)[:12]
            anchors.append(tuple(round(statistics.median(p[c] for p in px)) for c in range(3)))
        for y in range(14):
            sh=tuple(round(anchors[0][c]*(1-y/13)+anchors[1][c]*y/13) for c in range(3))+(255,)
            for x in range(14):bg.putpixel((x,y),sh)
    else:
        for y in range(14):
            row=sorted([src.getpixel((x,y)) for x in range(14)],key=lum)[:5]
            sh=tuple(round(statistics.median(p[c] for p in row)) for c in range(3))+(255,)
            for x in range(14):bg.putpixel((x,y),sh)
    m=fz_mask(cfg['text'],14,14,ink_h=cfg.get('ink_h',13))
    fg=Image.new('RGBA',(14,14),color);bg=Image.composite(fg,bg,m)
    out=cur.copy();out.paste(bg,box[:2])
    return out,dict(style=dict(fill=color[:3],outline=None,width=0),erase=list(box),placed=[dict(text=cfg['text'],pos=list(box[:2]),size=[14,14])])

def redraw_plate(cur,orig,u,cfg):
    """Codex 546 plate method: plate colour on the original alpha, centred FZ text."""
    l,t,r,b=cfg['plate_box'];w,h=r-l,b-t
    plate=Image.new('RGBA',(w,h),tuple(cfg['plate'])+(255,));plate.putalpha(orig.crop((l,t,r,b)).getchannel('A'))
    m=fz_mask(cfg['text'],w,h,ink_h=cfg.get('ink_h'),pad=cfg.get('pad',2))
    fg=Image.new('RGBA',(w,h),tuple(cfg['color'])+(255,));plate.alpha_composite(Image.composite(fg,Image.new('RGBA',(w,h)),m))
    out=cur.copy();out.paste(plate,(l,t))
    return out,dict(style=dict(fill=cfg['color'],outline=None,width=0),erase=[l,t,r,b],placed=[dict(text=cfg['text'],pos=[l,t],size=[w,h])])

_generic=redraw_unit
def redraw_unit(cur,orig,u,cfg):
    if cfg.get('mode')=='icon14':return redraw_icon14(cur,orig,u,cfg)
    if cfg.get('mode')=='plate':return redraw_plate(cur,orig,u,cfg)
    return _generic(cur,orig,u,cfg)

def redraw_pill(cur,orig,u,cfg):
    """White pill with a coloured key icon on the left and dark text on the right."""
    x0,y0,x1,y1=u['box'];im=cur.crop(u['box']);w,h=im.size;px=im.load()
    sat=lambda c:max(c[:3])-min(c[:3])
    light=cfg.get('light_text',False)
    icon_r=-2 if light else max([x for x in range(w//2) for y in range(h) if px[x,y][3]>200 and sat(px[x,y])>80] or [-1])
    sx0,sy0,sx1,sy1=0,0,w,h
    if cfg.get('use_diff'):
        d=diff_bbox(orig.crop(u['box']),im)
        if d:sx0,sy0,sx1,sy1=d
    if cfg.get('search'):sx0,sy0,sx1,sy1=cfg['search']
    istxt=(lambda c:c[3]>200 and sat(c)<60 and lum(c)>200) if light else (lambda c:c[3]>200 and sat(c)<60 and lum(c)<170)
    txt=[(x,y) for y in range(sy0,sy1) for x in range(max(icon_r+2,sx0),sx1) if istxt(px[x,y])]
    xs=[p[0] for p in txt];ys=[p[1] for p in txt]
    rect=[min(xs)-1,min(ys)-1,max(xs)+2,max(ys)+2]
    tm=Image.new('L',(w,h))
    for p in txt:tm.putpixel(p,255)
    tm=tm.filter(ImageFilter.MaxFilter(3))
    out=cur.copy();op=out.load();meds={}
    for y in range(h):
        if light:cs=[px[x,y] for x in range(max(0,rect[0]-3),min(w,rect[2]+3)) if px[x,y][3]>200 and not tm.getpixel((x,y)) and lum(px[x,y])<200]
        else:cs=[px[x,y] for x in range(icon_r+2,w) if px[x,y][3]>200 and sat(px[x,y])<60 and not tm.getpixel((x,y)) and lum(px[x,y])>170]
        if len(cs)>=(2 if light else 4):meds[y]=tuple(round(statistics.median(c[i] for c in cs)) for i in range(4))
    for y in range(max(0,rect[1]),min(h,rect[3])):
        med=meds.get(y) or meds[min(meds,key=lambda t:abs(t-y))]
        for x in range(max(0,rect[0]),min(w,rect[2])):op[x+x0,y+y0]=med
    st=dict(fill=tuple(cfg['style']['fill'])+(255,),outline=None,width=0)
    t,_=render_text(cfg['text'],cfg['style'].get('ink_h',11),st,w-icon_r-6)
    cx=(rect[0]+rect[2])/2;cy=(rect[1]+rect[3])/2
    lx=round(cx-t.width/2);ly=round(cy-t.height/2)
    lx=min(max(lx,icon_r+3),w-t.width-1)
    out.alpha_composite(t,(x0+lx,y0+ly))
    return out,dict(style=dict(fill=cfg['style']['fill'],outline=None,width=0),erase=[x0+rect[0],y0+rect[1],x0+rect[2],y0+rect[3]],placed=[dict(text=cfg['text'],pos=[x0+lx,y0+ly],size=list(t.size))])

_dispatch=redraw_unit
def redraw_unit(cur,orig,u,cfg):
    if cfg.get('mode')=='pill':return redraw_pill(cur,orig,u,cfg)
    return _dispatch(cur,orig,u,cfg)

_before_split=redraw_unit
def redraw_unit(cur,orig,u,cfg):
    if not cfg.get('split'):return _before_split(cur,orig,u,cfg)
    x0,y0,x1,y1=u['box']
    d=diff_mask(orig.crop(u['box']),cur.crop(u['box']))
    cols=[any(d.getpixel((x,y)) for y in range(d.height)) for x in range(d.width)];runs=[];x=0
    while x<d.width:
        if cols[x]:
            s0=x;gap=0;e=x
            while x<d.width and gap<cfg.get('gap',3):
                if cols[x]:e=x;gap=0
                else:gap+=1
                x+=1
            runs.append((s0,e+1))
        else:x+=1
    texts=cfg['text'];assert len(runs)==len(texts),(u['sprite'],runs,texts)
    out=cur;info=[]
    for (a,b),t in zip(runs,texts):
        sub=dict(cfg);sub.pop('split');sub['text']=t;sub['erase']=[a,0,b,y1-y0]
        r=_before_split(out,orig,u,sub)
        if r:out,i=r;info.append(i)
    return out,dict(style=info[0]['style'] if info else None,erase=[i['erase'] for i in info],placed=[p for i in info for p in i['placed']])

_before_parts=redraw_unit
def redraw_unit(cur,orig,u,cfg):
    if not cfg.get('parts'):return _before_parts(cur,orig,u,cfg)
    out=cur;info=[]
    for t,rect in cfg['parts']:
        sub={k:v for k,v in cfg.items() if k!='parts'};sub['text']=t;sub['erase']=rect;sub.setdefault('align','center')
        r=_before_split(out,orig,u,sub)
        if r:out,i=r;info.append(i)
    return out,dict(style=info[0]['style'] if info else None,erase=[i['erase'] for i in info],placed=[p for i in info for p in i['placed']])

def redraw_cutout(cur,orig,u,cfg):
    """White plate with the text knocked out as transparent holes."""
    x0,y0,x1,y1=u['box'];im=cur.crop(u['box']);w,h=im.size;a=im.getchannel('A');ap=a.load()
    sx0,sy0,sx1,sy1=cfg.get('search',[0,0,w,h])
    filled=a.copy();fp=filled.load();holes=[]
    for y in range(h):
        xs=[x for x in range(w) if ap[x,y]>200]
        if not xs:continue
        for x in range(xs[0],xs[-1]+1):
            if sx0<=x<sx1 and sy0<=y<sy1:
                if ap[x,y]<200:holes.append((x,y))
                fp[x,y]=255
    hx=[p[0] for p in holes];hy=[p[1] for p in holes]
    cx=(min(hx)+max(hx)+1)/2;cy=(min(hy)+max(hy)+1)/2
    m=fz_mask(cfg['text'],sx1-sx0,sy1-sy0,ink_h=cfg.get('ink_h',10))
    bb=m.getbbox();m=m.crop(bb)
    ox=round(cx-m.width/2);oy=round(cy-m.height/2)
    mm=Image.new('L',(w,h));mm.paste(m,(ox,oy))
    newa=ImageChops.multiply(filled,ImageChops.invert(mm))
    out=cur.copy();patch=im.copy();patch.putalpha(newa);out.paste(patch,(x0,y0))
    return out,dict(style=dict(fill='cutout',outline=None,width=0),erase=[x0+sx0,y0+sy0,x0+sx1,y0+sy1],placed=[dict(text=cfg['text'],pos=[x0+ox,y0+oy],size=list(m.size))])

_before_cutout=redraw_unit
def redraw_unit(cur,orig,u,cfg):
    if cfg.get('mode')=='cutout':return redraw_cutout(cur,orig,u,cfg)
    return _before_cutout(cur,orig,u,cfg)
