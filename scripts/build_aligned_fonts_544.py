"""Apply approved 543 calibration to new CJK glyphs in six isolated BCFNTs."""
import copy,hashlib,shutil,sys,struct
from PIL import Image,ImageDraw,ImageFont
from compile_translation import ROOT,read,write
from build_sample import run,FONT_TOOL
WORK=ROOT/'full_work/font_aligned_544'
def main():
    mapping=read(ROOT/'translation/font_encoding.hex.json');reports=[]
    for cfg in read(ROOT/'translation/feedback_543/font_alignment_prototype.json')['fonts']:
        name=cfg['font'];src=ROOT/'full_work/font_verify'/name
        m=read(src/f'{name}_manifest.json');old=read(ROOT/f'full_work/font_original/{name}/{name}_manifest.json')
        previous=copy.deepcopy(m);dst=WORK/'build'/name;dst.mkdir(parents=True,exist_ok=True)
        for p in src.glob('*.png'):shutil.copy2(p,dst/p.name)
        tx=m['textureInfo'];si=tx['sheetInfo'];cw=tx['glyph']['width']+1;ch=tx['glyph']['height']+1;per=si['cols']*si['rows']
        size=cfg['advance'];top,bottom=cfg['target_vertical_band'];st,sb=cfg['source_vertical_band']
        face=ImageFont.truetype(str(ROOT/'fonts/SourceHanSansSC-Medium.otf'),size*4)
        sheets={};changed={}
        for char,encoded in mapping.items():
            code=chr(int(encoded,16))
            if code in old['glyphMap'] or not '\u4e00'<=char<='\u9fff':continue
            index=m['glyphMap'][code];sheet,slot=divmod(index,per)
            if sheet not in sheets:sheets[sheet]=Image.open(dst/f'{name}_sheet{sheet}.png').convert('RGBA')
            high=Image.new('RGBA',(size*4,size*12));ImageDraw.Draw(high).text((0,size*4),char,font=face,anchor='ls',fill='white')
            bbox=high.getchannel('A').getbbox();assert bbox and bbox[1]>=size*4+st and bbox[3]<=size*4+sb,(name,char,'clipping',bbox)
            band=high.crop((0,size*4+st,size*4,size*4+sb))
            cell=Image.new('RGBA',(cw,ch));cell.paste(band.resize((size,bottom-top),Image.Resampling.LANCZOS),(0,top))
            x=slot%si['cols']*cw+1;y=slot//si['cols']*ch+2
            sheets[sheet].paste(cell,(x,y));m['glyphWidths'][str(index)]={'char':size,'glyph':size,'left':0};changed[index]=char
        for sheet,im in sheets.items():im.save(dst/f'{name}_sheet{sheet}.png')
        write(dst/f'{name}_manifest.json',m)
        target=WORK/'payload'/f'{name}.bcfnt';target.parent.mkdir(exist_ok=True)
        run([sys.executable,FONT_TOOL,'-c','-y','-f',target],dst)
        # The bundled writer writes every width but records end-1 in CWDH.
        # Repair that bounded header in this isolated output, not the shared tool.
        binary=bytearray(target.read_bytes());p=binary.index(b'CWDH')
        section,start,end,next_offset=struct.unpack_from('<IHHI',binary,p+4)
        last=max(map(int,m['glyphWidths']))
        assert start==0 and end==last-1 and section==16+3*(last+1) and next_offset==0
        struct.pack_into('<H',binary,p+10,last);target.write_bytes(binary)
        verify=WORK/'verify'/name;verify.mkdir(parents=True,exist_ok=True)
        run([sys.executable,FONT_TOOL,'-x','-y','-f',target],verify)
        after=read(verify/f'{name}_manifest.json');assert after['glyphMap']==previous['glyphMap']
        assert after['glyphWidths']==m['glyphWidths']
        cache={}
        for index in set(m['glyphMap'].values()):
            sheet,slot=divmod(index,per)
            if sheet not in cache:cache[sheet]=tuple(Image.open(p/f'{name}_sheet{sheet}.png').convert('RGBA') for p in [src,dst,verify])
            a,b,c=cache[sheet];x=slot%si['cols']*cw+1;y=slot//si['cols']*ch+2;box=(x,y,min(x+cw,si['width']),min(y+ch,si['height']))
            if index not in changed:assert a.crop(box).tobytes()==c.crop(box).tobytes(),(name,index,'unchanged glyph modified')
            # Alpha-only texture quantization is expected; verify visible ink exists and fits runtime width.
            else:
                ink=c.crop(box).getchannel('A').getbbox();assert ink and ink[2]<=size and ink[3]<=ch,(name,index,ink)
        reports.append(dict(font=name,changed_glyphs=len(changed),path=target.relative_to(ROOT).as_posix(),
            sha256=hashlib.sha256(target.read_bytes()).hexdigest(),encoding_sha256=hashlib.sha256((ROOT/'translation/font_encoding.hex.json').read_bytes()).hexdigest(),
            original_and_other_glyphs_preserved=True,glyph_map_unchanged=True,roundtrip_verified=True,clipping_checked=True,runtime_tested=False))
        write(ROOT/'translation/font_aligned_544.generated.json',reports);print('VERIFIED',name,len(changed),flush=True)
    assert len(reports)==6
if __name__=='__main__':main()
