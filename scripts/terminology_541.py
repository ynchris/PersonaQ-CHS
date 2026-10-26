"""Source-checked material drop enemy names, aligned with battle name bank."""
import re
from functools import lru_cache
from compile_translation import ROOT,read,write,TOKEN
PATH=ROOT/'translation/terminology_541.review.json'
@lru_cache(maxsize=1)
def entries():
    return {r['key']:r for r in read(PATH)['rows']}
def apply(key,original,value):
    row=entries().get(key)
    if row is None:return value
    assert original==row['original'] and value==row['before'],('Stale enemy terminology',key)
    return row['after']
def prepare():
    if PATH.exists():
        prior=read(PATH)
        assert prior['packaged'] is False
    rows=[];unresolved=[];checked=0
    audited=read(ROOT/'translation/feedback_541/material_enemy_audit.json')
    # Source typo/variant: material text omits ら; battle bank uses 捕らえる者.
    source=read(ROOT/'export_base/init/datmaterialhelp.bmd.json')['texts'][343]['lines'][0]
    assert '討伐：捕える者' in source
    original_before='{F2 05 FF FF}{F1 41}蜘蛛吐出的黏性丝线。\n讨伐：捕捉者\n{00}'
    audited.append(dict(key='export_base/init/datmaterialhelp.bmd.json:343:0',original=source,
        translation=original_before,enemies=[['捕える者','捕获者']]))
    for r in audited:
        if len(r['enemies'])!=1:
            unresolved.append(r);continue
        jp,zh=r['enemies'][0]
        before=r['translation']
        match=re.search(r'讨伐：([^\n{]+)',before)
        source=re.search(r'討伐：([^\n{]+)',r['original'])
        if not match and jp+'が落とした素材。' in r['original']:
            match=re.search(r'([^\n{}]+)掉落的素材。',before)
            source=(None,jp)
        if not match or not source or source[1].strip()!=jp:
            unresolved.append(r);continue
        checked+=1
        if match[1]==zh:continue
        after=before[:match.start(1)]+zh+before[match.end(1):]
        assert TOKEN.findall(before)==TOKEN.findall(after)
        rows.append(dict(key=r['key'],original=r['original'],before=before,after=after,enemy_original=jp,enemy_translation=zh))
    write(PATH,dict(rows=rows,checked_rows=checked,unresolved=unresolved,policy='Battle enemy name bank is authoritative for material drop references.',packaged=False))
    print('Checked:',checked,'Corrections:',len(rows),'Unresolved:',len(unresolved))
    for r in rows:print(r['key'],r['enemy_original'],'->',r['enemy_translation'])
if __name__=='__main__':prepare()
