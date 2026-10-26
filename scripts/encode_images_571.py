"""Merge seven approved atlases and Seneca texture, preserving all other bytes."""
import hashlib,json,shutil,struct,sys
from pathlib import Path
from PIL import Image
import encode_images_540 as base
from check_roundtrip import parse_members
from localize_ctpk_464 import layout
from patch_menu_blocks_461 import block_offset
ROOT=Path(__file__).resolve().parent
WORK=ROOT/'full_work/images_571'
REPORT=ROOT/'translation/build_569/images.json'
base.WORK=WORK
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def cgfx_entries(bam):
    model=struct.unpack_from('<I',bam,0x14)[0]+0x80
    assert bam[model:model+4]==b'CGFX'
    b=bam[model:];ptr=40
    dictionary=ptr+struct.unpack_from('<I',b,ptr)[0]
    assert b[dictionary:dictionary+4]==b'DICT'
    count=struct.unpack_from('<I',b,dictionary+8)[0]
    rows=[]
    for i in range(count):
        p=dictionary+28+i*16+12
        t=p+struct.unpack_from('<I',b,p)[0]
        assert b[t+4:t+8]==b'TXOB'
        h,w=struct.unpack_from('<II',b,t+24)
        mips=struct.unpack_from('<I',b,t+40)[0]
        fmt=struct.unpack_from('<I',b,t+52)[0]
        user,usize=struct.unpack_from('<I',b,t+20)[0],struct.unpack_from('<I',b,t+56)[0]
        p=t+56+usize if user and usize>4 else t+60
        h2,w2,size,rel=struct.unpack_from('<IIII',b,p)
        start=model+p+12+rel
        assert (h,w)==(h2,w2) and mips in (0,1)
        rows.append(dict(index=i,width=w,height=h,format=fmt,offset=start,bytes=size))
    return rows
