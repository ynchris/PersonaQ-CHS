"""Revision 589: encode all approved textures (540 + 562 rows, 20 UI textures replaced by the
user-accepted 587 finals). Untouched ETC blocks and container bytes are preserved. The opening
quote (570), fiction and caution TMX are reused byte-for-byte from the verified 583 payload.
The 583 SPR3 box edit for sprite 218 is NOT applied (label went back to its own box in 587)."""
import hashlib,json,shutil,struct
from pathlib import Path
from PIL import Image
import encode_images_540 as base
from check_roundtrip import parse_members
from localize_ctpk_464 import layout
from patch_menu_blocks_461 import block_offset
ROOT=Path(__file__).resolve().parent
WORK=ROOT/'full_work/images_589';base.WORK=WORK
REPORT=ROOT/'translation/build_589/images.json'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(b):return hashlib.sha256(b).hexdigest()
def norm(p):return p.replace('\\','/')
def main():
    for n in ['source','png','trial','encoded','readback','payload']:(WORK/n).mkdir(parents=True,exist_ok=True)
    rows={}
    for f in ['translation/build_540/images.json','translation/build_583/images.json']:
        for r in read(ROOT/f)['textures']:
            rows[(r['container'],r['texture_offset'])]=dict(container=r['container'],member=r.get('member'),texture_offset=r['texture_offset'],source=norm(r['source']),png=norm(r['png']))
    final=read(ROOT/'translation/previews_587/final/report.json');replaced=0
    for e in final:
        k=(e['container'],e['texture_offset']);assert k in rows,k
        assert sha((ROOT/e['png']).read_bytes())==e['sha256']
        rows[k]['png']=e['png'];rows[k]['revision']=587;rows[k]['decision']=e.get('decision','fz_redraw');replaced+=1
    rows=list(rows.values());print('textures',len(rows),'replaced by 587 finals',replaced,flush=True)
    for i,row in enumerate(rows):
        raw=(ROOT/'data'/row['container']).read_bytes()
        if row['member']:raw=dict(parse_members(raw))[row['member']]
        off=row['texture_offset'];assert raw[off:off+4]==b'CTPK',row
        section,size=struct.unpack_from('<II',raw,off+8);ctpk=raw[off:off+section+size]
        start,w,h,bs=layout(ctpk)
        with Image.open(ROOT/row['png']) as im:assert im.size==(w,h),row
        unit=f'{i:03}.ctpk';row['unit']=unit;row['sha256']=sha((ROOT/row['png']).read_bytes())
        (WORK/'source'/unit).write_bytes(ctpk);shutil.copy2(ROOT/row['png'],WORK/'png'/(unit+'.00.png'))
    base.run('import',WORK/'source',WORK/'trial',WORK/'png')
    containers={}
    for row in rows:
        unit=row['unit'];original=(WORK/'source'/unit).read_bytes();encoded=(WORK/'trial'/unit).read_bytes()
        start,w,h,bs=layout(original);es,ew,eh,ebs=layout(encoded);assert (w,h,bs)==(ew,eh,ebs)
        a=Image.open(ROOT/row['source']).convert('RGBA');b=Image.open(ROOT/row['png']).convert('RGBA')
        blocks={(i%w//4*4,i//w//4*4) for i,(x,y) in enumerate(zip(a.getdata(),b.getdata())) if x!=y}
        out=bytearray(original)
        for x,y in blocks:
            p=block_offset(x,y,w)*bs//16;out[start+p:start+p+bs]=encoded[es+p:es+p+bs]
        assert out[:start]==original[:start]
        (WORK/'encoded'/unit).write_bytes(out);row['blocks']=len(blocks)
        rel=row['container'];current=containers.get(rel,(ROOT/'data'/rel).read_bytes());off=row['texture_offset']
        if row['member']:
            parts=parse_members(current);current=base.pack([(n,b2[:off]+bytes(out)+b2[off+len(out):] if n==row['member'] else b2) for n,b2 in parts])
        else:
            current=current[:off]+bytes(out)+current[off+len(out):]
        containers[rel]=current
        row['_blockset']=blocks
    base.run('export',WORK/'encoded',WORK/'readback')
    for row in rows:
        a=Image.open(ROOT/row['source']).convert('RGBA');b=Image.open(WORK/'readback'/(row['unit']+'.00.png')).convert('RGBA');w=a.width
        blocks=row.pop('_blockset')
        assert all(x==y or (i%w//4*4,i//w//4*4) in blocks for i,(x,y) in enumerate(zip(a.getdata(),b.getdata()))),row['source']
        row['readback']=(WORK/'readback'/(row['unit']+'.00.png')).relative_to(ROOT).as_posix()
    # reuse verified 583 bytes for non-CTPK assets (quote model texture, fiction, caution TMX)
    prev=read(ROOT/'translation/build_583/images.json');reused=[]
    for f in prev['files']:
        if f['file'] in ('event/model/e020_001.pac','title/fiction.ctpk','title/logo.bin'):
            blob=(ROOT/f['output']).read_bytes();assert sha(blob)==f['sha256']
            assert f['file'] not in containers or f['file']=='title/fiction.ctpk'
            containers[f['file']]=blob;reused.append(f['file'])
    assert sorted(reused)==['event/model/e020_001.pac','title/fiction.ctpk','title/logo.bin'],reused
    # c_main.spr3 must carry the ORIGINAL sprite records (no 583 box edit)
    cm=containers['camp/c_main.spr3'];orig=(ROOT/'data/camp/c_main.spr3').read_bytes()
    table=struct.unpack_from('<I',orig,28)[0];p=struct.unpack_from('<I',orig,table+218*8+4)[0]
    assert struct.unpack_from('<4i',cm,p+84)==(353,493,422,511)
    files=[]
    for rel,blob in containers.items():
        out=WORK/'payload'/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(blob)
        files.append(dict(file=rel,output=out.relative_to(ROOT).as_posix(),sha256=sha(blob),source_sha256=sha((ROOT/'data'/rel).read_bytes())))
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(json.dumps(dict(quote=prev['quote'],tmx_count=1,model_texture_count=1,files=files,textures=rows,ctpk_count=len(rows),reused_from_583=reused,ui_textures_from_587=replaced,
        sprite_218_box_original=True,untouched_blocks_verified=True,original_data_modified=False),ensure_ascii=False,indent=1),encoding='utf-8')
    print('Encoded',len(files),'containers;',len(rows),'textures; reused',reused,flush=True)
if __name__=='__main__':main()
