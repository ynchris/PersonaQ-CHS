"""Encode explicitly approved PNGs; preserve untouched ETC blocks and members."""
import hashlib
import json
import re
import shutil
import struct
import subprocess
from pathlib import Path
from PIL import Image
from check_roundtrip import parse_members
from localize_ctpk_464 import layout
from patch_menu_blocks_461 import block_offset
from caution_tmx_463 import decode

ROOT=Path(__file__).resolve().parent
WORK=ROOT/'full_work/images_540'
DOTNET=ROOT.parent/'tools/dotnet8/dotnet.exe'
HELPER=ROOT.parent/'references/PersonaQ2ChsLocalization/bin/PersonaQ2ChsLocalizationHelper/PersonaQ2ChsLocalizationHelper/bin/Release/net8.0-windows/publish/PersonaQ2ChsLocalizationHelper.dll'

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def pack(parts):
    return struct.pack('<I',len(parts))+b''.join(n.encode().ljust(32,b'\0')+struct.pack('<I',len(b))+b for n,b in parts)

def resolve(export):
    rel=export.replace('\\','/').removeprefix('export_base/').removesuffix('.00.png')
    if (ROOT/'data'/rel).is_file(): return rel,None
    m=re.match(r'^(.*?\.(?:bin|arc))_(.*)$',rel)
    assert m and (ROOT/'data'/m[1]).is_file(),rel
    return m[1],m[2]

def selections():
    rows=read(ROOT/'translation/image_selection_515.json')['files']
    batches={467:[43],466:[44],468:[2,6],469:[29,35,37],470:[36,25],471:[34],
             472:[7,8,32,33,23,24],474:[10,11,12],475:[20],477:[38],479:[4,30],
             482:[27],484:[26],485:[22]}
    for batch,ids in batches.items():
        review=read(ROOT/f'translation/previews_{batch}/review.json')
        for n in ids:
            png=f'translation/previews_{batch}/t{n:03}.ctpk.00.png'
            digest=sha(ROOT/png)
            approval=read(ROOT/'translation/previews_468/prior_approvals.json') if batch in (466,467) else review
            assert digest in json.dumps(approval),png
            rows.append(dict(source=f'export_base/tutorial/t{n:03}.ctpk.00.png',png=png,sha256=digest))
    assert len(rows)==67
    return rows

def run(mode,src,dst,png=None):
    args=[str(DOTNET),str(HELPER),mode,'-i',str(src),'-o',str(dst)]
    if png: args+=['-j',str(png)]
    with (WORK/(mode+'.log')).open('wb') as log:
        subprocess.run(args,stdout=log,stderr=subprocess.STDOUT,check=True)

