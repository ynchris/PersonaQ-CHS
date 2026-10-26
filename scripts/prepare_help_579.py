"""Review missing facility help tables; preserve metadata and truncated header tails."""
import hashlib,json
from pathlib import Path
from check_roundtrip import members
from extract_fixed_tables import inspect
from raw_text_codec import encode_display,decode_display
R=Path(__file__).resolve().parent
T={'合体の基本':'合体基础','合体の法則':'合体法则','スキルの継承':'技能继承','継承できるスキルの属性':'可继承的技能属性','合体事故':'合体事故','検索合体':'搜索合体','トライアングル・スプレッド':'三角展开','イケニエ・スプレッド':'祭品展开','スキルカード抽出':'技能卡抽出','すれちがい手帳を閲覧する':'查看擦肩手册','自分の手帳を編集する':'编辑自己的手册','ＱＲコード':'二维码','すれちがい通信設定':'擦肩通信设置','説明を聞く':'听取说明','やめる':'取消','治療':'治疗'}
mapping=json.loads((R/'translation/font_encoding.hex.json').read_text(encoding='utf-8'))
working=json.loads((R/'translation/tables.catalog.working.json').read_text(encoding='utf-8'))
covered={r['key']:r for r in working}
new=[];audit=[]
for i,(name,data) in enumerate(members(R/'data/init/fcltable.bin')):
    if not name.startswith('fclHelpTable_'):continue
    rows=inspect(data,name);out=bytearray(data);pairs=[]
    for r in rows:
        key=f'init/fcltable.bin:{i}:{name}:{r["row"]}'
        if key in covered:
            assert covered[key]['translation'],key
            continue
        jp=r['original'];cn=T[jp];encoded=encode_display(cn,mapping);assert len(encoded)<r['capacity_bytes'];assert decode_display(encoded,mapping)==cn
        p=r['offset'];cap=r['capacity_bytes'];out[p:p+cap]=encoded.ljust(cap,b'\0');pairs.append([jp,cn])
    if pairs:
        assert len(pairs)==len(rows)
        allowed={j for r in rows for j in range(r['offset'],r['offset']+r['capacity_bytes'])}
        assert all(x==y or j in allowed for j,(x,y) in enumerate(zip(data,out)))
        new.append(dict(index=i,name=name,sha256=hashlib.sha256(data).hexdigest(),rows=pairs))
    audit.append(dict(member=name,rows=len(rows),new_rows=len(pairs),all_rows_translated=True))
assert sum(len(m['rows']) for m in new)==23
(R/'translation/table_batches/579_facility_help.json').write_text(json.dumps(dict(source='init/fcltable.bin',members=new),ensure_ascii=False,indent=2),encoding='utf-8')
(R/'translation/help_audit_579.json').write_text(json.dumps(dict(tables=audit,new_rows=23,metadata_preserved=True,encoded_roundtrip_verified=True,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(new,ensure_ascii=False,indent=2))
