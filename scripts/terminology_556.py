"""User-approved StreetPass attachment wording, exact two message contexts."""
from functools import lru_cache
from compile_translation import ROOT,read,write,TOKEN
PATH=ROOT/'translation/terminology_556.review.json'
@lru_cache(maxsize=1)
def entries():return {r['key']:r for r in read(PATH)['rows']}
def apply(key,original,value):
    row=entries().get(key)
    if row is None:return value
    assert row['original']==original and row['before']==value,('Stale sharing correction',key)
    return row['after']
def prepare():
    assert not PATH.exists(),'Frozen review exists'
    catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')};rows=[]
    for mi in [216,217]:
        key=f'export_base/facility/msg_combine.bmd.json:{mi}:1';r=catalog[key]
        before=r['translation'];old='比如更换\n附在手册里发出的人格面具…'
        assert old in before
        after=before.replace(old,'比如更换附在手册中、\n用于分享的人格面具……')
        assert TOKEN.findall(before)==TOKEN.findall(after)
        rows.append(dict(key=key,original=r['original'],before=before,after=after))
    write(PATH,dict(rows=rows,policy='User approved 更换人格面具 / 分享人格面具 and matching help text.',packaged=False))
if __name__=='__main__':prepare()
