"""Resolve Arcana through three real pointer tables per version; review only."""
import hashlib
import struct
from compile_translation import ROOT, read, write
from audit_visual_457 import ARCANA
from raw_text_codec import encode_display, encode_message

TABLES={'exefs/code.bin':[0x3eb5ac,0x3fcbe0,0x3fcf4c],
        'update/exefs/code.bin':[0x3fec9c,0x4102d0,0x41063c]}

def main():
    mapping=read(ROOT/'translation/font_encoding.hex.json')
    q2path=ROOT.parent/'references/PersonaQ2ChsLocalization-latest-20260928/texts/zh_Hans/code.bin.json'
    q2={r['original']:r['translation'] for r in read(q2path)}
    old=read(ROOT/'translation/code_ui_450.review.json')
    system=read(ROOT/'translation/system_456.review.json')
    files=[]
    for f,s in zip(old['files'],system['files']):
        raw=(ROOT/f['source']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==f['sha256']==s['sha256']
        rows=[]
        for i,(jp,default) in enumerate(ARCANA.items()):
            slots=[table+i*4 for table in TABLES[f['source']]]
            pointers=[struct.unpack_from('<I',raw,p)[0]-0x100000 for p in slots]
            assert len(set(pointers))==1
            pos=pointers[0]; end=raw.index(0,pos)
            assert raw[pos:end].decode('cp932')==jp,(jp,pos)
            cn=q2.get(jp,default)
            encoded=encode_display(cn,mapping)
            assert len(encoded)<=end-pos
            # Single-character suffixes share storage with other strings.
            # Do not alter them if a previous byte is not NUL.
            if raw[pos-1]!=0:assert encoded==raw[pos:end],jp
            rows.append(dict(offset=pos,capacity_bytes=end-pos,original=jp,translation=cn,
                             pointer_slots=slots,reference='Q2 local snapshot' if jp in q2 else 'same written form',
                             changes_bytes=encoded!=raw[pos:end]))
        jp='どちらの物語を体験しますか？'; needle=jp.encode('cp932')+b'\0'
        pos=raw.find(needle); assert pos>=0 and raw.find(needle,pos+1)<0 and pos%4==0
        rows.append(dict(offset=pos,capacity_bytes=len(needle)-1,original=jp,translation='想体验哪位主角的故事？',reference='user screenshot'))
        # Existing 時計塔 -> 钟楼 zero-pads the aliased 塔 string. Preserve
        # its last character at the original address with a full-length label.
        parent=next(r for r in f['rows'] if r['original']=='時計塔')
        correction=dict(parent,translation='时钟塔',supersedes_translation=parent['translation'],
                        reference='Preserve Arcana 塔 suffix; reviewed storage alias')
        rows.append(correction)
        for oldrow in f['rows']:
            if oldrow['offset']!=parent['offset'] and '钟楼' in oldrow['translation']:
                rows.append(dict(oldrow,translation=oldrow['translation'].replace('钟楼','时钟塔'),
                                 supersedes_translation=oldrow['translation'],reference='User-approved place-name consistency'))
        active=[r for r in rows if r.get('changes_bytes',True)]
        superseded={r['offset'] for r in rows if 'supersedes_translation' in r}
        prior=[r for r in f['rows'] if r['offset'] not in superseded]
        # Dry-run complete planned code changes in memory only.
        allrows=prior+s['rows']+active; occupied=set(); out=bytearray(raw)
        for r in allrows:
            pos=r['offset']; end=pos+r['capacity_bytes']; region=set(range(pos,end))
            assert not occupied.intersection(region),(f['source'],r)
            occupied.update(region)
            expected=bytes.fromhex(r['original_hex']) if 'original_hex' in r else r['original'].encode('cp932')
            assert raw[pos:end]==expected and raw[end]==0
            encoded=encode_message(r['translation'],mapping)
            assert len(encoded)<=end-pos
            out[pos:end]=encoded.ljust(end-pos,b'\0')
        assert len(out)==len(raw)
        assert all(a==b or i in occupied for i,(a,b) in enumerate(zip(raw,out)))
        for r in rows:
            for p in r.get('pointer_slots',[]):assert out[p:p+4]==raw[p:p+4]
            if 'pointer_slots' in r:
                pos=r['offset']; end=out.index(0,pos)
                assert bytes(out[pos:end])==encode_display(r['translation'],mapping),r
        files.append(dict(source=f['source'],sha256=f['sha256'],rows=rows,
                          combined_dry_run_rows=len(allrows),combined_dry_run_sha256=hashlib.sha256(out).hexdigest()))
    write(ROOT/'translation/code_extra_458.review.json',dict(files=files,packaged=False,code_written=False,
        q2_reference_sha256=hashlib.sha256(q2path.read_bytes()).hexdigest(),
        encoding_sha256=hashlib.sha256((ROOT/'translation/font_encoding.hex.json').read_bytes()).hexdigest(),
        notes=['Q2 translations only; PQ1 addresses resolved separately. 剛毅 reuses Q2 力量.',
               'Corrects 457 false standalone 塔/月 candidates: actual Arcana pointers reference suffixes of other strings. Shared suffix bytes left unchanged.',
               'No on-disk code output. Runtime and sprite labels remain unverified.']))
    print([(f['source'],len(f['rows']),f['combined_dry_run_rows']) for f in files])

if __name__=='__main__':main()
