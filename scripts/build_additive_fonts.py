"""Build draft fonts by appending missing glyphs, preserving original pixels."""
import copy
import argparse
import hashlib
import math
import shutil
import struct
import sys
from pathlib import Path
from build_sample import run, FONT_TOOL
from compile_translation import read, write

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'tools/pq_python_deps'))
from PIL import Image, ImageDraw, ImageFont

def unicode_coverage(path):
    """Read the supplied CJK OTF's format-12 cmap without external parsers."""
    data=path.read_bytes()
    count=struct.unpack_from('>H',data,4)[0]
    cmap_offset=None
    for i in range(count):
        tag,checksum,offset,size=struct.unpack_from('>4sIII',data,12+16*i)
        if tag==b'cmap':
            cmap_offset=offset
            break
    if cmap_offset is None:
        raise ValueError('Source OTF has no cmap')
    count=struct.unpack_from('>H',data,cmap_offset+2)[0]
    covered=set()
    for i in range(count):
        platform,encoding,offset=struct.unpack_from('>HHI',data,cmap_offset+4+8*i)
        start=cmap_offset+offset
        if platform not in (0,3) or struct.unpack_from('>H',data,start)[0]!=12:
            continue
        groups=struct.unpack_from('>I',data,start+12)[0]
        for j in range(groups):
            first,last,glyph=struct.unpack_from('>III',data,start+16+12*j)
            covered.update(range(first+(glyph==0),last+1))
    if not covered:
        raise ValueError('Source OTF needs a Unicode format-12 cmap')
    return covered

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--raw-trial', action='store_true', help='Build isolated experimental byte-addressed fonts')
    args=parser.parse_args()
    work=ROOT/'full_work/raw_font_trial' if args.raw_trial else ROOT/'full_work'
    encoding_path=work/'encoding.hex.json' if args.raw_trial else ROOT/'translation/font_encoding.hex.json'
    encoding=read(encoding_path)
    fontpath=ROOT/'fonts/SourceHanSansSC-Medium.otf'
    cmap=unicode_coverage(fontpath)
    report=[]
    for source in sorted((ROOT/'data/font').glob('*.bcfnt')):
        if source.stem=='demo_font':
            continue
        name=source.stem
        original=work/'font_original'/name
        original.mkdir(parents=True,exist_ok=True)
        run([sys.executable,FONT_TOOL,'-x','-y','-f',source],original)
        manifest=read(original/f'{name}_manifest.json')
        baseline=copy.deepcopy(manifest)
        directory=work/'font_build'/name
        directory.mkdir(parents=True,exist_ok=True)
        for path in original.glob('*.png'):
            shutil.copy2(path,directory/path.name)
        info=manifest['textureInfo']
        si=info['sheetInfo']
        cols,rows=si['cols'],si['rows']
        per=cols*rows
        cw,ch=info['glyph']['width']+1,info['glyph']['height']+1
        size=max(8,manifest['fontInfo']['width']-1)
        face=ImageFont.truetype(str(fontpath),size*4)
        next_index=max(manifest['glyphMap'].values())+1
        sheets={}
        added=[]
        for char,encoded in sorted(encoding.items()):
            code=chr(int.from_bytes(bytes.fromhex(encoded),'big'))
            if code in manifest['glyphMap']:
                continue
            if ord(char) not in cmap:
                raise ValueError(f'Source font lacks {char!r}')
            index=next_index
            next_index+=1
            sheetno,slot=divmod(index,per)
            if sheetno not in sheets:
                path=directory/f'{name}_sheet{sheetno}.png'
                sheets[sheetno]=Image.open(path).convert('RGBA') if path.exists() and sheetno<baseline['textureInfo']['sheetCount'] else Image.new('RGBA',(si['width'],si['height']))
            glyph=Image.new('RGBA',(cw*4,ch*4))
            ImageDraw.Draw(glyph).text((0,(manifest['fontInfo']['ascent']+0.5)*4),char,font=face,fill='white',anchor='ls')
            glyph=glyph.resize((cw,ch),Image.Resampling.LANCZOS)
            if glyph.getbbox() is None and not char.isspace():
                raise ValueError(f'Empty rendered glyph: {char!r}')
            x,y=(slot%cols)*cw+1,(slot//cols)*ch+2
            sheets[sheetno].paste(glyph,(x,y))
            manifest['glyphMap'][code]=index
            manifest['glyphWidths'][str(index)]={'char':size,'glyph':size,'left':0}
            added.append(char)
        manifest['textureInfo']['sheetCount']=math.ceil(next_index/per)
        for no,sheet in sheets.items():
            sheet.save(directory/f'{name}_sheet{no}.png')
        for code,index in baseline['glyphMap'].items():
            assert manifest['glyphMap'][code]==index
        write(directory/f'{name}_manifest.json',manifest)
        payload=work/'font_payload'/source.name
        payload.parent.mkdir(parents=True,exist_ok=True)
        run([sys.executable,FONT_TOOL,'-c','-y','-f',payload],directory)
        verify=work/'font_verify'/name
        verify.mkdir(parents=True,exist_ok=True)
        run([sys.executable,FONT_TOOL,'-x','-y','-f',payload],verify)
        roundtrip=read(verify/f'{name}_manifest.json')
        assert roundtrip['glyphMap']==manifest['glyphMap']
        # Verify original glyph cell pixels survive rebuilding/texture encoding.
        cache={}
        for index in set(baseline['glyphMap'].values()):
            sheetno,slot=divmod(index,per)
            if sheetno not in cache:
                cache[sheetno]=(Image.open(original/f'{name}_sheet{sheetno}.png').convert('RGBA'),Image.open(verify/f'{name}_sheet{sheetno}.png').convert('RGBA'))
            x,y=(slot%cols)*cw+1,(slot//cols)*ch+2
            box=(x,y,min(x+cw,si['width']),min(y+ch,si['height']))
            a,b=cache[sheetno]
            assert a.crop(box).tobytes()==b.crop(box).tobytes(),f'Original glyph pixels changed: {name}:{index}'
        report.append(dict(font=name,added=len(added),missing=[],bytes=payload.stat().st_size,sha256=hashlib.sha256(payload.read_bytes()).hexdigest(),encoding_sha256=hashlib.sha256(encoding_path.read_bytes()).hexdigest(),original_pixels_preserved=True,roundtrip_verified=True,runtime_tested=False))
    write(work/'font_build.generated.json' if args.raw_trial else ROOT/'translation/font_build.generated.json',report)
    print(report)
    if not args.raw_trial and (ROOT/'translation/font_aligned_544.generated.json').exists():
        from build_aligned_fonts_544 import main as align_fonts
        from activate_fonts_544 import main as select_aligned_fonts
        align_fonts()
        select_aligned_fonts()

if __name__=='__main__':
    main()
