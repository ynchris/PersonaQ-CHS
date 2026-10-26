"""Frozen source-checked overlay for the user's 破坏属性 terminology."""
from functools import lru_cache
from collections import Counter
import re
from compile_translation import ROOT, read, write, TOKEN

PATH=ROOT/'translation/terminology_473.review.json'
RULES=(('打击属性','破坏属性'),('坏击属性','破坏属性'),('坏属性','破坏属性'),
       ('打击伤害','破坏属性伤害'),('打击耐性','破坏属性耐性'),('（打击）','（破坏属性）'))

@lru_cache(maxsize=1)
def entries():
    return {r['key']:r for r in read(PATH)['rows']}

def apply(key,original,value):
    row=entries().get(key)
    if row is None:return value
    assert original==row['original'] and value==row['before'], ('Stale 473 terminology',key)
    return row['after']

def prepare():
    assert not PATH.exists(), 'Frozen review already exists'
    catalog=read(ROOT/'translation/catalog.working.json')
    rows=[]
    unresolved=[]
    for r in catalog:
        before=r.get('translation') or ''
        if not before:continue
        if not re.search('壊属性|壊耐性',TOKEN.sub('',r['original'])):continue
        after=before
        for old,new in RULES:after=after.replace(old,new)
        if before==after:
            unresolved.append(dict(key=r['key'],original=r['original'],translation=before))
            continue
        assert TOKEN.findall(before)==TOKEN.findall(after)
        rows.append(dict(key=r['key'],original=r['original'],before=before,after=after))
    assert not unresolved, unresolved
    write(PATH,dict(rows=rows,reason='User authorized unifying 壊属性 terminology; ordinary 打击 and single-character 坏 remain unchanged.',packaged=False))
    print('Frozen rows:',len(rows),'DLC:',sum(r['key'].startswith('export_dlc/') for r in rows))

if __name__=='__main__':prepare()
