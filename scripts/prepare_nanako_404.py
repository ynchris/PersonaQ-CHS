"""Nanako sleep/paralysis/curse, retaining childlike reactions."""
import hashlib
from collections import defaultdict
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING
from prepare_margaret_393 import IDS
TEXT={
58:['哥哥，醒醒！\n可怕的敌人来了！','醒醒，副队长！\n很危险啊！','真是的，阳介哥哥……\n现在可不是说梦话的时候！','千枝姐姐，醒醒！\n睡在那种地方很危险啊！','雪子姐姐睡着了！\n要怎么才能叫醒她呢……','完二哥哥睡着了！？\n这种时候不能睡觉啊！','直斗姐姐，怎么了！？\n困了吗！？','小熊先生，快醒醒——！\n那里很危险啊！','由加莉姐姐！\n不能睡在那种地方啊！','顺平哥哥，醒醒啊——！\n有可怕的敌人啊——！','啊，真田哥哥，\n睡着了！！','咦！？\n美鹤姐姐睡着了？','不好了，埃癸斯姐姐\n睡着了！','乾，真是的！\n得快点醒来啊！','哇，小虎，\n睡在那种地方很危险啊！','怎么办……荒垣哥哥……\n要怎么才能叫醒他呢……','哇！善哥哥和玲姐姐，\n两个人都睡着了！！','善哥哥，振作一点！\n不能睡觉啊！！','哥哥，醒醒！\n睡在那种地方很危险啊！','咦！？\n队长睡着了！？'],
59:['哥哥，在麻麻的感觉消失前，\n可能没法好好动了……','副队长麻痹了！\n可能没法好好动了……','阳介哥哥，\n麻痹还没好哦。','千枝姐姐的麻痹还没好。\n可能没法好好动了。','雪子姐姐麻痹了。\n要小心！','完二哥哥浑身麻麻的。\n希望还能好好动……','直斗姐姐麻痹了……\n麻痹了该怎么办呢……','小熊先生，没事吧？\n还是没法好好动吗？','由加莉姐姐，\n好像还麻麻的。','顺平哥哥，\n麻痹了，可能动不了……','真田哥哥浑身麻麻的，\n可能没法好好动了……','美鹤姐姐，\n麻痹好像还没好……','埃癸斯姐姐，\n麻痹好像还没好。','乾，没事吧？\n还是麻麻的吗？','小虎麻痹了，\n可能没法好好动了……','荒垣哥哥还是麻麻的。\n可能动不了……','善哥哥和玲姐姐，\n浑身麻麻的，可能动不了！','善哥哥麻痹了！\n可能没法好好动了……','哥哥，还是麻麻的吗？\n能好好动吗？','队长麻痹了！\n可能还是没法好好动！'],
60:['哥哥被诅咒了！？\n快去驱邪吧！','啊，副队长\n被诅咒了！','阳介哥哥被诅咒了……\n以后就不能去朱尼斯了吗？','怎么办……\n千枝姐姐被诅咒了……','雪子姐姐，没事吧？\n不要输给诅咒啊！','完二哥哥被诅咒了！\n这么强也会被诅咒啊……','直斗姐姐被诅咒了！\n得、得驱邪才行！','小熊先生被诅咒了……？\n那毛就会一直长长吗？','啊……由加莉姐姐……\n被诅咒了……','哇……顺平哥哥……\n被诅咒了啊……','真田哥哥被诅咒了……\n……得请人帮忙驱邪……','美鹤姐姐被诅咒了……\n好可怕啊……','埃癸斯姐姐\n被诅咒了……','呜……乾被诅咒了……\n原来真的有诅咒啊……','小虎……被诅咒了……\n好可怜啊……','荒垣哥哥被诅咒了！\n得驱邪才行！','善哥哥和玲姐姐，\n被诅咒了！','善哥哥被诅咒了！\n该、该怎么办？','呜……哥哥被诅咒了……\n该怎么跟爸爸说呢……','啊……队长……\n被诅咒了吗？']}

def main():
    path=ROOT/'translation/batches/404_nanako_statuses_b.generated.json';assert not path.exists()
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
    write(path,dict(status='draft',sources=dict(sources),source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},reuse_audit=audit,review_notes=['菜菜子058—060有效60页；保留麻麻的儿童表达、驱邪及长毛等原文反应。','保留麻痹可能无法行动的不确定性；未加入原文没有的诅咒反噬说明；运行未验证。']))
    print('Pages:',sum(map(len,sources.values())),'exact reuse:',len(audit))

if __name__=='__main__':main()
