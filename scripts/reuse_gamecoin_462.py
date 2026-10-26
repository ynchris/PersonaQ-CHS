"""Unedited Q2 bitmap reuse, original compressed blocks retained elsewhere."""
import shutil
import struct
import subprocess
import uuid
from pathlib import Path
from PIL import Image
from compile_translation import ROOT,write
from reuse_menu_image_460 import differences,sha
from patch_menu_blocks_461 import layout,block_offset

def main():
    rel=Path('gamecoin/game_coin.spr3')
    source=ROOT/'data'/rel
    reference=ROOT.parent/'references/PersonaQ2ChsLocalization-latest-20260928/files/images'/(str(rel)+'.00.png')
    original_png=ROOT/'export_base'/(str(rel)+'.00.png')
    a=Image.open(original_png).convert('RGBA'); b=Image.open(reference).convert('RGBA')
    delta=differences(a,b)
    assert delta and all(24<=x<=89 and 40<=y<=51 for x,y in delta)
    work=ROOT/'full_work'/('image_462_'+uuid.uuid4().hex[:8])
    for name in ['source','import','payload']:(work/name/rel.parent).mkdir(parents=True,exist_ok=False)
    shutil.copy2(source,work/'source'/rel)
    shutil.copy2(reference,work/'import'/(str(rel)+'.00.png'))
    dotnet=ROOT.parent/'tools/dotnet8/dotnet.exe'
    helper=ROOT.parent/'references/PersonaQ2ChsLocalization/bin/PersonaQ2ChsLocalizationHelper/PersonaQ2ChsLocalizationHelper/bin/Release/net8.0-windows/publish/PersonaQ2ChsLocalizationHelper.dll'
    def run(*args):subprocess.run([str(dotnet),str(helper),*map(str,args)],check=True)
    run('import','-i',work/'source','-j',work/'import','-o',work/'trial')
    run('export','-i',work/'trial','-o',work/'trial_readback')
    raw=source.read_bytes(); encoded=(work/'trial'/rel).read_bytes()
    start,w,h=layout(raw); imported_start,iw,ih=layout(encoded)
    assert (w,h)==(iw,ih)==a.size
    blocks={(x//4*4,y//4*4) for x,y in delta}
    out=bytearray(raw);allowed=set()
    for x,y in blocks:
        offset=block_offset(x,y,w)
        out[start+offset:start+offset+16]=encoded[imported_start+offset:imported_start+offset+16]
        allowed.update(range(start+offset,start+offset+16))
    assert len(out)==len(raw) and out[:start]==raw[:start]
    assert all(p==q or i in allowed for i,(p,q) in enumerate(zip(raw,out)))
    output=work/'payload'/rel;output.write_bytes(out)
    run('export','-i',work/'payload','-o',work/'readback')
    preview=work/'readback'/(str(rel)+'.00.png')
    c=Image.open(preview).convert('RGBA')
    trial=Image.open(work/'trial_readback'/(str(rel)+'.00.png')).convert('RGBA')
    assert all((x//4*4,y//4*4) in blocks for x,y in differences(a,c))
    for x,y in blocks:
        for j in range(y,y+4):
            for i in range(x,x+4):assert c.getpixel((i,j))==trial.getpixel((i,j))
    write(ROOT/'translation/image_gamecoin_462.generated.json',dict(source=rel.as_posix(),source_sha256=sha(source),
         reference=str(reference),reference_sha256=sha(reference),output=output.relative_to(ROOT).as_posix(),sha256=sha(output),
         preview=preview.relative_to(ROOT).as_posix(),blocks=sorted(blocks),
         metadata_preserved=True,all_other_bytes_preserved=True,pixels_outside_blocks_preserved=True,
         visual_review_pending=True,runtime_tested=False,packaged=False))
    print('Preview:',preview)

if __name__=='__main__':main()
