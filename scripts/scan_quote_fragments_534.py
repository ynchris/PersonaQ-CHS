"""Read-only multi-encoding fragment scan for independent source triage."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'translation/handoff_534';OUT.mkdir(exist_ok=True)
fragments=['志ある','志なき','引きず','Seneca','運命']
encodings=['cp932','shift_jis','utf-16-le','utf-16-be','utf-8']
needles=[]
for frag in fragments:
    for enc in encodings:
        needles.append((frag,enc,frag.encode(enc)))
paths=sorted(p for p in (ROOT/'data').rglob('*') if p.is_file())
paths += [ROOT/'exefs/code.bin',ROOT/'update/exefs/code.bin']
failed=[];hits=[];scanned=0;total_bytes=0
for p in paths:
    rel=p.relative_to(ROOT).as_posix()
    try:raw=p.read_bytes()
    except Exception as e:
        failed.append(dict(source=rel,error=str(e)));continue
    scanned+=1;total_bytes+=len(raw);found=[]
    for frag,enc,needle in needles:
        start=0
        while (pos:=raw.find(needle,start))>=0:
            found.append(dict(fragment=frag,encoding=enc,offset=pos,offset_hex=hex(pos)))
            start=pos+1
    if found:hits.append(dict(source=rel,size=len(raw),sha256=hashlib.sha256(raw).hexdigest(),hits=found))
result=dict(created_utc=datetime.now(timezone.utc).isoformat(),roots=['data','exefs/code.bin','update/exefs/code.bin'],fragments=fragments,encodings=encodings,scanned_files=scanned,scanned_bytes=total_bytes,files_with_hits=len(hits),hit_count=sum(len(x['hits']) for x in hits),failed=failed,hits=hits,notes=['Read-only raw-byte search; hits are not verified displayed text or safe patch offsets.','Equivalent encoding labels may produce duplicate offsets.','Compressed members are not decompressed by this scan.','Update executable is an additional target beyond supplied script.'])
(OUT/'quote_fragment_scan.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
lines=[f'Root: {ROOT}',f'Scanned: {scanned} files; hits in {len(hits)} files; failed: {len(failed)}','Offsets are file-relative. No resource was modified.','Duplicate offsets across equivalent encodings are retained.','']
for entry in hits:
    lines.append('HIT: '+entry['source'])
    for h in entry['hits']:lines.append(f"  [{h['encoding']}] {h['fragment']} @ {h['offset_hex']}")
for entry in failed:lines.append('FAILED: '+entry['source']+' '+entry['error'])
(OUT/'quote_fragment_scan.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8-sig')
print(json.dumps({k:result[k] for k in ['scanned_files','scanned_bytes','files_with_hits','hit_count','failed']},ensure_ascii=False))
print('Distinct file/offset hits by fragment:',{f:len({(r['source'],h['offset']) for r in hits for h in r['hits'] if h['fragment']==f}) for f in fragments})
