"""Frozen, source-checked 阿尔卡那 normalization; retain historical drafts."""
from functools import lru_cache
from compile_translation import ROOT,read,write,TOKEN
PATH=ROOT/'translation/terminology_520.review.json'
@lru_cache(maxsize=1)
def entries():
    return {r['key']:r for r in read(PATH)['rows']}
def apply(key,original,value):
    row=entries().get(key)
    if row is None:return value
    assert row['original']==original and row['before']==value,('Stale 520 terminology',key)
    return row['after']
def prepare():
    assert not PATH.exists(),'Review already frozen'
    rows=[]
    for r in read(ROOT/'translation/catalog.working.json'):
        before=r.get('translation') or ''
        if '阿尔卡纳' not in before:continue
        after=before.replace('阿尔卡纳','阿尔卡那')
        assert TOKEN.findall(before)==TOKEN.findall(after)
        rows.append(dict(key=r['key'],original=r['original'],before=before,after=after))
    assert len(rows)==2,len(rows)
    write(PATH,dict(rows=rows,reason='User requires 阿尔卡那 consistently; matches 25 existing message occurrences and one table occurrence. Historical input drafts retained; compiler applies this reviewed overlay.',packaged=False))
if __name__=='__main__':prepare()
