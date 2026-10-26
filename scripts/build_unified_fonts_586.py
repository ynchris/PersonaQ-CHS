"""586: redraw all CJK glyphs of the six BCFNTs with one face; isolated output, not activated."""
import copy,hashlib,shutil,struct,sys
from PIL import Image
from font_unify_586 import ROOT,FONTS,read,is_cjk,code_char,original_target,render_cell,faces
from compile_translation import write
from build_sample import run,FONT_TOOL
WORK=ROOT/'full_work/font_unified_586'
def main():
    mapping=read(ROOT/'translation/font_encoding.hex.json')
    reverse={chr(int(v,16)):k for k,v in mapping.items()}
    reports=[]
    for name in FONTS:
        src=ROOT/'full_work/font_aligned_544/verify'/name
        m=read(src/f'{name}_manifest.json');previous=copy.deepcopy(m)
        dst=WORK/'build'/name;dst.mkdir(parents=True,exist_ok=True)
        for p in src.glob('*.png'):shutil.copy2(p,dst/p.name)
        tx=m['textureInfo'];si=tx['sheetInfo'];cw=tx['glyph']['width']+1;ch=tx['glyph']['height']+1;per=si['cols']*si['rows']
        target,_=original_target(name)
        sheets={};changed={};fallback=[];kept=[]
        for code,index in m['glyphMap'].items():
            char=reverse.get(code) or code_char(code)
            if not is_cjk(char):continue
            mapped=code in reverse
            if not mapped and not faces()[0].has(char):kept.append(char);continue  # untranslated JP-only kanji: original pixels
            cell,primary=render_cell(char,target,(cw,ch))
            if not primary:fallback.append(char)
            assert cell.getchannel('A').getbbox(),(name,char)
            sheet,slot=divmod(index,per)
            if sheet not in sheets:sheets[sheet]=Image.open(dst/f'{name}_sheet{sheet}.png').convert('RGBA')
            x=slot%si['cols']*cw+1;y=slot//si['cols']*ch+2
            sheets[sheet].paste(cell,(x,y));changed[index]=char
        for sheet,im in sheets.items():im.save(dst/f'{name}_sheet{sheet}.png')
        write(dst/f'{name}_manifest.json',m)
        target_path=WORK/'payload'/f'{name}.bcfnt';target_path.parent.mkdir(parents=True,exist_ok=True)
        run([sys.executable,FONT_TOOL,'-c','-y','-f',target_path],dst)
        # Same bounded CWDH end-index repair as 544 (bundled writer records end-1).
        binary=bytearray(target_path.read_bytes());p=binary.index(b'CWDH')
        section,start,end,next_offset=struct.unpack_from('<IHHI',binary,p+4)
        last=max(map(int,m['glyphWidths']))
        assert start==0 and end==last-1 and section==16+3*(last+1) and next_offset==0
        struct.pack_into('<H',binary,p+10,last);target_path.write_bytes(binary)
        verify=WORK/'verify'/name;verify.mkdir(parents=True,exist_ok=True)
        run([sys.executable,FONT_TOOL,'-x','-y','-f',target_path],verify)
        after=read(verify/f'{name}_manifest.json')
        assert after['glyphMap']==previous['glyphMap'] and after['glyphWidths']==previous['glyphWidths']
        cache={}
        for index in set(m['glyphMap'].values()):
            sheet,slot=divmod(index,per)
            if sheet not in cache:cache[sheet]=tuple(Image.open(d/f'{name}_sheet{sheet}.png').convert('RGBA') for d in [src,verify])
            a,c=cache[sheet];x=slot%si['cols']*cw+1;y=slot//si['cols']*ch+2;box=(x,y,min(x+cw,si['width']),min(y+ch,si['height']))
            if index not in changed:assert a.crop(box).tobytes()==c.crop(box).tobytes(),(name,index,'non-CJK glyph modified')
            else:assert c.crop(box).getchannel('A').getbbox(),(name,index,'empty')
        reports.append(dict(font=name,redrawn_glyphs=len(changed),fallback_face_glyphs=''.join(sorted(set(fallback))),
            unmapped_kanji_kept_original=len(kept),target_ink_box=target,path=target_path.relative_to(ROOT).as_posix(),
            sha256=hashlib.sha256(target_path.read_bytes()).hexdigest(),
            encoding_sha256=hashlib.sha256((ROOT/'translation/font_encoding.hex.json').read_bytes()).hexdigest(),
            glyph_map_unchanged=True,widths_unchanged=True,non_cjk_pixels_preserved=True,roundtrip_verified=True,activated=False,runtime_tested=False))
        write(ROOT/'translation/font_unified_586.generated.json',reports);print('VERIFIED',name,len(changed),'fallback',''.join(sorted(set(fallback))),'kept',len(kept),flush=True)
    assert len(reports)==6
if __name__=='__main__':main()