def main():
    rows=selections()
    for name in ['source','png','encoded','readback','payload']:(WORK/name).mkdir(parents=True,exist_ok=True)
    for i,row in enumerate(rows):
        assert sha(ROOT/row['png'])==row['sha256']
        container,member=resolve(row['source'])
        raw=(ROOT/'data'/container).read_bytes()
        if member: raw=dict(parse_members(raw))[member]
        off=0 if raw.startswith(b'CTPK') else struct.unpack_from('<I',raw,36)[0]
        assert raw[off:off+4]==b'CTPK'
        section,size=struct.unpack_from('<II',raw,off+8)
        ctpk=raw[off:off+section+size]
        start,w,h,bs=layout(ctpk)
        with Image.open(ROOT/row['png']) as im: assert im.size==(w,h)
        unit=f'{i:03}.ctpk'
        (WORK/'source'/unit).write_bytes(ctpk)
        shutil.copy2(ROOT/row['png'],WORK/'png'/(unit+'.00.png'))
        row.update(container=container,member=member,texture_offset=off,unit=unit)
    print('Encoding',len(rows),'approved textures',flush=True)
    run('import',WORK/'source',WORK/'trial',WORK/'png')
    containers={}
    for row in rows:
        unit=row['unit'];original=(WORK/'source'/unit).read_bytes();encoded=(WORK/'trial'/unit).read_bytes()
        start,w,h,bs=layout(original);es,ew,eh,ebs=layout(encoded)
        assert (w,h,bs)==(ew,eh,ebs)
        a=Image.open(ROOT/row['source']).convert('RGBA');b=Image.open(ROOT/row['png']).convert('RGBA')
        blocks={(i%w//4*4,i//w//4*4) for i,(x,y) in enumerate(zip(a.getdata(),b.getdata())) if x!=y}
        out=bytearray(original)
        for x,y in blocks:
            p=block_offset(x,y,w)*bs//16
            out[start+p:start+p+bs]=encoded[es+p:es+p+bs]
        assert out[:start]==original[:start]
        (WORK/'encoded'/unit).write_bytes(out)
        row['blocks']=[list(p) for p in sorted(blocks)]
        rel=row['container']
        current=containers.get(rel,(ROOT/'data'/rel).read_bytes())
        off=row['texture_offset']
        if row['member']:
            parts=parse_members(current)
            parts=[(n,b[:off]+bytes(out)+b[off+len(out):] if n==row['member'] else b) for n,b in parts]
            current=pack(parts)
        else: current=current[:off]+bytes(out)+current[off+len(out):]
        containers[rel]=current
    run('export',WORK/'encoded',WORK/'readback')
    for row in rows:
        a=Image.open(ROOT/row['source']).convert('RGBA')
        b=Image.open(WORK/'readback'/(row['unit']+'.00.png')).convert('RGBA')
        blocks={tuple(p) for p in row['blocks']};w=a.width
        assert all(x==y or (i%w//4*4,i//w//4*4) in blocks for i,(x,y) in enumerate(zip(a.getdata(),b.getdata()))),row['source']
        row['readback']=str((WORK/'readback'/(row['unit']+'.00.png')).relative_to(ROOT))
    # Fiction was explicitly approved from its decoded 464 output. Reuse the
    # exact already-encoded bytes, avoiding a second lossy recompression.
    fiction=next(r for r in read(ROOT/'translation/images_464.generated.json')['files'] if r['source']=='title/fiction.ctpk')
    assert sha(ROOT/fiction['output'])==fiction['sha256']
    containers['title/fiction.ctpk']=(ROOT/fiction['output']).read_bytes()
    # Latest approved TMX: retain palette, dimensions, headers and sibling logos.
    approval=read(ROOT/'translation/previews_527/review.json')
    assert approval['status']=='approved_by_user' and sha(ROOT/approval['png'])==approval['sha256']
    parts=parse_members((ROOT/'data/title/logo.bin').read_bytes())
    original=dict(parts)['caution.tmx'];a,palette=decode(original)
    target=Image.open(ROOT/approval['png']).convert('RGBA')
    assert target.size==a.size
    assert all(r==g==b and alpha==255 for r,g,b,alpha in palette)
    nearest={v:min(range(256),key=lambda j:abs(palette[j][0]-v)) for v in range(256)}
    out=bytearray(original)
    for i,(old,new) in enumerate(zip(a.getdata(),target.getdata())):
        if old!=new:
            assert new[0]==new[1]==new[2] and new[3]==255
            out[1088+i]=nearest[new[0]]
    decoded,_=decode(out)
    decoded.save(WORK/'readback/caution.png')
    assert out[:1088]==original[:1088]
    containers['title/logo.bin']=pack([(n,bytes(out) if n=='caution.tmx' else b) for n,b in parts])
    files=[]
    for rel,blob in containers.items():
        p=WORK/'payload'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(blob)
        files.append(dict(file=rel,output=str(p.relative_to(ROOT)),sha256=sha(p),source_sha256=sha(ROOT/'data'/rel)))
    report=dict(files=files,textures=rows,ctpk_count=68,tmx_count=1,untouched_blocks_verified=True,original_data_modified=False)
    (ROOT/'translation/build_540/images.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Verified image encoding:',len(files),'containers; 68 CTPK + 1 TMX.',flush=True)

if __name__=='__main__':main()
