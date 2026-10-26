"""587: remove thin white text from a textured background by onion-peel inpainting."""
import numpy as np
from PIL import Image,ImageFilter,ImageDraw

def text_mask(img,box,min_rgb=200,max_sat=60):
    """White-ish low-saturation pixels inside box (the original Japanese strokes), grown by 1px."""
    a=np.asarray(img.crop(box).convert('RGBA')).astype(int)
    rgb=a[...,:3];m=(rgb.min(-1)>=min_rgb)&((rgb.max(-1)-rgb.min(-1))<=max_sat)&(a[...,3]>0)
    im=Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.MaxFilter(3))
    return np.asarray(im)>0

def inpaint(img,box,mask):
    """Fill masked pixels from the outside in with the mean of already-known 8-neighbours."""
    a=np.asarray(img.crop(box).convert('RGBA')).astype(float);known=~mask.copy();h,w=known.shape
    todo=mask.copy()
    while todo.any():
        acc=np.zeros_like(a);cnt=np.zeros((h,w))
        for dy in (-1,0,1):
            for dx in (-1,0,1):
                if dx==dy==0:continue
                sh=np.roll(np.roll(a*known[...,None],dy,0),dx,1);sk=np.roll(np.roll(known,dy,0),dx,1)
                # do not wrap around edges
                if dy==1:sh[0]=0;sk[0]=0
                if dy==-1:sh[-1]=0;sk[-1]=0
                if dx==1:sh[:,0]=0;sk[:,0]=0
                if dx==-1:sh[:,-1]=0;sk[:,-1]=0
                acc+=sh;cnt+=sk
        front=todo&(cnt>=2)
        if not front.any():front=todo&(cnt>=1)
        if not front.any():break
        a[front]=acc[front]/cnt[front][:,None];known|=front;todo&=~front
    out=img.copy();out.paste(Image.fromarray(np.clip(a.round(),0,255).astype('uint8'),'RGBA'),box[:2]);return out

def relative_text_mask(img,box,sample_x,thr=None,grow=2):
    """Pixels much brighter than the row background sampled at column sample_x (text, not icon shading)."""
    a=np.asarray(img.convert('RGBA')).astype(float)
    x0,y0,x1,y1=box;lum=lambda c:0.299*c[...,0]+0.587*c[...,1]+0.114*c[...,2]
    reg=lum(a[y0:y1,x0:x1]);bg=lum(a[y0:y1,sample_x])[:,None]
    d=reg-bg
    if thr is None:thr=max(35,0.45*d.max())
    m=d>thr
    im=Image.fromarray((m*255).astype('uint8'))
    for _ in range(grow):im=im.filter(ImageFilter.MaxFilter(3))
    return np.asarray(im)>0

def _bg_rows(a,box,sample_x):
    x0,y0,x1,y1=box
    return np.repeat(a[y0:y1,sample_x][:,None,:],x1-x0,axis=1)

