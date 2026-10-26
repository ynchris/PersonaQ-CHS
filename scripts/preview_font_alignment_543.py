"""Isolated added-glyph alignment prototype; no font binary or game changes."""
from collections import Counter
from statistics import median
from PIL import Image,ImageDraw,ImageFont
from compile_translation import ROOT,read,write
OUT=ROOT/'translation/feedback_543';mapping=read(ROOT/'translation/font_encoding.hex.json')
phrases=['蕾丝衬衫','京折扇','更换谁的装备？','谎言夸口者']
folders=sorted((ROOT/'full_work/font_verify').glob('*'));report=[]
canvas=Image.new('RGBA',(1440,110*len(folders)),'#222222');d=ImageDraw.Draw(canvas)
for row,folder in enumerate(folders):
    name=folder.name;m=read(folder/f'{name}_manifest.json');old=read(ROOT/f'full_work/font_original/{name}/{name}_manifest.json')
    tx=m['textureInfo'];si=tx['sheetInfo'];cw=tx['glyph']['width']+1;ch=tx['glyph']['height']+1;per=si['cols']*si['rows'];cache={}
    def glyph(index):
        sheet,slot=divmod(index,per)
        if sheet not in cache:cache[sheet]=Image.open(folder/f'{name}_sheet{sheet}.png').convert('RGBA')
        sx=slot%si['cols']*cw+1;sy=slot//si['cols']*ch+2
        return cache[sheet].crop((sx,sy,sx+cw,sy+ch))
    def bounds(im):return im.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox()
    refs=[]
    for code,index in old['glyphMap'].items():
        try:c=ord(code).to_bytes(1 if ord(code)<256 else 2,'big').decode('cp932')
        except (UnicodeError,OverflowError):continue
        if len(c)!=1 or not '\u4e00'<=c<='\u9fff':continue
        bb=bounds(glyph(index))
        if bb:refs.append((c,old['glyphWidths'][str(index)]['char'],bb))
    assert refs,name
    advance=Counter(r[1] for r in refs).most_common(1)[0][0]
    face=ImageFont.truetype(str(ROOT/'fonts/SourceHanSansSC-Medium.otf'),advance*4)
    original_bottom=median(r[2][3] for r in refs)
    face_bottom=median(face.getbbox(r[0],anchor='ls')[3]/4 for r in refs)
    baseline=original_bottom-face_bottom
    target_top=round(median(r[2][1] for r in refs));target_bottom=round(original_bottom)
    face_boxes=[face.getbbox(r[0],anchor='ls') for r in refs]
    source_top=min(b[1] for b in face_boxes);source_bottom=max(b[3] for b in face_boxes)
    report.append(dict(font=name,original_reference_count=len(refs),advance=advance,original_median_bottom=original_bottom,
        baseline=baseline,source_font_size=advance,target_vertical_band=[target_top,target_bottom],
        source_vertical_band=[source_top,source_bottom],original_glyphs_preserved=True))
    d.text((5,row*110+3),name,fill='white')
    for col in range(2):
        x=col*720+5;y=row*110+35
        for phrase in phrases:
            for char in phrase:
                code=chr(int(mapping[char],16));idx=m['glyphMap'][code];cell=glyph(idx);width=m['glyphWidths'][str(idx)]['char']
                if col and code not in old['glyphMap'] and '\u4e00'<=char<='\u9fff':
                    high=Image.new('RGBA',(advance*4,advance*12));dr=ImageDraw.Draw(high)
                    dr.text((0,advance*4),char,font=face,anchor='ls',fill='white')
                    # One shared transformation per font, never per-character centering.
                    band=high.crop((0,advance*4+source_top,advance*4,advance*4+source_bottom))
                    cell=Image.new('RGBA',(cw,ch));cell.paste(band.resize((advance,target_bottom-target_top),Image.Resampling.LANCZOS),(0,target_top));width=advance
                else:
                    # Respect runtime glyph width instead of previewing unused cell gutter.
                    cell=cell.crop((0,0,m['glyphWidths'][str(idx)]['glyph'],ch))
                enlarged=cell.resize((cell.width*2,ch*2),Image.Resampling.NEAREST)
                canvas.alpha_composite(enlarged,(x,y));x+=width*2
            x+=15
canvas.convert('RGB').save(OUT/'font_alignment_compare.png');write(OUT/'font_alignment_prototype.json',dict(fonts=report,applied=False,packaged=False,scope='Only new CJK glyphs; shared old glyphs unchanged. Actual in-game placement still needs validation.'))
print(report)
