"""Read-only audit, including word-aligned strings embedded beside machine code."""
import json,re
from pathlib import Path
from audit_executable_text import scan
R=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
reviews=[read(R/'translation'/n) for n in ['code_ui_450.review.json','system_456.review.json','code_extra_458.review.json','code_party_577.review.json','code_party_580.review.json']]
reports=[]
for source in ['exefs/code.bin','update/exefs/code.bin']:
    b=(R/source).read_bytes();known=[]
    for doc in reviews:
        for f in doc['files']:
            if f['source']==source:known.extend((r['offset'],r['offset']+r['capacity_bytes']) for r in f['rows'])
    cand={r['offset']:r['original'] for r in scan(R/source)['candidates']}
    for pos in range(0,len(b),4):
        if b[pos]<0x80:continue
        end=b.find(b'\0',pos,pos+160)
        if end<pos+8:continue
        try:s=b[pos:end].decode('cp932')
        except UnicodeDecodeError:continue
        if not re.search('[ぁ-んァ-ヶ]',s):continue
        if not all('\u3000'<=c<='\u30ff' or '\u4e00'<=c<='\u9fff' or c in ' 0123456789%？！？、。～\n' for c in s):continue
        cand[pos]=s
    rows=[];lastend=-1
    for pos,s in sorted(cand.items()):
        end=pos+len(s.encode('cp932'))
        if any(x<=pos<y for x,y in known) or pos<lastend:continue
        rows.append(dict(offset=hex(pos),text=s));lastend=end
    reports.append(dict(source=source,candidates=rows))
names=[]
for p in sorted((R/'translation/compiled/export_base/facility').glob('*.json')):
    d=read(p)
    remaining=[s for s in d.get('speakers',[]) if re.search('[ぁ-んァ-ヶ]',s) and s!='ダミー']
    if remaining:names.append(dict(source=str(p.relative_to(R)),names=remaining))
out=R/'translation/remaining_ui_581.audit.json';out.write_text(json.dumps(dict(executable=reports,facility_speakers=names,classification='candidates_require_review',modified_game_resources=False),ensure_ascii=False,indent=2),encoding='utf-8')
print('BASE candidates',len(reports[0]['candidates']))
for r in reports[0]['candidates']:print(r['offset'],r['text'])
print('FACILITY SPEAKERS',json.dumps(names,ensure_ascii=False))
