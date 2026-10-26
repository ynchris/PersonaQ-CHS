"""Read only this task's history and recover original 501 review exchange."""
import json
from pathlib import Path
from compile_translation import ROOT,write
path=Path('C:/Users/ynChr/.codex/sessions/2026/08/25/rollout-2026-08-25T18-50-23-01a03bc2-e416-7520-b2ff-4277b676670f.jsonl')
messages=[]
with path.open(encoding='utf-8') as f:
    for line in f:
        r=json.loads(line);p=r.get('payload',{})
        if r.get('type')!='response_item' or p.get('type')!='message' or p.get('role') not in ('user','assistant'):continue
        text='\n'.join(c.get('text','') for c in p.get('content',[]) if isinstance(c,dict))
        if text:messages.append(dict(role=p['role'],timestamp=r.get('timestamp'),text=text))
hits=[]
for i,r in enumerate(messages):
    if r['role']=='assistant' and any(s in r['text'] for s in ['previews_501','营地14','营地 14']):
        hits.append(messages[max(0,i-1):i+4])
write(ROOT/'translation/previews_548/history_501.json',hits)
print(json.dumps(hits[:5],ensure_ascii=False,indent=2))
