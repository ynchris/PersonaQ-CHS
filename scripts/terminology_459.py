"""User-approved place-name overlay, checked against exact prior translations."""
from functools import lru_cache
from compile_translation import ROOT,read,write,TOKEN

PATH=ROOT/'translation/terminology_459.review.json'

@lru_cache(maxsize=1)
def entries():
    return {(r['scope'],r['key']):r for r in read(PATH)['rows']}

def apply(scope,key,value):
    row=entries().get((scope,str(key)))
    if row is None:return value
    assert value==row['before'],('Stale terminology input',scope,key)
    return row['after']

def prepare():
    assert not PATH.exists(), 'Review is a frozen snapshot; do not regenerate from amended outputs.'
    groups=[('messages',read(ROOT/'translation/catalog.working.json')),
            ('tables',read(ROOT/'translation/tables.catalog.working.json')),
            ('schoolwalk',read(ROOT/'translation/schoolwalk_names.review.json')['rows'])]
    rows=[]
    for scope,data in groups:
        for r in data:
            before=r.get('translation') or ''
            if '钟楼' not in before:continue
            after=before.replace('钟楼','时钟塔')
            assert TOKEN.findall(before)==TOKEN.findall(after)
            rows.append(dict(scope=scope,key=str(r['index'] if scope=='schoolwalk' else r['key']),
                             original=r['original'],before=before,after=after))
    write(PATH,dict(rows=rows,reason='User approved 时钟塔 for the place name, including dialogue and menus.',
                   code_policy='Executable floors and shared suffix handled by code_extra_458 review.',packaged=False))
    print('Terminology rows:',len(rows))

if __name__=='__main__':prepare()
