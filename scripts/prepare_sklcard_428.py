import re,hashlib
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING

TEXT={
0:['是的','不需要'],1:['，要买吗？\n'],2:['，可以给我吗？\n'],
3:['你手里的技能卡，\n可以全给我吗？\n'],
4:['…嗯，没问题。\n','能复制的技能卡，\n我都列在清单上了。\n'],
5:['那就说说“复制技能卡”，\n简单说明一下吧。\n','把你手里的卡交给我，\n我就能复制出很多张。\n','你会失去１张技能卡，\n但之后想买多少张都行。\n','啊，不过技能卡的效果不同，\n价格也不一样，记住哦。\n','想强化人格面具的话，\n最好多复制些不同的卡。\n'],
6:['，您要购买吗？\n'],7:['，可以交给我吗？\n'],
8:['您持有的技能卡，\n可以全部交给我吗？\n'],
9:['…已经完成了。\n','可以复制的技能卡，\n已全部登记在购买清单中。\n'],
10:['那么，关于“复制技能卡”，\n请容我为您简单说明。\n','只要您交出持有的技能卡，\n我就能为您复制。\n','交出的卡无法归还，\n但此后您可以不限张数地购买。\n','不过，购买时会根据技能卡的效果\n收取相应费用，还请知悉。\n','为了强化人格面具，\n建议您多复制各种技能卡。\n'],
11:['啊…，要买吗？\n'],12:['…，可以给我吗？\n'],
13:['…你手里的卡，\n可以全给我，对吧？\n'],
14:['…弄好了。\n','能复制的技能卡，\n我都列在清单上了…\n'],
15:['…关于“复制技能卡”，\n我简单说明一下。\n','把你手里的卡交给我，\n我就能复制出很多张。\n','…你会失去１张技能卡，\n但之后想买多少张都行。\n','还有…技能卡的效果不同，\n购买时的价格也不一样哦。\n','…就这样。\n']}

def replace_slots(old,plain):
    # Keep all byte-control tokens in their original order and line.
    # Each source glyph slot receives at most one Chinese glyph.
    a=old.split('\n');b=plain.split('\n');assert len(a)==len(b)
    out=[]
    for source,target in zip(a,b):
        parts=re.findall(r'\{[0-9A-F ]+\}|[^{}]',source)
        assert len(target)<=sum(not TOKEN.fullmatch(p) for p in parts),(TOKEN.sub('',source),target)
        pos=0;line=[]
        for p in parts:
            if TOKEN.fullmatch(p):line.append(p)
            else:
                line.append(target[pos:pos+1]);pos+=1
        out.append(''.join(line))
    result='\n'.join(out)
    assert TOKEN.findall(old)==TOKEN.findall(result)
    assert TOKEN.sub('',result)==plain
    return result

def main():
    s='export_base/facility/msg_sklcard.bmd.json';doc=read(ROOT/s)
    target=ROOT/'translation/batches/428_skillcard_copy_dialogue.generated.json';assert not target.exists()
    catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')};rows=[]
    for i,lines in TEXT.items():
        assert len(lines)==len(doc['texts'][i]['lines'])
        for j,plain in enumerate(lines):
            r=catalog[f'{s}:{i}:{j}'];assert not r.get('translation')
            old=r['original'];full=replace_slots(old,plain)
            prefix=LEADING.match(old).group();suffix=TRAILING.search(old).group()
            assert full.startswith(prefix) and full.endswith(suffix)
            body=full[len(prefix):len(full)-len(suffix)] if suffix else full[len(prefix):]
            assert prefix+body+suffix==full
            rows.append([i,j,doc['texts'][i]['id'],body])
    write(target,dict(status='draft',sources={s:rows},source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest()},review_notes=['技能卡复制三套语气共32页。保留全部逐字控制码、换行和动态道具名；空余字槽不填空格。','动态道具名在句首，使用“道具名，要买吗”等顺序；11/12的感叹前缀保留在道具名前。','说明登记卡不可归还、后续不限数量购买及按效果定价。此资源可能包含旧作遗留，未验证运行时可达性。']))
    print('Skill card copy pages:',len(rows))

if __name__=='__main__':main()
