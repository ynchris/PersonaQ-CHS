"""Merge reviewed images, executable strings and native pinyin into test payload."""
import hashlib
import json
from pathlib import Path
from raw_text_codec import encode_display,encode_message,decode_display
from stage_pinyin_539 import patch_archive,TARGETS

ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(b):return hashlib.sha256(b).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')

def codes(extra_reviews=(),output_dir='full_work/code_540'):
    mapping=read(ROOT/'translation/font_encoding.hex.json')
    reviews=[read(ROOT/'translation'/n) for n in ['code_ui_450.review.json','system_456.review.json','code_extra_458.review.json']]
    reviews.extend(read(ROOT/'translation'/n) for n in extra_reviews)
    results=[]
    for source in ['exefs/code.bin','update/exefs/code.bin']:
        raw=(ROOT/source).read_bytes();out=bytearray(raw);allowed=set();ranges=[]
        for group,review in enumerate(reviews):
            f=next(f for f in review['files'] if f['source']==source)
            assert sha(raw)==f['sha256']
            for row in f['rows']:
                if group==0 and row['translation'].startswith('钟楼'):
                    assert any(r.get('supersedes_translation')==row['translation'] and r['offset']==row['offset'] for r in next(x for x in reviews[2]['files'] if x['source']==source)['rows'])
                    continue
                pos=row['offset'];cap=row['capacity_bytes']
                encoded=(encode_message if group==1 else encode_display)(row['translation'],mapping)
                assert len(encoded)<=cap,row
                original=bytes.fromhex(row['original_hex']) if 'original_hex' in row else row['original'].encode('cp932')
                assert raw[pos:pos+len(original)]==original
                replacement=encoded.ljust(cap,b'\0')
                overlaps=[r for r in ranges if max(pos,r[0])<min(pos+cap,r[1])]
                if overlaps:
                    for previous in overlaps:
                        lo=max(pos,previous[0]);hi=min(pos+cap,previous[1])
                        if out[lo:hi]!=replacement[lo-pos:hi-pos]:
                            assert group==2 and (row.get('supersedes_translation') or row['original']=='時計塔'),(row,previous)
                out[pos:pos+cap]=replacement;allowed.update(range(pos,pos+cap))
                ranges.append((pos,pos+cap,row['translation']))
                assert out[pos+cap]==raw[pos+cap]
        assert len(out)==len(raw)
        assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,out)))
        # Re-read all final rows, except explicitly superseded old tower text.
        for group,review in enumerate(reviews):
            for row in next(f for f in review['files'] if f['source']==source)['rows']:
                if group==0 and row['translation'].startswith('钟楼'):continue
                pos=row['offset'];cap=row['capacity_bytes']
                expected=(encode_message if group==1 else encode_display)(row['translation'],mapping)
                assert bytes(out[pos:pos+cap]).rstrip(b'\0')==expected.rstrip(b'\0'),row
        scope='update' if source.startswith('update') else 'base'
        path=ROOT/output_dir/scope/'code.bin';path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(out)
        results.append(dict(scope=scope,source=source,source_sha256=sha(raw),output=str(path.relative_to(ROOT)),sha256=sha(out),bytes=len(out),
                            reviewed_strings=len(ranges),outside_string_bytes_preserved=True,roundtrip_verified=True))
    return results

def main():
    manifest_path=ROOT/'translation/integrated_build.generated.json'
    manifest=read(manifest_path)
    stage=ROOT/'full_work/integrated_payload'
    resources={r['file']:r['sha256'] for r in manifest['resources']}
    for rel,digest in resources.items():assert sha((stage/rel).read_bytes())==digest
    exe=codes()
    images=read(ROOT/'translation/build_540/images.json')
    for row in images['files']:
        rel=row['file'];old=(ROOT/'data'/rel).read_bytes();image=(ROOT/row['output']).read_bytes()
        assert sha(old)==row['source_sha256'] and sha(image)==row['sha256']
        current=bytearray((stage/rel).read_bytes() if rel in resources else old)
        # Nested message recompilation may change offsets. Merge by member name
        # in that case; standalone images retain their exact original length.
        from check_roundtrip import parse_members
        from encode_images_540 import pack
        if rel.endswith(('.bin','.arc')):
            a=dict(parse_members(old));b=dict(parse_members(image));parts=parse_members(bytes(current))
            replacement={n:v for n,v in b.items() if v!=a[n]}
            for n,v in parts:
                if n in replacement:assert v==a[n] or v==replacement[n],(rel,n)
            current=bytearray(pack([(n,replacement.get(n,v)) for n,v in parts]))
        else:
            assert len(current)==len(old)==len(image)
            for i,(before,after) in enumerate(zip(old,image)):
                if before!=after:
                    assert current[i] in (before,after),(rel,i)
                    current[i]=after
        target=stage/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(current)
        resources[rel]=sha(current)
    ime=ROOT/'translation/ime_538'
    build=read(ime/'build.json');tests=read(ime/'native_test.json')
    assert build['font_map_sha256']==sha((ROOT/'translation/font_encoding.hex.json').read_bytes())
    for name,digest in build['dictionaries'].items():assert digest==tests['hashes'][name]==sha((ime/name).read_bytes())
    for filename,prefix in TARGETS.items():
        rel='init/'+filename
        before=(stage/rel).read_bytes() if rel in resources else (ROOT/'data'/rel).read_bytes()
        after=patch_archive(before,prefix,(ime/'pinyin_idx.tbl').read_bytes(),(ime/'pinyin_dat.txt').read_bytes())
        target=stage/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after);resources[rel]=sha(after)
    manifest.update(executable_resources=exe,resources=[dict(file=n,sha256=h) for n,h in sorted(resources.items())],
                    test_revision=540,image_ctpk_count=68,image_tmx_count=1,pinyin_input_archives=4,
                    pinyin_native_function_tests=838,cpk_packaged=False,runtime_tested=False,
                    pending=['Seneca opening quote untranslated','Gameplay layout and pinyin input/save testing','Full-game coverage verification'])
    assert {p.relative_to(stage).as_posix():sha(p.read_bytes()) for p in stage.rglob('*') if p.is_file()}==resources
    write(manifest_path,manifest)
    write(ROOT/'translation/build_540/integrated.json',manifest)
    print('Integrated test revision 540:',len(resources),'resources;',[(r['scope'],r['reviewed_strings']) for r in exe])

if __name__=='__main__':main()
