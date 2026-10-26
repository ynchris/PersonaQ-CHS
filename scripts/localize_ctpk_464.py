"""Deterministic, user-authorized caption edits and block-preserving CTPK import."""
import struct,subprocess,uuid,shutil
from PIL import Image,ImageDraw,ImageFont
from compile_translation import ROOT,write
from reuse_menu_image_460 import differences,sha
from patch_menu_blocks_461 import block_offset

SPECS={
'title/fiction.ctpk':[
 ((58,88,342,156),['本故事纯属虚构，','与实际人物、团体、地名、事件等','均无任何关联。'],(0,0,0,255),(210,210,210,255),12,23,True)],
'tutorial/t043.ctpk':[
 ((31,17,98,31),['L/R键'],(255,255,255,255),(238,0,102,255),12,14,False),
 ((102,17,170,31),['左右平移'],(255,255,255,255),(0,0,0,255),12,14,False),
 ((30,131,220,165),[],(255,255,255,255),(0,0,0,255),12,16,False),
 ((31,132,98,148),['方向键上下'],(255,255,255,255),(0,150,240,255),12,16,False),
 ((102,132,220,148),['前进／后退'],(255,255,255,255),(0,0,0,255),12,16,False),
 ((31,150,98,165),['方向键左右'],(255,255,255,255),(0,150,240,255),12,15,False),
 ((102,150,220,165),['转向'],(255,255,255,255),(0,0,0,255),12,15,False)],
'tutorial/t044.ctpk':[
 ((18,112,276,168),[],(255,255,255,255),(0,0,0,255),12,16,False),
 ((19,113,121,129),['B键＋方向键上下'],(255,255,255,255),(0,145,230,255),12,16,False),
 ((19,133,121,148),['B键＋L/R键'],(255,255,255,255),(0,145,230,255),12,15,False),
 ((138,122,217,139),['快速移动'],(255,255,255,255),(0,0,0,255),12,17,False),
 ((19,152,87,168),['B键＋摇杆'],(255,255,255,255),(65,140,0,255),12,16,False),
 ((95,152,163,168),['环视'],(255,255,255,255),(0,0,0,255),12,16,False)]}

def layout(b):
    assert b[:4]==b'CTPK' and struct.unpack_from('<H',b,6)[0]==1
    start,size=struct.unpack_from('<II',b,8)
    length,offset,fmt,w,h,mips=struct.unpack_from('<IIIHHB',b,36)
    assert fmt in (12,13) and mips==1 and w%8==h%8==0
    blockbytes=8 if fmt==12 else 16
    assert length==size==w*h*blockbytes//16 and start+offset+size==len(b)
    return start+offset,w,h,blockbytes

def main():
    work=ROOT/'full_work'/('images_464_'+uuid.uuid4().hex[:8]);files=[]
    dotnet=ROOT.parent/'tools/dotnet8/dotnet.exe'
    helper=ROOT.parent/'references/PersonaQ2ChsLocalization/bin/PersonaQ2ChsLocalizationHelper/PersonaQ2ChsLocalizationHelper/bin/Release/net8.0-windows/publish/PersonaQ2ChsLocalizationHelper.dll'
    for rel,spec in SPECS.items():
        source=ROOT/'data'/rel; raw=source.read_bytes();start,w,h,bs=layout(raw)
        original=Image.open(ROOT/'export_base'/(rel+'.00.png')).convert('RGBA'); image=original.copy()
        for box,lines,bg,fg,size,leading,center in spec:
            x,y,r,b=box;scale=4
            patch=Image.new('RGBA',((r-x)*scale,(b-y)*scale),bg);draw=ImageDraw.Draw(patch)
            font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',size*scale)
            for i,line in enumerate(lines):
                width=draw.textlength(line,font=font);assert width<patch.width
                draw.text(((patch.width-width)/2 if center else 0,(i*leading+2)*scale),line,font=font,fill=fg,anchor='lt')
            image.paste(patch.resize((r-x,b-y),Image.Resampling.LANCZOS),(x,y))
        if rel=='tutorial/t044.ctpk':
            draw=ImageDraw.Draw(image)
            draw.line([(123,120),(130,120),(130,143),(123,143)],fill=(0,0,0,255),width=1)
        delta=differences(original,image);assert delta
        for folder in ['source','import','payload']:(work/folder/source.relative_to(ROOT/'data').parent).mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,work/'source'/rel);image.save(work/'import'/(rel+'.00.png'))
    def run(*args):subprocess.run([str(dotnet),str(helper),*map(str,args)],check=True)
    run('import','-i',work/'source','-j',work/'import','-o',work/'trial')
    for rel,spec in SPECS.items():
        source=ROOT/'data'/rel;raw=source.read_bytes();encoded=(work/'trial'/rel).read_bytes()
        start,w,h,bs=layout(raw);ins,iw,ih,ibs=layout(encoded);assert (w,h,bs)==(iw,ih,ibs)
        a=Image.open(ROOT/'export_base'/(rel+'.00.png')).convert('RGBA');b=Image.open(work/'import'/(rel+'.00.png')).convert('RGBA')
        blocks={(x//4*4,y//4*4) for x,y in differences(a,b)}
        out=bytearray(raw);allowed=set()
        for x,y in blocks:
            off=block_offset(x,y,w)*bs//16
            out[start+off:start+off+bs]=encoded[ins+off:ins+off+bs];allowed.update(range(start+off,start+off+bs))
        assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,out)))
        dest=work/'payload'/rel;dest.write_bytes(out)
        files.append(dict(source=rel,source_sha256=sha(source),output=dest.relative_to(ROOT).as_posix(),sha256=sha(dest),blocks=sorted(blocks),
                          translations=[s[1] for s in spec],preview=(work/'readback'/(rel+'.00.png')).relative_to(ROOT).as_posix()))
    run('export','-i',work/'payload','-o',work/'readback')
    for f in files:
        a=Image.open(ROOT/'export_base'/(f['source']+'.00.png')).convert('RGBA');b=Image.open(ROOT/f['preview']).convert('RGBA');blocks={tuple(p) for p in f['blocks']}
        assert all((x//4*4,y//4*4) in blocks for x,y in differences(a,b))
    write(ROOT/'translation/images_464.generated.json',dict(files=files,metadata_and_nonselected_blocks_preserved=True,
          pixels_outside_blocks_preserved=True,packaged=False,runtime_tested=False,visual_review_pending=True))
    print('Previews:',[f['preview'] for f in files])

if __name__=='__main__':main()