def inpaint_delta(img,box,mask,sample_x,triangles=()):
    """Inpaint in 'overlay' space (pixel minus row background), then add the row background back.
    triangles: list of (x_from,x_to) column ranges (box-local) whose shape is a downward triangle; its two
    lower edges are fitted on the visible part and extended to their intersection to restore the hidden tip."""
    A=np.asarray(img.convert('RGBA')).astype(float);x0,y0,x1,y1=box
    bg=_bg_rows(A,box,sample_x);delta=A[y0:y1,x0:x1]-bg
    # under the text the true overlay is either 0 (plain row background) or part of a shape
    filled=delta.copy();filled[mask]=0
    lum=lambda c:0.299*c[...,0]+0.587*c[...,1]+0.114*c[...,2]
    for c0,c1 in triangles:
        d=lum(delta[:,c0:c1]);vis=(d>10)&(d<60)&~mask[:,c0:c1]
        rows=[y for y in range(vis.shape[0]) if vis[y].any()]
        if len(rows)<4:continue
        lower=rows[len(rows)//2:]
        L=np.array([(y,c0+np.where(vis[y])[0].min()) for y in lower],float);Rr=np.array([(y,c0+np.where(vis[y])[0].max()) for y in lower],float)
        al,bl=np.polyfit(L[:,0],L[:,1],1);ar,br=np.polyfit(Rr[:,0],Rr[:,1],1)
        yt=(br-bl)/(al-ar) if abs(al-ar)>1e-6 else 1e9  # apex row (box-local)
        col=np.median(delta[:,c0:c1][vis],axis=0)  # overlay colour of the shape
        S=8;H,W=mask.shape;cov=np.zeros((H,W))
        for yy in range(H):
            for xx in range(c0,c1):
                if not mask[yy,xx] or yy<rows[-1]:continue
                n=0
                for sy in range(S):
                    for sx in range(S):
                        y=yy+(sy+.5)/S;x=xx+(sx+.5)/S
                        if y<=yt and al*y+bl<=x<=ar*y+br:n+=1
                cov[yy,xx]=n/S/S
        m=cov>0
        filled[m]=filled[m]*(1-cov[m][:,None])+col*cov[m][:,None]
    out_rgba=np.clip(bg+filled,0,255);out_rgba[...,3]=A[y0:y1,x0:x1,3]
    a2=A.copy();a2[y0:y1,x0:x1][mask]=out_rgba[mask]
    return Image.fromarray(a2.round().astype('uint8'),'RGBA')

LUM=lambda c:0.299*c[...,0]+0.587*c[...,1]+0.114*c[...,2]
def rebuild_overlay(img,box,mask,polys=(),radius=2,glow_from=None,glow_thr=12,local_bg=0):
    """Background = per-row darker-half median of uncovered pixels; masked pixels become shape colour
    where the nearby uncovered pixels are mostly shape, else background; optional polygons (box-local,
    float coords) are drawn with 8x coverage in the shape colour."""
    A=np.asarray(img.convert('RGBA')).astype(float);x0,y0,x1,y1=box;R=A[y0:y1,x0:x1].copy();H,W=mask.shape
    bg=np.zeros_like(R);rowbg={}
    for y in range(H):
        cs=R[y,3:W-3][~mask[y,3:W-3]]
        if len(cs)>=6:
            l=LUM(cs);sel=cs[l<=np.median(l)];rowbg[y]=np.median(sel,axis=0)
    ks=sorted(rowbg)
    for y in range(H):
        if y in rowbg:bg[y]=rowbg[y];continue
        lo=[k for k in ks if k<y];hi=[k for k in ks if k>y]
        if lo and hi:t=(y-lo[-1])/(hi[0]-lo[-1]);bg[y]=rowbg[lo[-1]]*(1-t)+rowbg[hi[0]]*t
        else:bg[y]=rowbg[(lo or hi)[-1 if lo else 0]]
    delta=R-bg
    if glow_from is not None:  # faint text glow in the text rows (shapes there come back from polygons)
        near=np.asarray(Image.fromarray((mask*255).astype('uint8')).filter(ImageFilter.MaxFilter(7)))>0  # within 3px of the text
        g=(LUM(delta)>glow_thr)&near;g[:glow_from]=False;mask=mask|g
    shape=(LUM(delta)>10)&~mask
    col=np.median(delta[shape],axis=0) if shape.any() else np.zeros(4)
    out=R.copy()
    for y,x in zip(*np.where(mask)):
        ya,yb,xa,xb=max(0,y-radius),min(H,y+radius+1),max(0,x-radius),min(W,x+radius+1)
        known=~mask[ya:yb,xa:xb]
        frac=shape[ya:yb,xa:xb][known].mean() if known.any() else 0
        base=bg[y,x]
        if local_bg:
            for rr in range(local_bg,local_bg+6):
                ya2,yb2,xa2,xb2=max(0,y-rr),min(H,y+rr+1),max(0,x-rr),min(W,x+rr+1)
                ok=(~mask[ya2:yb2,xa2:xb2])&(~shape[ya2:yb2,xa2:xb2])
                if ok.sum()>=4:base=np.median(R[ya2:yb2,xa2:xb2][ok],axis=0);break
        out[y,x]=base+(col if frac>0.5 else 0)
    S=8
    for poly in polys:  # each polygon uses the overlay colour of its own visible part
        big=Image.new('L',(W*S,H*S));d=ImageDraw.Draw(big);d.polygon([(x*S,y*S) for x,y in poly],fill=255)
        cov=np.asarray(big.resize((W,H),Image.Resampling.BOX)).astype(float)/255
        own=(cov>0.9)&shape
        pc=np.median(delta[own],axis=0) if own.sum()>=3 else col
        m=mask&(cov>0)
        out[m]=(out[m] if local_bg else bg[m])+pc*cov[m][:,None]
    out[...,3]=R[...,3]
    a2=A.copy();a2[y0:y1,x0:x1]=out
    return Image.fromarray(np.clip(a2.round(),0,255).astype('uint8'),'RGBA')

def rebuild_rows(img,outer,rows,polys=(),thr=6,ref_rows=None):
    """Clean text rows across the whole button interior.
    outer: button box; rows: (ya,yb) absolute rows to clean. Every pixel in those rows that is not plain
    background (overlay lum > thr vs. the row's darker-half median) is replaced by horizontal linear
    interpolation between the nearest clean pixels of the same row; then polygons (absolute coords)
    are added with the median shape overlay colour measured on ref_rows (absolute, above the text)."""
    A=np.asarray(img.convert('RGBA')).astype(float);bx0,by0,bx1,by1=outer
    ix0,ix1=bx0+3,bx1-3;out=A.copy()
    def rowbg(y):
        cs=A[y,ix0:ix1];l=LUM(cs);return np.median(cs[l<=np.median(l)],axis=0)
    ya,yb=rows
    for y in range(ya,yb):
        b=rowbg(y);d=LUM(A[y,ix0:ix1]-b)
        clean=np.where(np.abs(d)<=thr)[0]
        if len(clean)<2:continue
        for x in range(ix0,ix1):
            i=x-ix0
            if abs(d[i])<=thr:continue
            L=clean[clean<i];R=clean[clean>i]
            if len(L) and len(R):
                l,r=L[-1],R[0];t=(i-l)/(r-l);out[y,x]=A[y,ix0+l]*(1-t)+A[y,ix0+r]*t
            else:out[y,x]=A[y,ix0+(L[-1] if len(L) else R[0])]
    if polys:
        ra,rb=ref_rows;sh=[]
        for y in range(ra,rb):
            b=rowbg(y);dd=A[y,ix0:ix1]-b;m=LUM(dd)>10;sh+=list(dd[m])
        col=np.median(np.array(sh),axis=0) if sh else np.zeros(4)
        S=8;W,H=bx1-bx0,by1-by0;big=Image.new('L',(W*S,H*S));dr=ImageDraw.Draw(big)
        for poly in polys:dr.polygon([((x-bx0)*S,(y-by0)*S) for x,y in poly],fill=255)
        cov=np.asarray(big.resize((W,H),Image.Resampling.BOX)).astype(float)/255
        for y in range(ya,yb):
            for x in range(ix0,ix1):
                c=cov[y-by0,x-bx0]
                if c>0:out[y,x,:3]=out[y,x,:3]+col[:3]*c
    out[...,3]=A[...,3]
    return Image.fromarray(np.clip(out.round(),0,255).astype('uint8'),'RGBA')

def hfill_masked(img,box,mask,rows=None):
    """Replace masked pixels by horizontal linear interpolation between the nearest unmasked pixels of the same row."""
    A=np.asarray(img.convert('RGBA')).astype(float);x0,y0,x1,y1=box;R=A[y0:y1,x0:x1];H,W=mask.shape;out=R.copy()
    for y in range(H):
        if rows and not (rows[0]<=y<rows[1]):continue
        known=np.where(~mask[y])[0]
        if len(known)<2:continue
        for x in np.where(mask[y])[0]:
            L=known[known<x];Rr=known[known>x]
            if len(L) and len(Rr):l,r=L[-1],Rr[0];t=(x-l)/(r-l);out[y,x]=R[y,l]*(1-t)+R[y,r]*t
            else:out[y,x]=R[y,(L[-1] if len(L) else Rr[0])]
    a2=A.copy();a2[y0:y1,x0:x1]=out
    return Image.fromarray(np.clip(a2.round(),0,255).astype('uint8'),'RGBA')
