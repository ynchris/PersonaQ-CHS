"""Context-bound storage-slot terminology; never replace geographical 处."""
from functools import lru_cache
from compile_translation import ROOT, read, write, TOKEN
PATH=ROOT/'translation/terminology_554.review.json'

@lru_cache(maxsize=1)
def entries():
    return {r['key']:r for r in read(PATH)['rows']}

def apply(key,original,value):
    r=entries().get(key)
    if r is None:return value
    assert original==r['original'] and value==r['before'],('Stale storage correction',key)
    return r['after']

def prepare():
    rows=[];audit=[]
    for r in read(ROOT/'translation/catalog.working.json'):
        old=r.get('translation') or '';jp=r['original'];mid=r.get('message_id','')
        if any(s in jp for s in ['か所','箇所','ヶ所','カ所']) or ('寄存' in old and any(s in old for s in ['空位','空间','格','处'])):
            audit.append(dict(key=r['key'],message_id=mid,original=jp,translation=old))
        if r['source']!='export_base/facility/msg_weapon.bmd.json':continue
        new=old
        if mid in ('WSHOP_EXP_CLOAKROOM_T','WSHOP_EXP_CLOAKROOM_M'):
            new=new.replace('准备了大约“９９处”\n存放物品的空间。','准备了大约“９９格”\n储物空间。')
            new=new.replace('每１处空间可存放','每１格可存放')
        if mid in ('CSHOP_COMMON_NG_1','CSHOP_COMMON_NG_1_Ex','CSHOP_COMMON_NG_4','CSHOP_COMMON_NG_4_Ex'):
            new=new.replace('已经没有空位','已经没有空储物格').replace('这里的空间已满','这里的储物格已满').replace('这里的空间已经满了','这里的储物格已经满了')
        if new!=old:
            assert TOKEN.findall(old)==TOKEN.findall(new)
            rows.append(dict(key=r['key'],original=jp,before=old,after=new))
    assert len(rows)==8,len(rows)
    write(PATH,dict(rows=rows,policy='Storage slots 格; item quantity 个; geographical counters unchanged',packaged=False))
    write(ROOT/'translation/previews_554/storage_audit.json',audit)
    print('Storage terminology corrections:',len(rows),'context candidates:',len(audit))

if __name__=='__main__':prepare()
