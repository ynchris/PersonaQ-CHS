"""Build isolated code copies and verify all current facility speaker fixes."""
import json,re
from pathlib import Path
from integrate_test_540 import codes
R=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
audit=read(R/'translation/ui_fixes_582.audit.json');checked=0
for row in audit['speaker_rows']:
    original=read(R/row['source']);current=read(R/'translation/compiled'/row['source'])
    assert current['speakers'][row['index']]==row['translation']
    for a,b in zip(original['texts'],current['texts']):
        if a['speaker']==row['original']:assert b['speaker']==row['translation'];checked+=1
        for x,y in zip(a['lines'],b['lines']):assert re.findall(r'\{[0-9A-F ]+\}',x)==re.findall(r'\{[0-9A-F ]+\}',y)
remaining=[]
for p in (R/'translation/compiled/export_base/facility').glob('*.json'):
    for s in read(p).get('speakers',[]):
        if s!='ダミー' and re.search('[ぁ-んァ-ヶ]',s):remaining.append([p.name,s])
assert not remaining,remaining
outputs=codes(['code_party_577.review.json','code_party_580.review.json','code_ui_582.review.json'],'full_work/code_582')
report=dict(files=outputs,verified_speaker_entries=len(audit['speaker_rows']),verified_message_speaker_references=checked,facility_kana_speakers_remaining=remaining,control_codes_preserved=True,packaged=False,runtime_tested=False)
(R/'translation/ui_fixes_582.verified.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
