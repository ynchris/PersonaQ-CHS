"""Locate and validate the missed party prompt in both executables; no packaging."""
import hashlib,json
from pathlib import Path
from raw_text_codec import encode_display
R=Path(__file__).resolve().parent
jp='入れ替えるメンバーを選んでください';cn='请选择要替换的成员'
mapping=json.loads((R/'translation/font_encoding.hex.json').read_text(encoding='utf-8'))
encoded=encode_display(cn,mapping);needle=jp.encode('cp932')+b'\0'
files=[]
for name in ['exefs/code.bin','update/exefs/code.bin']:
    raw=(R/name).read_bytes();hits=[];p=0
    while (p:=raw.find(needle,p))>=0:hits.append(p);p+=len(needle)
    assert len(hits)==1,(name,hits)
    pos=hits[0];capacity=len(needle)-1
    assert pos%4==0 and len(encoded)<=capacity
    overlaps=[]
    for report in ['code_ui_450.review.json','system_456.review.json','code_extra_458.review.json']:
        doc=json.loads((R/'translation'/report).read_text(encoding='utf-8'))
        for f in doc['files']:
            if f['source']==name:
                overlaps += [r for r in f['rows'] if r['offset']<pos+capacity and r['offset']+r['capacity_bytes']>pos]
    assert not overlaps
    trial=bytearray(raw);trial[pos:pos+capacity]=encoded.ljust(capacity,b'\0')
    assert trial[:pos]==raw[:pos] and trial[pos+capacity:]==raw[pos+capacity:]
    files.append(dict(source=name,sha256=hashlib.sha256(raw).hexdigest(),rows=[dict(offset=pos,offset_hex=hex(pos),capacity_bytes=capacity,original=jp,translation=cn,encoded_hex=encoded.hex())],occurrences=1,prior_patch_overlap=False,dry_run_verified=True))
out=R/'translation/code_party_577.review.json'
out.write_text(json.dumps(dict(files=files,status='validated_pending_next_integration',code_written=False,packaged=False,route_note='One occurrence in each executable; shared-route use is likely but P3 runtime has not been verified.'),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(files,ensure_ascii=False,indent=2))
