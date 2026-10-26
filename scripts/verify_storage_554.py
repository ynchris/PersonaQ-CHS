"""Verify compiled slot labels, control streams, and unrelated location terms."""
from compile_translation import ROOT,read,TOKEN,write
catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')}
rows=read(ROOT/'translation/terminology_554.review.json')['rows']
keys={r['key'] for r in rows}
for r in rows:
    current=catalog[r['key']]
    assert current['translation']==r['after'],r['key']
    assert TOKEN.findall(r['before'])==TOKEN.findall(r['after'])
    src,mi,li=r['key'].rsplit(':',2)
    doc=read(ROOT/'translation/compiled'/src)
    assert doc['texts'][int(mi)]['lines'][int(li)]==r['after']
unchanged=0
for r in read(ROOT/'translation/previews_554/storage_audit.json'):
    if r['key'] not in keys:
        assert catalog[r['key']]['translation']==r['translation']
        unchanged+=1
remaining=[r['key'] for r in catalog.values() if r['source']=='export_base/facility/msg_weapon.bmd.json' and any(t in (r.get('translation') or '') for t in ['９９处','１处空间'])]
assert not remaining,remaining
write(ROOT/'translation/previews_554/text_verification.json',dict(corrected_rows=len(rows),unchanged_context_rows=unchanged,controls_unchanged=True,compiled_values_match=True,remaining_old_storage_counter=remaining,rom_rebuilt=False))
print('PASS:',len(rows),'storage rows;',unchanged,'unrelated contexts preserved')
