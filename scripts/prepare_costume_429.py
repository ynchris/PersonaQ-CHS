import hashlib
from compile_translation import ROOT,read,write,LEADING,TRAILING
from prepare_sklcard_428 import replace_slots

TEXT={0:['是的','不需要'],1:['＞，购买吗？\n'],2:['＞×件，卖出吗？\n'],4:['＞，装备吗？\n'],5:['＞之前装备的\n　，卖掉吗？\n'],11:['＞这套服装是成套的。\n　要让所有人装备这套服装吗？\n']}

def main():
    s='export_base/facility/msg_costume.bmd.json';doc=read(ROOT/s)
    target=ROOT/'translation/batches/429_costume_confirmations.generated.json';assert not target.exists()
    catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')};rows=[]
    for i,lines in TEXT.items():
        for j,plain in enumerate(lines):
            r=catalog[f'{s}:{i}:{j}'];assert not r.get('translation')
            old=r['original'];full=replace_slots(old,plain)
            prefix=LEADING.match(old).group();suffix=TRAILING.search(old).group()
            assert full.startswith(prefix) and full.endswith(suffix)
            body=full[len(prefix):len(full)-len(suffix)]
            assert prefix+body+suffix==full
            rows.append([i,j,doc['texts'][i]['id'],body])
    write(target,dict(status='draft',sources={s:rows},source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest()},review_notes=['服装购买、卖出、装备、替换装备出售及全员套装确认7页。','沿用逐字槽保留策略，动态道具名与数量仍按原顺序输出；8/9/10开发标签及dummy不译。','可能为遗留资源，未验证运行时可达性。']))
    print('Costume confirmations:',len(rows))

if __name__=='__main__':main()
