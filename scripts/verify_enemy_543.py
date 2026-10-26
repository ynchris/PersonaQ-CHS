from compile_translation import ROOT,read,write,TOKEN
from raw_text_codec import encode_message
catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')}
mapping=read(ROOT/'translation/font_encoding.hex.json');counts={}
for revision in [541,543]:
    rows=read(ROOT/f'translation/terminology_{revision}.review.json')['rows']
    for r in rows:
        assert catalog[r['key']]['translation']==r['after']
        assert TOKEN.findall(r['original'])==TOKEN.findall(r['after'])
        encode_message(r['after'],mapping)
    counts[str(revision)]=len(rows)
write(ROOT/'translation/feedback_543/enemy_verification.json',dict(verified_corrections=counts,
    control_codes_preserved=True,existing_font_encoding_supported=True,packaged=False))
print(counts)
