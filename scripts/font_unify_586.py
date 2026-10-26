"""586: redraw every CJK glyph with one face (Q2 approach), fitted to the original kanji ink box.

Kana, Latin, digits and symbols keep their original pixels. The encoding map is unchanged.
"""
import json,statistics
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
PRIMARY=ROOT.parent/'FZFWQingYinTiJWB.TTF'
FALLBACK=ROOT/'fonts/SourceHanSansSC-Medium.otf'
FONTS=['anito_13_13','anito_16_16','humming_d_12','humming_d_14','seurapro_12_12','seurapro_13_13']
HI=96  # supersampled em size
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def is_cjk(c):return '一'<=c<='鿿'
def code_char(code):
    try:return code.encode('utf-16-be').decode('cp932').strip('\0')
    except UnicodeDecodeError:return ''
class Face:
    def __init__(self,path):
        self.font=ImageFont.truetype(str(path),HI)
        self.notdef={self._raw(chr(0xE000)).tobytes(),self._raw(chr(0xFFFF)).tobytes()}
    def _raw(self,c):
        im=Image.new('L',(HI*2,HI*2));ImageDraw.Draw(im).text((HI//2,HI*3//2),c,font=self.font,anchor='ls',fill=255);return im
    def has(self,c):return self._raw(c).tobytes() not in self.notdef
    def render(self,c):
        """Return (L image, origin) with baseline at y=HI*3//2, pen x at HI//2."""
        return self._raw(c)
FACES=None
def faces():
    global FACES
    if FACES is None:FACES=[Face(PRIMARY),Face(FALLBACK)]
    return FACES
def pick(c):
    for f in faces():
        if f.has(c):return f
    raise ValueError(f'no face has {c!r}')
def ink_box(im,threshold=80):return im.point(lambda v:255 if v>threshold else 0).getbbox()
def original_target(name):
    """Median thresholded ink box of the font's original kanji, in cell pixels."""
    m=read(ROOT/f'full_work/font_original/{name}/{name}_manifest.json')
    tx=m['textureInfo'];si=tx['sheetInfo'];cw=tx['glyph']['width']+1;ch=tx['glyph']['height']+1;per=si['cols']*si['rows']
    sheets={};boxes=[]
    for code,idx in m['glyphMap'].items():
        if not is_cjk(code_char(code)):continue
        s,slot=divmod(idx,per)
        if s not in sheets:sheets[s]=Image.open(ROOT/f'full_work/font_original/{name}/{name}_sheet{s}.png').convert('RGBA')
        x=slot%si['cols']*cw+1;y=slot//si['cols']*ch+2
        b=ink_box(sheets[s].crop((x,y,x+cw,y+ch)).getchannel('A'))
        if b:boxes.append(b)
    return [statistics.median(b[i] for b in boxes) for i in range(4)],(cw,ch)
_SOURCE={}
def source_box(face):
    """Median ink box of common kanji in a face, in supersampled pixels."""
    if id(face) not in _SOURCE:
        sample='国的第章要读取哪个存档不可思议之你一二三人大中日本学生时间东西南北愿意灵魂迷宫钟楼'
        boxes=[ink_box(face.render(c)) for c in sample if face.has(c)]
        _SOURCE[id(face)]=[statistics.median(b[i] for b in boxes) for i in range(4)]
    return _SOURCE[id(face)]
def render_cell(c,target,cell,weight=0):
    """Map the face's median kanji box onto the target box; keeps per-glyph relative size."""
    face=pick(c);hi=face.render(c);sb=source_box(face);(cw,ch)=cell
    tl,tt,tr,tb=target
    sx=(tr-tl)/(sb[2]-sb[0]);sy=(tb-tt)/(sb[3]-sb[1])
    # Affine: source px -> cell px. Resize whole supersampled canvas, then crop.
    W=round(hi.width*sx);H=round(hi.height*sy)
    small=hi.resize((W,H),Image.Resampling.LANCZOS)
    ox=tl-sb[0]*sx;oy=tt-sb[1]*sy
    cellim=Image.new('L',(cw,ch));cellim.paste(small,(round(ox),round(oy)))
    if weight:
        from PIL import ImageFilter
        cellim=Image.blend(cellim,cellim.filter(ImageFilter.MaxFilter(3)),weight)
    out=Image.new('RGBA',(cw,ch),(255,255,255,0));out.putalpha(cellim)
    return out,face is faces()[0]
