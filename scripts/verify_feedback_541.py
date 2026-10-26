import re
from compile_translation import ROOT,read,write,TOKEN
from raw_text_codec import encode_message,encode_display,decode_display
review=read(ROOT/'translation/terminology_541.review.json')
catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')}
mapping=read(ROOT/'translation/font_encoding.hex.json')
for r in review['rows']:
    assert catalog[r['key']]['translation']==r['after']
    assert TOKEN.findall(r['before'])==TOKEN.findall(r['after'])
    encode_message(r['after'],mapping)
    assert decode_display(encode_display(r['enemy_translation'],mapping),mapping)==r['enemy_translation']
refs=read(ROOT/'translation/feedback_541/material_enemy_audit.json')
for r in refs:
    assert len(r['enemies'])==1
    assert r['enemies'][0][1] in catalog[r['key']]['translation']
unmatched=[]
known={r['key'] for r in refs}|{r['key'] for r in review['rows']}
for r in catalog.values():
    if 'datmaterialhelp' in r['source'] and '討伐：' in r['original'] and r['key'] not in known:unmatched.append(r)
write(ROOT/'translation/feedback_541/verification.json',dict(corrected_rows=len(review['rows']),
    verified_enemy_references=len(refs),control_codes_preserved=True,font_encodable=True,
    unmatched_material_drop_rows=unmatched,images_pending_user_review=True,packaged=False))
print('Verified corrections:',len(review['rows']),'enemy references:',len(refs),'unmatched:',len(unmatched))
for r in unmatched:print(r['key'],TOKEN.sub('',r['original']))
