"""Extract exact original CTPK bytes for a read-only external investigation."""
from pathlib import Path
import hashlib,json
from check_roundtrip import parse_members
ROOT=Path(__file__).resolve().parent
out=ROOT/'translation/handoff_535';out.mkdir(exist_ok=True)
container=ROOT/'data/dungeon_in/dungeon_in.bin'
raw=container.read_bytes()
matches=[d for n,d in parse_members(raw) if n=='net_512.ctpk']
assert len(matches)==1
assets={'net_512.ctpk':matches[0],'fiction.ctpk':(ROOT/'data/title/fiction.ctpk').read_bytes()}
report=[]
for name,data in assets.items():
    assert data[:4]==b'CTPK'
    target=out/name
    if target.exists():assert target.read_bytes()==data
    else:target.write_bytes(data)
    assert target.read_bytes()==data
    report.append(dict(file=name,size=len(data),sha256=hashlib.sha256(data).hexdigest()))
assert container.read_bytes()==raw
(out/'sources.json').write_text(json.dumps(dict(net_source='data/dungeon_in/dungeon_in.bin -> net_512.ctpk',fiction_source='data/title/fiction.ctpk',files=report,original_bytes_unchanged=True),indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
