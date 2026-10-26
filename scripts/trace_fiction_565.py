"""Read-only executable string/pointer triage, not proven runtime calls."""
import json, re, struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent
out = ROOT / 'translation/opening_trace_565'
out.mkdir(exist_ok=True)
report = []
for rel in ['exefs/code.bin', 'update/exefs/code.bin']:
    raw = (ROOT / rel).read_bytes()
    entries = []
    for m in re.finditer(rb'[ -~]{4,}', raw):
        if not any(t in m.group().lower() for t in [b'fiction', b'nameentry', b'butter', b'dungeon_in', b'psq00']):
            continue
        va = m.start() + 0x100000
        needle = struct.pack('<I', va)
        refs = [p for p in range(0, len(raw)-3, 4) if raw[p:p+4] == needle]
        entries.append(dict(string=m.group().decode('ascii'), offset=hex(m.start()), assumed_va=hex(va), aligned_pointer_offsets=[hex(p) for p in refs]))
    report.append(dict(source=rel, entries=entries))
(out / 'string_refs.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
