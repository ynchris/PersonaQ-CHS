"""Read back all current enemy references and NPC speaker labels."""
from collections import Counter
from compile_translation import ROOT,read,write,TOKEN
from q2_name_banks import load,build_bank
from raw_text_codec import encode_message
out=ROOT/'translation/audit_555';out.mkdir(exist_ok=True)
catalog=read(ROOT/'translation/catalog.working.json');lookup={r['key']:r for r in catalog}
group=next(g for g in load()['groups'] if g['source']=='battle/table/enemynametable.tbl')
names={r['original']:r['translation'] for r in group['rows']}
mapping=read(ROOT/'translation/font_encoding.hex.json')
for r in read(ROOT/'translation/terminology_555.review.json')['messages']:
    assert lookup[r['key']]['translation']==r['after']
    encode_message(r['after'],mapping)
build_bank((ROOT/'data'/group['source']).read_bytes(),group['count'],group['rows'],mapping)
candidates=[];matched=0
for r in catalog:
    if not r.get('translation'):continue
    jp=TOKEN.sub('',r['original']);zh=TOKEN.sub('',r['translation'])
    found=[n for n in names if n in jp]
    found=[n for n in found if not any(n!=m and n in m for m in found)]
    for n in found:
        if names[n] in zh:matched+=1
        else:candidates.append(dict(key=r['key'],enemy=n,expected=names[n],original=jp,translation=zh))
speakers=Counter();wrong=[]
for path in (ROOT/'translation/compiled').rglob('*.json'):
    doc=read(path)
    if not isinstance(doc,dict):continue
    for s in doc.get('speakers',[]):
        if any(n in s for n in ['伊丽莎白','伊莉莎白','迪奥多','西奥多','玛格丽特']):speakers[s]+=1
        if '伊莉莎白' in s or '西奥多' in s:wrong.append((str(path),s))
assert not wrong,wrong
assert not any(any(n in (r.get('translation') or '') for n in ['伊莉莎白','西奥多']) for r in catalog)
write(out/'remaining_reference_candidates.json',candidates)
write(out/'report.json',dict(exact_name_references=matched,remaining_candidates=len(candidates),candidate_counts=dict(Counter(r['enemy'] for r in candidates)),npc_speaker_counts=dict(speakers),bank_roundtrip_pass=True,old_npc_variants_remaining=0,rom_rebuilt=False))
print(read(out/'report.json'))
for r in candidates:print(r)
