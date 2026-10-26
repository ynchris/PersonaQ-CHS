"""Nanako analysis and defeat dialogue."""
import hashlib,re,unicodedata
from collections import Counter,defaultdict
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING
TEXT={
69:['那个敌人，\n好像很怕被砍！'],70:['那个敌人呀，\n好像很怕被刺！'],71:['那个敌人怕一种叫作\n坏击属性……？……的东西！'],72:['那个敌人好像很怕热。\n很不耐热吗……'],73:['那个敌人好像不喜欢冷。\n很怕冷吗？'],74:['那个敌人好像很怕\n麻麻的电！'],75:['那个敌人，\n好像很怕强风。'],76:['那个敌人好像很怕刺眼的东西。\n讨厌光吗……'],77:['那个敌人好像很怕黑。\n菜、菜菜子不怕黑哦！'],78:['那个敌人好像很怕一种\n叫作万能属性……的东西。'],79:['敌人还剩１名哦！','敌人只剩１名了哦！'],80:['敌人还剩２名哦！','只剩那些敌人了呢！'],81:['敌人还剩３名！','敌人呀，还剩３名哦！'],82:['剩下的敌人有，\n一名……两名……４名！','敌人还剩４名哦！'],83:['敌人还有５名呢！'],84:['敌人还有６名！'],85:['呜……还有\n好多敌人啊！'],101:['加油！加油！','加油！\n一定能赢的！','菜菜子也来加油！\n加油啊——！'],102:['啊！逃走了！','啊……敌人走掉了……'],
103:['哥哥！！怎么会……不要啊……\n不要丢下菜菜子啊——！！','啊！哥哥！怎么会……\n哥哥……哥哥啊！'],104:['哥哥！！怎么会……不要啊……\n不要丢下菜菜子啊——！！','啊！哥哥！怎么会……\n哥哥……哥哥啊！'],105:['啊！队长！！\n不行……不行啊……不能这样！','队长！！队长……\n队长！！回答我啊！'],106:['啊！副队长！\n怎么会……大家，回答我啊！','副队长！！怎么会……\n大家也？为什么……为什么！'],107:['啊！由加莉姐姐！\n大家！喂！回答我啊！'],108:['啊！顺平哥哥！\n不行啊，大家，快醒醒啊！'],109:['啊！真田哥哥！！\n那、那大家都……怎么会……'],110:['啊！美鹤姐姐！\n大家……不要这样啊！'],111:['乾！怎么会……连乾也……\n不要这样啊……不要啊……！'],112:['啊！小虎！\n那么……大家……大家啊——！'],113:['啊！埃癸斯姐姐！\n这、这样太过分了……太过分了！'],114:['荒垣哥哥！怎么会，谁来……\n谁都……动不了了吗……？喂！'],115:['啊！阳介哥哥！！\n那……大家也……怎么会这样……'],116:['啊！千枝姐姐！！\n谁来……谁来救救大家……谁来！'],117:['怎么会！雪子姐姐！\n那大家都……不行，不能这样！'],118:['完二哥哥！怎么会……\n完二哥哥！谁来啊！！'],119:['小熊先生！怎么会……小熊先生……\n谁来……不要这样啊！'],120:['啊！直斗姐姐！大家……\n不要丢下菜菜子啊——！'],121:['啊，善哥哥，玲姐姐！\n怎么会……不要……不要这样啊！'],122:['啊！善哥哥！！\n那大家也……怎么会……怎么会！']}

def main():
    path=ROOT/'translation/batches/406_nanako_analysis_defeat.generated.json';assert not path.exists()
    rows=read(ROOT/'translation/catalog.working.json');index=defaultdict(list)
    for r in rows:
        if r.get('translation') and '/battle/support/' in r['source']:index[r['original']].append(r)
    sources=defaultdict(list);audit=[];seen=set()
    for r in rows:
        if r.get('translation') or not r['source'].startswith('export_dlc/0009/battle/support/'):continue
        m=int(re.search(r'_\((\d+)\)',r['source'])[1]);i=r['message_index'];j=r['line_index']
        if not 69<=m<=122 or TOKEN.sub('',r['original']).strip()=='ダミーだよ':continue
        body=TEXT[m][i]+'\n';refs=index.get(r['original'],[])
        if refs and len({x['translation'] for x in refs})==1:
            body=TRAILING.sub('',LEADING.sub('',refs[0]['translation']));audit.append({'key':r['key'],'reference':refs[0]['key']})
        a=TOKEN.sub('',r['original']).splitlines();b=body.splitlines()
        assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),(m,i,max(map(len,b)),max(map(len,a)))
        nums=lambda t:Counter(re.findall(r'\d+',unicodedata.normalize('NFKC',TOKEN.sub('',t))))
        assert nums(body)==nums(r['original']);assert j==0
        doc=read(ROOT/r['source']);sources[r['source']].append([i,j,doc['texts'][i]['id'],body]);seen.add((m,i))
    assert len(seen)==50
    write(path,dict(status='draft',sources=dict(sources),source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},reuse_audit=audit,review_notes=['菜菜子分析、剩余敌人数、声援、逃敌和战败50页；保留儿童表达及原文未明示数字的句子。','占位不改，万能弱点不代表确认实际触发；运行未验证。']))
    print('Pages:',len(seen),'exact reuse:',len(audit))

if __name__=='__main__':main()
