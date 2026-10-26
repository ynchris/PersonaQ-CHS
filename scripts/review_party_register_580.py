"""Validate missed registration/recall executable labels without altering binaries."""
from pathlib import Path
import json,hashlib
from raw_text_codec import encode_display,decode_display
R=Path(__file__).resolve().parent
T={'パーティを登録します':'登录队伍','登録パーティを呼び出します':'调用已登录队伍'}
mapping=json.loads((R/'translation/font_encoding.hex.json').read_text(encoding='utf-8'))
files=[]
for source in ['exefs/code.bin','update/exefs/code.bin']:
    raw=(R/source).read_bytes();out=bytearray(raw);rows=[];allowed=set()
    for jp,cn in T.items():
        needle=jp.encode('cp932')+b'\0';pos=raw.find(needle);assert pos>=0 and raw.find(needle,pos+1)<0
        cap=len(needle)-1;encoded=encode_display(cn,mapping)
        assert pos%4==0 or raw[pos-1]==0
        assert len(encoded)<=cap and decode_display(encoded,mapping)==cn
        for report in ['code_ui_450.review.json','system_456.review.json','code_extra_458.review.json','code_party_577.review.json']:
            doc=json.loads((R/'translation'/report).read_text(encoding='utf-8'))
            for f in doc['files']:
                if f['source']==source:
                    assert not any(r['offset']<pos+cap and r['offset']+r['capacity_bytes']>pos for r in f['rows'])
        out[pos:pos+cap]=encoded.ljust(cap,b'\0');allowed.update(range(pos,pos+cap))
        rows.append(dict(offset=pos,offset_hex=hex(pos),capacity_bytes=cap,original=jp,translation=cn))
    assert len(out)==len(raw) and all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,out)))
    files.append(dict(source=source,sha256=hashlib.sha256(raw).hexdigest(),rows=rows,dry_run_verified=True))
(R/'translation/code_party_580.review.json').write_text(json.dumps(dict(files=files,status='validated_pending_next_integration',code_written=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(files,ensure_ascii=False,indent=2))
