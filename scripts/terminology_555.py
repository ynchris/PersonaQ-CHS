"""Unify NPC boss banks with existing dialogue and speaker names."""
from functools import lru_cache
from compile_translation import ROOT,read,write,TOKEN
PATH=ROOT/'translation/terminology_555.review.json'
@lru_cache(maxsize=1)
def review():return read(PATH)
def apply(key,original,value):
    row=next((r for r in review()['messages'] if r['key']==key),None)
    if row is None:return value
    assert row['original']==original and row['before']==value,('Stale NPC message',key)
    return row['after']
def apply_bank(source,row):
    match=next((r for r in review()['bank'] if r['source']==source and r['index']==row['index']),None)
    if match:
        assert row['original']==match['original'] and row['translation']==match['before']
        row['translation']=match['after'];row['local_name_consistency_revision']=555
def prepare():
    assert not PATH.exists(),'Frozen review already exists'
    bank=[];messages=[]
    for g in read(ROOT/'translation/q2_name_banks.review.generated.json')['groups']:
        if g['source']!='battle/table/enemynametable.tbl':continue
        for r in g['rows']:
            target={'エリザベス':'伊丽莎白','テオドア':'迪奥多'}.get(r['original'])
            if target and r['translation']!=target:
                bank.append(dict(source=g['source'],index=r['index'],original=r['original'],before=r['translation'],after=target))
    for r in read(ROOT/'translation/catalog.working.json'):
        before=r.get('translation') or ''
        if '西奥多' not in before:continue
        assert 'テオ' in r['original']
        target='迪奥多' if 'テオドア' in r['original'] else '迪奥'
        after=before.replace('西奥多',target)
        assert TOKEN.findall(before)==TOKEN.findall(after)
        messages.append(dict(key=r['key'],original=r['original'],before=before,after=after))
    assert len(bank)==7 and len(messages)==7,(len(bank),len(messages))
    write(PATH,dict(bank=bank,messages=messages,policy='Existing dialogue names: 伊丽莎白 / 迪奥多; テオ nickname: 迪奥.',packaged=False))
if __name__=='__main__':prepare()
