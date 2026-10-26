"""Read-only anchor discovery for keyboard/opening; not safe patch addresses."""
import json
from preview_tutorials_468 import ROOT,digest
terms=['おまかせ','キャンセル','決定','記号','小字','かな','カナ','この名前でよろしいですか','運命は','志ある者','志なき者','Lucius','Seneca']
targets=[ROOT/'exefs/code.bin',ROOT/'update/exefs/code.bin']
targets += list((ROOT/'data/init').glob('*.arc'))+list((ROOT/'data/title').glob('*'))
hits=[];files=[]
for p in targets:
    if not p.is_file():continue
    raw=p.read_bytes();source=p.relative_to(ROOT).as_posix()
    files.append(dict(source=source,sha256=digest(p),size=len(raw)))
    for term in terms:
        for enc in ['cp932','utf-16-le','utf-8']:
            needle=term.encode(enc);start=0
            while (pos:=raw.find(needle,start))>=0:
                hits.append(dict(source=source,term=term,encoding=enc,offset=pos,context_hex=raw[max(0,pos-12):pos+len(needle)+32].hex()))
                start=pos+len(needle)
result=dict(files=files,hits=hits,scope='Exact anchor scan of both executables and init/title archives only.',patch_safe=False,notes=['Hits may be metadata, not displayed text.','No runtime references or string capacities validated.','No executable changes, pinyin implementation, or movie decoding.'])
(ROOT/'translation/keyboard_opening_523.scan.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
for h in hits:print(h['source'],h['term'],h['encoding'],hex(h['offset']))
print('Hits:',len(hits))
