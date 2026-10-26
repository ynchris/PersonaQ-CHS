"""Inspect unexplored opening containers; read-only against source assets."""
import json, hashlib
from pathlib import Path
from check_roundtrip import parse_members
ROOT=Path(__file__).resolve().parent
out=ROOT/'translation/opening_526';out.mkdir(exist_ok=True)
rows=[]
for rel in ['title/logo.bin','title/title.bin','init/nameentry.arc']:
    raw=(ROOT/'data'/rel).read_bytes()
    try:members=parse_members(raw)
    except Exception as e:
        rows.append(dict(source=rel,error=str(e),header=raw[:64].hex()));continue
    row=dict(source=rel,sha256=hashlib.sha256(raw).hexdigest(),members=[])
    for name,data in members:
        row['members'].append(dict(name=name,size=len(data),magic=data[:16].hex()))
    rows.append(row)
(out/'containers.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
for row in rows:
    print(row['source'],[(m['name'],m['size']) for m in row.get('members',[])],row.get('error',''))
