"""Exact-context enemy-name corrections outside the material descriptions."""
from functools import lru_cache
from compile_translation import ROOT,read,write,TOKEN
PATH=ROOT/'translation/terminology_543.review.json'
ALIASES={
 '刈り取る者':['猎杀者'], 'おまつり野郎':['祭典狂人','祭典混混'],
 'フェイトサーチャー':['命运搜索者','命运探寻者'], 'マッハフォート':['马赫堡垒'],
 'バスタードライブ':['破坏驱动者'], '憤怒のキュクロプス':['愤怒的独眼巨人'],
 '古ぼけたお人形さん':['老旧娃娃','破旧的人偶'], '恋の使者':['恋爱使者'],
}
@lru_cache(maxsize=1)
def entries():return {r['key']:r for r in read(PATH)['rows']}
def apply(key,original,value):
    row=entries().get(key)
    if row is None:return value
    assert original==row['original'] and value==row['before'],('Stale enemy correction',key)
    return row['after']
def prepare():
    if PATH.exists():assert read(PATH)['packaged'] is False
    catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')}
    rows=[];unresolved=[]
    for candidate in read(ROOT/'translation/feedback_543/enemy_candidates.json'):
        enemy=candidate['enemy']
        if enemy not in ALIASES:continue
        r=catalog[candidate['key']];before=r['translation'];after=before
        for alias in ALIASES[enemy]:after=after.replace(alias,candidate['expected'])
        if before==after:unresolved.append(candidate);continue
        assert TOKEN.findall(after)==TOKEN.findall(before)
        rows.append(dict(key=r['key'],original=r['original'],before=before,after=after,enemy_original=enemy,enemy_translation=candidate['expected']))
    assert len({r['key'] for r in rows})==len(rows)
    write(PATH,dict(rows=rows,unresolved=unresolved,packaged=False,policy='Only enemy names verified in original text, aligned to battle bank. Named NPC boss variants require separate dialogue/speaker consistency review.'))
    print('Corrections',len(rows),'unresolved',len(unresolved))
    for r in unresolved:print(r)
if __name__=='__main__':prepare()
