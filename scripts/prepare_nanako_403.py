"""Nanako first four status groups; preserve familiar forms of address."""
import hashlib
from collections import defaultdict
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING
from prepare_margaret_393 import IDS
TEXT={
54:['啊！哥哥！！\n哥哥！！哥哥！！','怎么办！副队长，\n倒下了！','不好了！阳介哥哥，\n好像已经动不了了！','啊，千枝姐姐！\n谁、谁来救救她！！','雪子姐姐不动了！\n快、快叫救护车！','完二哥哥倒下了！！\n翻着白眼倒下了！！','啊！直斗姐姐！！\n怎么办……她不动了……','啊！小熊先生，\n振作一点！小熊先生！！','啊！由加莉姐姐，\n倒下了！！','谁、谁来啊！\n救救顺平哥哥！','啊！真田哥哥！\n得、得叫救护车！','不好了！\n美鹤姐姐倒下了！','怎么办……埃癸斯姐姐，\n不动了……','乾出事了！\n他倒下了！','啊，小虎！\n没事吧？小虎！！','哇！荒垣哥哥！\n怎、怎么办……谁来啊！','啊！善哥哥和玲姐姐，\n两个人都倒下了！','不好了！善哥哥，\n倒下了！！','呜哇——！哥哥！\n哥哥啊！','啊！队长！\n谁来救救他！'],
55:['哥哥！伤得好重！\n和菜菜子去保健室吧！','副队长，好像很痛……\n谁来救救他！','阳介哥哥，好像很痛……\n爸爸说过不能勉强！','千枝姐姐摇摇晃晃的……\n没事吧……','谁来救救雪子姐姐！\n好像很痛！','完二哥哥，没事吧？\n好像很痛……','直斗姐姐伤得好重！\n谁带了药？','小熊先生，好像很痛……\n谁来救救他！','由加莉姐姐，没事吧？\n好像很痛……','顺平哥哥好像很痛……\n没事吧……','真田哥哥都站不稳了……\n得包扎一下！','美鹤姐姐好像很难受……\n谁来救救她！','埃癸斯姐姐好像很痛……\n怎么办……','乾，没事吧？\n好像很难受……','小虎好像很难受……\n谁来救救它！','荒垣哥哥伤得好重！\n得请人帮他包扎！','善哥哥和玲姐姐，\n好像很痛……','善哥哥伤得好重……\n得快点涂药……','哥哥！伤得好重！\n去保健室吧！','队长，好像很痛……\n没事吧？'],
56:['呜哇——，\n哥哥变成石头了！','哇，副队长，\n变成石头了！','咦，\n阳介哥哥变成石头了！？','不好了！千枝姐姐，\n变成石头了！','哇，雪子姐姐，\n被变成石头了！','啊……完二哥哥……\n变成石头了……','啊……怎么办……\n直斗姐姐变成石头了……','怎么办……小熊先生……\n变得像摆件一样了……','怎么办……\n由加莉姐姐变成石头了……','不好了……\n顺平哥哥变成石头了！','咦！？真田哥哥，\n变成石头了！？','怎么办……\n美鹤姐姐变成石头了……','不好了！\n埃癸斯姐姐变成石头了！','啊，乾变成石头了！\n该怎么办……','哇，小虎变成石头了……\n像狛犬石像一样了！！','荒垣哥哥被变成石头了……\n吃、吃药能治好吗？','哇，善哥哥和玲姐姐，\n被变成石头了！','善哥哥变成石头了……\n要怎么才能治好？','啊，哥哥变成石头了……\n变成石头了啊！','哇！？队长，\n变成石头了！！'],
57:['哥哥，你真的中毒了吗？\n菜菜子……该怎么办……？','副队长中毒了！\n得快点吃药！','不好了，\n阳介哥哥中毒了！','千枝姐姐中毒了吗？\n没事吧？','雪子姐姐，\n好像中毒了……','啊，完二哥哥，\n中毒后摇摇晃晃的！','怎么办……直斗姐姐，\n中毒了！','小熊先生中毒了！？\n没事吧？','啊，由加莉姐姐，\n中毒了！','顺平哥哥中毒了！\n好像很难受……','啊，真田哥哥中毒了！\n好像很难受……','美鹤姐姐，\n好像中毒了！','怎么办……\n埃癸斯姐姐中毒了！','怎么办……\n乾中毒了！','啊，小虎中毒了……\n谁来救救它！','啊，荒垣哥哥，\n好像中毒了！','善哥哥和玲姐姐，\n中毒后好像很难受……','善哥哥中毒后好像很难受……\n怎么办……','啊，哥哥中毒了！\n怎么办……','啊，队长，\n中毒了！']}

def main():
    path=ROOT/'translation/batches/403_nanako_statuses_a.generated.json';assert not path.exists()
    rows=read(ROOT/'translation/catalog.working.json');catalog={r['key']:r for r in rows};index=defaultdict(list)
    for r in rows:
        if r.get('translation') and '/battle/support/' in r['source']:index[r['original']].append(r)
    sources=defaultdict(list);audit=[]
    for m,values in TEXT.items():
        assert len(values)==20
        source=f'export_dlc/0009/battle/support/bsv125.bvp_({m:03}).BMD.json';doc=read(ROOT/source)
        for i,body in zip(IDS,values):
            row=catalog[f'{source}:{i}:0'];assert not row.get('translation');body+='\n'
            refs=index.get(row['original'],[])
            if refs and len({r['translation'] for r in refs})==1:
                body=TRAILING.sub('',LEADING.sub('',refs[0]['translation']));audit.append({'key':row['key'],'reference':refs[0]['key']})
            a=TOKEN.sub('',row['original']).splitlines();b=body.splitlines()
            assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),(m,i,max(map(len,b)),max(map(len,a)))
            sources[source].append([i,0,doc['texts'][i]['id'],body])
    write(path,dict(status='draft',sources=dict(sources),source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},reuse_audit=audit,review_notes=['菜菜子054—057有效80页；保留哥哥/姐姐称呼和救护车、保健室等原文反应。','占位保留；石化台词不表示确认运行触发，运行未验证。']))
    print('Pages:',sum(map(len,sources.values())),'exact reuse:',len(audit))

if __name__=='__main__':main()
