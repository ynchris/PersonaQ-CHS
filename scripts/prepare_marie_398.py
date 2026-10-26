"""Marie sleep, paralysis and curse; do not replace character lines with mechanics."""
import hashlib
from collections import defaultdict
from compile_translation import ROOT,read,write,TOKEN
from prepare_margaret_393 import IDS
TEXT={
58:['副队长睡着了。\n没人能叫醒他吗？','哇！副队长睡着了……\n那里很危险啊！','阳介睡着了……\n还在说梦话。','千枝睡着了。\n……还摆着架势。','咦……雪子睡着了……\n话说，这不危险吗？','啊……完二睡着了……\n不管他没问题吗？','直斗睡着了。\n现在被盯上就糟透了。','小熊睡着了……\n这就是冬眠吗？','由加莉，你在睡觉！？\n被盯上就不妙了吧！？','咦！？顺平睡着了？\n就在那儿！？','真田……\n站着睡着了……','美鹤睡着了？\n在那种地方！？','哇……埃癸斯睡着了……\n……明明是机器人……','咦！？\n乾睡着了！？','哇……狗狗睡着了……\n……话说，好可爱……','荒垣睡着了。\n谁能叫醒他？','善和玲睡着了……\n那里很危险吧？很危险对吧？','善睡着了，没问题吗？\n肯定有问题吧？','咦！？你在睡觉！？\n等等，很危险啊！','队、队长，\n现在可不是睡觉的时候！'],
59:['副队长还在麻痹。\n也许动不了。','副队长还在麻痹。\n不知道能不能动。','阳介麻痹了。\n也许动不了哦。','千枝的麻痹还没好。\n也许动不了哦。','雪子还能动吗……\n麻痹还没好呢。','完二还在麻痹。\n也许动不了哦。','直斗麻痹了。\n还能动吗……','小熊的麻痹还没好。\n还能动吗……','由加莉的麻痹还没好。\n也许动不了哦。','顺平的麻痹还没好。\n也许动不了哦。','真田还在麻痹。\n也许动不了呢……','美鹤也许动不了哦。\n麻痹还没好呢。','原来埃癸斯也会麻痹……\n那也许就动不了了。','乾的麻痹还没好。\n也许动不了。','狗狗还在麻痹。\n也许动不了哦。','荒垣的麻痹还没好。\n也许动不了哦。','善和玲麻痹了。\n不知道能不能动。','善的麻痹还没好。\n不知道能不能动哦。','你的麻痹还没好吧？\n能动吗？','队长还在麻痹？\n也许动不了哦。'],
60:['副队长被诅咒了？怎、怎么可能，\n诅咒都是虚构，都是都市传说！','副队长被诅咒了？那、那种东西，\n诅咒都是迷信，怎么可能有……','阳介被诅咒了？诅、诅咒怎么可能\n存在，肯定是自己想太多了……','千枝被诅咒了？怎、怎么可能，\n诅咒根本不存在……大概……','雪子被诅咒了？诅、诅咒怎么可能\n存在，肯定都是想象出来的。','完二被诅咒了？我、我才不信诅咒，\n都是迷信，都是都市传说……','直斗被诅咒了？诅、诅咒怎么可能\n存在，肯定是自己想太多了……','小熊被诅咒了？诅、诅咒怎么可能\n存在，肯定是自己想太多了……','由加莉被诅咒了？诅、诅咒都是\n迷信什么的，怎么可能有……对吧？','顺平被诅咒了？怎、怎么可能，\n诅咒都是迷信……','真田被诅咒了？我、我才不信诅咒，\n怎么可能有，肯定……','美鹤被诅咒了？那、那肯定只是\n错觉啦，诅咒什么的……','埃癸斯被诅咒了？\n话说，机器人也会被诅咒吗？','乾被诅咒了？诅、诅咒根本不存在，\n肯定只是错觉……','狗狗被诅咒了？诅、诅咒怎么可能有，\n都是迷信，才不可怕……','荒垣被诅咒了？怎、怎么可能，\n诅咒都是迷信，大概……','善和玲被诅咒了？怎、怎么可能，\n诅咒根本不存在……','善被诅咒了？诅、诅咒怎么可能存在，\n都是迷信，都是自己想太多……','你被诅咒了？诅、诅咒怎么可能有，\n都是自己想太多，都是迷信……','队长被诅咒了？诅、诅咒怎么可能有……\n我才不信……']}

def main():
    path=ROOT/'translation/batches/398_marie_statuses_b.generated.json';assert not path.exists()
    catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')};sources=defaultdict(list)
    for m,values in TEXT.items():
        assert len(values)==20
        source=f'export_dlc/0008/battle/support/bsv124.bvp_({m:03}).BMD.json';doc=read(ROOT/source)
        for i,body in zip(IDS,values):
            row=catalog[f'{source}:{i}:0'];assert not row.get('translation');body+='\n'
            a=TOKEN.sub('',row['original']).splitlines();b=body.splitlines()
            assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),(m,i,max(map(len,b)),max(map(len,a)))
            sources[source].append([i,0,doc['texts'][i]['id'],body])
    write(path,dict(status='draft',sources=dict(sources),source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},review_notes=['玛丽058—060有效60页；5/13占位保留。','复用既有人名和状态术语；现有战斗导航可见原文精确匹配为零，独有台词重新翻译。','诅咒台词保留嘴硬否认语气，不替换成其他导航的机制警告。未运行验证。']))
    print('Marie statuses:',sum(map(len,sources.values())))

if __name__=='__main__':main()
