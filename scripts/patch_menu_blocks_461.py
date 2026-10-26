"""Copy only changed ETC1A4 blocks from the existing Q2-label import trial."""
import hashlib
import struct
import subprocess
import tempfile
from pathlib import Path
from PIL import Image
from compile_translation import ROOT,read,write
from reuse_menu_image_460 import differences,sha

def layout(raw):
    offset=struct.unpack_from('<I',raw,36)[0]
    assert raw[offset:offset+4]==b'CTPK'
    assert struct.unpack_from('<H',raw,offset+6)[0]==1
    section,size=struct.unpack_from('<II',raw,offset+8)
    entry=offset+32
    data_size,relative,fmt,width,height,mips=struct.unpack_from('<IIIHHB',raw,entry+4)
    assert fmt==13 and width%8==height%8==0 and mips==1
    assert data_size==size==width*height
    start=offset+section+relative
    assert start+size==len(raw)
    return start,width,height

def block_offset(x,y,width):
    # 8x8 tiles in row order; four Morton-ordered 4x4 ETC1A4 blocks per tile.
    return ((y//8)*(width//8)+x//8)*64+((y%8)//4*2+(x%8)//4)*16

def main():
    rel=Path('camp/c_sub.spr3')
    original=ROOT/'data'/rel
    prior=read(ROOT/'translation/image_reuse_460.failed.json')
    trial=ROOT/prior['trial']
    raw=original.read_bytes(); imported=trial.read_bytes()
    start,width,height=layout(raw)
    assert layout(imported)==(start,width,height)
    a=Image.open(ROOT/'export_base'/(str(rel)+'.00.png')).convert('RGBA')
    target_path=trial.parents[2]/'import'/(str(rel)+'.00.png')
    target=Image.open(target_path).convert('RGBA')
    delta=differences(a,target)
    assert all(174<=x<=220 and 350<=y<=366 for x,y in delta)
    blocks={(x//4*4,y//4*4) for x,y in delta}
    out=bytearray(raw); allowed=set()
    for x,y in blocks:
        pos=start+block_offset(x,y,width)
        out[pos:pos+16]=imported[pos:pos+16]
        allowed.update(range(pos,pos+16))
    assert all(x==y or i in allowed for i,(x,y) in enumerate(zip(raw,out)))
    assert out[:start]==raw[:start]
    work=Path(tempfile.mkdtemp(prefix='image_461_',dir=ROOT/'full_work'))
    result=work/'payload'/rel; result.parent.mkdir(parents=True); result.write_bytes(out)
    dotnet=ROOT.parent/'tools/dotnet8/dotnet.exe'
    helper=ROOT.parent/'references/PersonaQ2ChsLocalization/bin/PersonaQ2ChsLocalizationHelper/PersonaQ2ChsLocalizationHelper/bin/Release/net8.0-windows/publish/PersonaQ2ChsLocalizationHelper.dll'
    subprocess.run([str(dotnet),str(helper),'export','-i',str(work/'payload'),'-o',str(work/'readback')],check=True)
    c=Image.open(work/'readback'/(str(rel)+'.00.png')).convert('RGBA')
    full=Image.open(trial.parents[2]/'readback'/(str(rel)+'.00.png')).convert('RGBA')
    changed=differences(a,c)
    assert changed
    assert all((x//4*4,y//4*4) in blocks for x,y in changed), 'Block coordinate mapping mismatch'
    for x,y in blocks:
        for j in range(y,y+4):
            for i in range(x,x+4):assert c.getpixel((i,j))==full.getpixel((i,j))
    write(ROOT/'translation/image_blocks_461.generated.json',dict(source=rel.as_posix(),source_sha256=sha(original),
        output=result.relative_to(ROOT).as_posix(),sha256=sha(result),readback=(work/'readback'/(str(rel)+'.00.png')).relative_to(ROOT).as_posix(),
        target_png=str(target_path),target_sha256=sha(target_path),blocks=sorted(blocks),
        preserved_all_other_bytes=True,preserved_pixels_outside_blocks=True,
        modified_blocks_match_import=True,lossy_encoding_inside_blocks=True,
        runtime_tested=False,packaged=False,visual_review_pending=True))
    print('Blocks:',len(blocks),'readback:',work/'readback'/(str(rel)+'.00.png'))

if __name__=='__main__':main()
