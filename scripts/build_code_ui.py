"""Build separate local code copies. Does not install or overwrite any ROM."""
import hashlib,re
from compile_translation import ROOT,read,write
from raw_text_codec import encode_display,decode_display
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    review_path=ROOT/'translation/code_ui_450.review.json';review=read(review_path)
    mapping_path=ROOT/'translation/font_encoding.hex.json';mapping=read(mapping_path);report=[]
    for file in review['files']:
        path=ROOT/file['source'];raw=path.read_bytes();assert sha(raw)==file['sha256'];out=bytearray(raw);allowed=set()
        for row in file['rows']:
            pos=row['offset'];cap=row['capacity_bytes'];original=row['original'].encode('cp932')
            assert raw[pos:pos+cap+1]==original+b'\0';assert len(original)==cap
            assert re.findall(r'%[sd]',row['original'])==re.findall(r'%[sd]',row['translation'])
            encoded=encode_display(row['translation'],mapping);assert len(encoded)<=cap,(row,len(encoded))
            assert decode_display(encoded,mapping)==row['translation']
            assert not allowed.intersection(range(pos,pos+cap));allowed.update(range(pos,pos+cap))
            out[pos:pos+cap]=encoded.ljust(cap,b'\0')
        assert len(out)==len(raw)
        assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,out)))
        for row in file['rows']:
            pos=row['offset'];cap=row['capacity_bytes'];assert out[pos+cap]==0
            assert decode_display(bytes(out[pos:pos+cap]).rstrip(b'\0'),mapping)==row['translation']
        scope='base' if file['source']=='exefs/code.bin' else 'update'
        dest=ROOT/'full_work/code_ui_payload'/scope/'code.bin';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(out)
        assert sha(path.read_bytes())==file['sha256']
        report.append(dict(scope=scope,source=file['source'],source_sha256=file['sha256'],output=dest.relative_to(ROOT).as_posix(),sha256=sha(out),bytes=len(out),reviewed_strings=len(file['rows']),outside_string_bytes_preserved=True,terminators_preserved=True,roundtrip_verified=True))
    write(ROOT/'translation/code_ui_build.generated.json',dict(files=report,review_sha256=sha(review_path.read_bytes()),encoding_sha256=sha(mapping_path.read_bytes()),runtime_tested=False,deployed=False,notes='Base/update copies are separate, not interchangeable; do not combine with old fonts or packaged snapshot429.'))
    print('Code copies verified:',[(r['scope'],r['reviewed_strings']) for r in report])
if __name__=='__main__':main()
