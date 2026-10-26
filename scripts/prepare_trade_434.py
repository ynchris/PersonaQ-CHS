import hashlib
from collections import defaultdict
from compile_translation import ROOT,read,write,LEADING,TRAILING,TOKEN
from prepare_sklcard_428 import replace_slots

NEW={(0,0):'是的',(0,1):'不需要',(1,0):'，要换吗？\n',(8,0):'哎呀，欢迎光临。\n',(8,1):'进了新商品哦。\n',(9,0):'哎呀，欢迎光临。\n',(10,0):'哎呀，欢迎光临。\n',(10,1):'冒着雨还来光顾，真谢谢你。\n',(11,0):'＞今天已经很晚了。\n　没什么事就回去吧。\n',(18,2):'店里虽然乱糟糟的，\n还是慢慢坐坐吧。\n'}
def main():
    s='export_base/facility/msg_trade.bmd.json';doc=read(ROOT/s)
    target=ROOT/'translation/batches/434_trade_shop_reuse.generated.json';assert not target.exists()
    catalog=read(ROOT/'translation/catalog.working.json');index=defaultdict(list)
    for r in catalog:
        if r.get('translation'):index[r['original']].append(r)
    visible=defaultdict(list)
    for r in catalog:
        if r['source']=='export_base/facility/msg_item.bmd.json' and r.get('translation'):
            visible[TOKEN.sub('',r['original'])].append(r)
    rows=[];audit=[]
    for r in catalog:
        if r['source']!=s or r.get('translation'):continue
        if not any(c in TOKEN.sub('',r['original']) for c in 'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんアイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン'):continue
        from audit_remaining_text import classify
        if classify(r['original'])[0]!='needs_review':continue
        i,j=r['message_index'],r['line_index'];old=r['original']
        refs=index[old];variants={x['translation'] for x in refs}
        if len(variants)==1:
            full=refs[0]['translation'];audit.append(dict(target_key=r['key'],reference_key=refs[0]['key'],original=old,translation=full))
        elif visible[TOKEN.sub('',old)]:
            refs=visible[TOKEN.sub('',old)];variants={TOKEN.sub('',x['translation']) for x in refs}
            assert len(variants)==1
            assert not any(t.startswith(('{F4 45','{F2 44')) for t in TOKEN.findall(old))
            full=replace_slots(old,next(iter(variants)))
            audit.append(dict(target_key=r['key'],reference_key=refs[0]['key'],original=old,translation=full,match='identical visible text from item shop; target controls retained'))
        else:
            assert (i,j) in NEW,('Missing',i,j,TOKEN.sub('',old))
            full=replace_slots(old,NEW[i,j])
        prefix=LEADING.match(old).group();suffix=TRAILING.search(old).group()
        assert full.startswith(prefix) and full.endswith(suffix)
        body=full[len(prefix):len(full)-len(suffix)]
        rows.append([i,j,doc['texts'][i]['id'],body])
    assert len(rows)==93,len(rows)
    write(target,dict(status='draft',sources={s:rows},source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest()},reuse_audit=audit,review_notes=['交易店93页，优先按完整原文/控制码匹配且译文唯一复用，余项补译。旧作语境，不宣称PQ可达。']))
    print('Trade pages:',len(rows),'audited reuse:',len(audit))
if __name__=='__main__':main()