def changed_blocks(a,b):
    w=a.width
    return {(i%w//4*4,i//w//4*4) for i,(x,y) in enumerate(zip(a.getdata(),b.getdata())) if x!=y}
def main():
    for name in ['source','png','trial','encoded','readback','payload','quote_source','quote_png','quote_trial','quote_readback','quote_final']:(WORK/name).mkdir(parents=True,exist_ok=True)
    rows=read(ROOT/'translation/preflight_562/image_selection.json')['files']
    old=read(ROOT/'translation/build_540/images.json')
    containers={r['file']:(ROOT/r['output']).read_bytes() for r in old['files']}
    for r in old['files']:assert sha(containers[r['file']])==r['sha256'] and sha((ROOT/'data'/r['file']).read_bytes())==r['source_sha256']
    for i,row in enumerate(rows):
        assert sha((ROOT/row['png']).read_bytes())==row['sha256']
        raw=(ROOT/'data'/row['container']).read_bytes();off=row['texture_offset']
        ctpk=raw[off:off+row['texture_bytes']];layout(ctpk)
        unit=f'{i:02}.ctpk';row['unit']=unit
        (WORK/'source'/unit).write_bytes(ctpk)
        shutil.copy2(ROOT/row['png'],WORK/'png'/(unit+'.00.png'))
    # Locate exactly the quote texture in the original BAM, not by raw magic search.
    rel='event/model/e020_001.pac';pac=(ROOT/'data'/rel).read_bytes()
    parts=parse_members(pac);bam=dict(parts)['e020_001.bam'];entries=cgfx_entries(bam)
    print('Seneca model texture entries:',entries,flush=True)
    q=entries[4];assert (q['width'],q['height'])==(512,256)
    write(WORK/'quote_layout.json',dict(source=rel,member='e020_001.bam',textures=entries))
    approval_path=ROOT/'translation/previews_570/review.json';approval=read(approval_path)
    assert sha((ROOT/approval['output']).read_bytes())==approval['sha256']
    approval.update(status='approved_by_user',approval_note='用户确认570字号及分行字距后授权继续整合。')
    write(approval_path,approval)
    (WORK/'quote_source/e020_001.pac').write_bytes(pac)
    shutil.copy2(ROOT/approval['output'],WORK/'quote_png/e020_001.pac_e020_001.bam_model.04.png')
    base.run('import',WORK/'source',WORK/'trial',WORK/'png')
    for row in rows:
        unit=row['unit'];original=(WORK/'source'/unit).read_bytes();trial=(WORK/'trial'/unit).read_bytes()
        start,w,h,bs=layout(original);es,ew,eh,ebs=layout(trial);assert (w,h,bs)==(ew,eh,ebs)
        a=Image.open(ROOT/row['source']).convert('RGBA');b=Image.open(ROOT/row['png']).convert('RGBA')
        assert a.size==b.size==(w,h)
        blocks=changed_blocks(a,b);encoded=bytearray(original)
        for x,y in blocks:
            p=block_offset(x,y,w)*bs//16
            encoded[start+p:start+p+bs]=trial[es+p:es+p+bs]
        (WORK/'encoded'/unit).write_bytes(encoded)
        rel=row['container'];current=containers.get(rel,(ROOT/'data'/rel).read_bytes())
        off=row['texture_offset'];updated=current[:off]+bytes(encoded)+current[off+len(encoded):]
        assert len(updated)==len(current) and updated[:off]==current[:off] and updated[off+len(encoded):]==current[off+len(encoded):]
        containers[rel]=updated;row['blocks']=[list(p) for p in sorted(blocks)]
    base.run('export',WORK/'encoded',WORK/'readback')
    for row in rows:
        a=Image.open(ROOT/row['source']).convert('RGBA')
        p=WORK/'readback'/(row['unit']+'.00.png');b=Image.open(p).convert('RGBA')
        blocks={tuple(p) for p in row['blocks']}
        assert changed_blocks(a,b)<=blocks
        row['readback']=p.relative_to(ROOT).as_posix()
    print('Seven atlas readbacks passed unchanged-block checks.',flush=True)
    base.run('import',WORK/'quote_source',WORK/'quote_trial',WORK/'quote_png')
    trial=dict(parse_members((WORK/'quote_trial/e020_001.pac').read_bytes()))['e020_001.bam']
    assert cgfx_entries(trial)==entries
    start=q['offset'];size=q['bytes'];patched=bytearray(bam)
    # Only copy encoded quote texels; retain original model/animation/header/siblings.
    assert q['format']==13 and size==512*256
    original_quote=Image.open(ROOT/approval['source']).convert('RGBA')
    approved_quote=Image.open(ROOT/approval['output']).convert('RGBA')
    quote_blocks=changed_blocks(original_quote,approved_quote)
    for x,y in quote_blocks:
        p=start+block_offset(x,y,512)
        patched[p:p+16]=trial[p:p+16]
    assert patched[:start]==bam[:start] and patched[start+size:]==bam[start+size:]
    rel='event/model/e020_001.pac'
    result=base.pack([(n,bytes(patched) if n=='e020_001.bam' else b) for n,b in parts])
    assert len(result)==len(pac)
    (WORK/'quote_final/e020_001.pac').write_bytes(result)
    base.run('export',WORK/'quote_final',WORK/'quote_readback')
    containers[rel]=result
    quote_png=WORK/'quote_readback/e020_001.pac_e020_001.bam_model.04.png'
    qa=Image.open(ROOT/approval['source']).convert('RGBA');qb=Image.open(quote_png).convert('RGBA')
    assert changed_blocks(qa,qb)<=quote_blocks
    assert qa.crop((0,180,512,256)).tobytes()==qb.crop((0,180,512,256)).tobytes()
    # Export all other model textures and check them byte-for-byte as decoded RGBA.
    for p in (WORK/'quote_readback').glob('*.png'):
        if p==quote_png:continue
        ref=ROOT/'export_base/event/model'/p.name
        assert Image.open(p).convert('RGBA').tobytes()==Image.open(ref).convert('RGBA').tobytes(),p.name
    for name,a,b in [('seneca_readback_compare',qa,qb),('seneca_preview_vs_readback',Image.open(ROOT/approval['output']).convert('RGBA'),qb)]:
        pair=Image.new('RGBA',(1040,256),(0,0,0,255));pair.alpha_composite(a);pair.alpha_composite(b,(528,0));pair.convert('RGB').save(WORK/(name+'.png'))
    files=[]
    for rel,blob in containers.items():
        p=WORK/'payload'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(blob)
        files.append(dict(file=rel,output=p.relative_to(ROOT).as_posix(),sha256=sha(blob),source_sha256=sha((ROOT/'data'/rel).read_bytes())))
    write(REPORT,dict(files=files,textures=rows,quote=dict(**q,png=approval['output'],sha256=approval['sha256'],readback=quote_png.relative_to(ROOT).as_posix(),other_model_textures_preserved=True,model_animation_bytes_preserved=True),ctpk_count=74,tmx_count=1,model_texture_count=1,original_data_modified=False))
    print('Encoded',len(files),'image containers; quote model/animation preserved.',flush=True)
if __name__=='__main__':main()
