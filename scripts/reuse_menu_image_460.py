"""Reuse an existing Chinese bitmap without pixel editing; isolated SPR3 trial."""
import hashlib
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path
from PIL import Image
from compile_translation import ROOT,write

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def visible(pixel):
    r,g,b,a=pixel
    return r*a,g*a,b*a,a

def differences(a,b):
    assert a.size==b.size
    return [(i%a.width,i//a.width) for i,(p,q) in enumerate(zip(a.getdata(),b.getdata())) if visible(p)!=visible(q)]

def main():
    rel=Path('camp/c_sub.spr3')
    original=ROOT/'data'/rel
    png=ROOT/'export_base'/(str(rel)+'.00.png')
    reference=ROOT.parent/'references/PersonaQ2ChsLocalization-latest-20260928/files/images'/ (str(rel)+'.00.png')
    a=Image.open(png).convert('RGBA'); b=Image.open(reference).convert('RGBA')
    delta=differences(a,b)
    assert delta and all(174<=x<=220 and 350<=y<=366 for x,y in delta)
    work=Path(tempfile.mkdtemp(prefix='image_460_',dir=ROOT/'full_work'))
    for folder in ['original','import']:(work/folder/'camp').mkdir(parents=True)
    shutil.copy2(original,work/'original'/rel)
    shutil.copy2(reference,work/'import'/(str(rel)+'.00.png'))
    dotnet=ROOT.parent/'tools/dotnet8/dotnet.exe'
    helper=ROOT.parent/'references/PersonaQ2ChsLocalization/bin/PersonaQ2ChsLocalizationHelper/PersonaQ2ChsLocalizationHelper/bin/Release/net8.0-windows/publish/PersonaQ2ChsLocalizationHelper.dll'
    subprocess.run([str(dotnet),str(helper),'import','-i',str(work/'original'),'-j',str(work/'import'),'-o',str(work/'payload')],check=True)
    result=work/'payload'/rel
    raw=original.read_bytes(); out=result.read_bytes()
    offset=struct.unpack_from('<I',raw,0x24)[0]
    imported_offset=struct.unpack_from('<I',out,0x24)[0]
    assert raw[offset:offset+4]==b'CTPK'
    assert out[imported_offset:imported_offset+4]==b'CTPK'
    # Helper normalizes away eight original alignment bytes. Preserve original
    # SPR3 header, offset and all entries; transplant only the rebuilt CTPK.
    assert raw[:0x24]==out[:0x24]
    assert raw[0x28:imported_offset]==out[0x28:imported_offset]
    assert not any(raw[imported_offset:offset])
    assert len(raw)-offset==len(out)-imported_offset
    out=raw[:offset]+out[imported_offset:]
    result.write_bytes(out)
    assert out[:offset]==raw[:offset], 'SPR3 crop/entry metadata changed'
    subprocess.run([str(dotnet),str(helper),'export','-i',str(work/'payload'),'-o',str(work/'readback')],check=True)
    c=Image.open(work/'readback'/(str(rel)+'.00.png')).convert('RGBA')
    error=differences(b,c)
    if error:
        changed=differences(a,c)
        write(ROOT/'translation/image_reuse_460.failed.json',dict(
            source=rel.as_posix(),trial=result.relative_to(ROOT).as_posix(),
            accepted=False,packaged=False,crop_metadata_preserved=True,
            import_visible_pixel_errors=len(error),changed_from_original=len(changed),
            outside_label_changed=sum(not (174<=x<=220 and 350<=y<=366) for x,y in changed),
            reason='Lossy texture recompression changes pixels outside the label; trial is NOT a deliverable.',
            next_step='Investigate original compression/block layout and preservation of unchanged blocks before acceptance.'))
    assert not error, f'Imported visible pixels differ: {len(error)}'
    assert sha(original)==sha(work/'original'/rel)
    write(ROOT/'translation/image_reuse_460.generated.json',dict(source=rel.as_posix(),source_sha256=sha(original),
      reference=str(reference),reference_sha256=sha(reference),output=result.relative_to(ROOT).as_posix(),sha256=sha(result),
      chinese_png=(work/'import'/(str(rel)+'.00.png')).relative_to(ROOT).as_posix(),
      visible_changed_pixels=len(delta),visible_change_bounds=[174,350,221,367],
      crop_metadata_preserved=True,decoded_pixels_verified=True,packaged=False,runtime_tested=False,
      notes='Reused existing Q2 menu label unchanged. Only intermediate SPR3 resource generated; no ROM/CPK/CIA rebuilt.'))
    print('Verified menu label reuse:',result)

if __name__=='__main__':main()
