"""DLC0006 groups 061--066: confusion, story call and bind/debuff warnings."""
import hashlib
from collections import defaultdict
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING

IDS=[i for i in range(22) if i not in {5,13}]
NAMES=['副队长大人','副队长大人','花村阳介先生','里中千枝小姐','天城雪子小姐','巽完二先生','白钟直斗小姐','小熊大人','岳羽由加莉小姐','伊织顺平先生','真田明彦先生','桐条美鹤小姐','埃癸斯小姐','天田乾先生','虎狼丸大人','荒垣真次郎先生','善大人','善大人','队长大人','队长大人']
TEXT={
61:['副队长大人混乱了……\n请别认错敌人……','副队长大人混乱了。\n……但愿不会袭击过来……','花村阳介先生……竟然混乱了……\n真是令人失望。','里中千枝小姐混乱了。\n哪位能替她治好呢？','天城雪子小姐似乎混乱了。\n敌人也会做这么有趣……麻烦的事！','巽完二先生混乱了。\n请小心别被打中。','此刻的白钟直斗小姐，是混乱王子！\n……是也。','小熊大人混乱了呢……\n太麻烦了，就放着不管吧……','岳羽由加莉小姐混乱了。\n敌人竟做出这么有趣……棘手的事！','伊织顺平先生混乱了呢……\n姐姐大人的耳光或许能治好……','真田明彦先生混乱了。\n但愿他不会袭击过来呢。','桐条美鹤小姐似乎混乱了。\n尽快治好不是更安全么？','埃癸斯小姐混乱了……？\n既然会混乱，那也没办法。嗯。','天田乾先生混乱了。\n但愿不会认错对手……','虎狼丸大人混乱了呢……\n瞧……简直像条疯狗……','荒垣真次郎先生混乱了。\n不快治好，我们也会有危险吧？','善大人……玲小姐……竟同时混乱……\n真是守规矩呢……','善大人混乱了。\n但愿不会袭击过来……','队长大人，您混乱了吗？\n这可有趣……麻烦了……','队长大人，您混乱了吗？\n……确实混乱了吧？真麻烦……'],
62:['这……这是玲的？','嗯，得先让它安静下来！','拜托了！救救玲！！','一定！一定一定！\n要救出玲！'],
63:['前辈的物理技能\n被封住，无法使用了。','副队长的物理攻击\n被封住了。','花村前辈的物理技能\n被封住，无法使用了。','千枝前辈的物理技能\n被封住了！','雪子前辈，现在不能\n使用物理技能哦。','完二的物理技能\n被封住了！','直斗，现在无法进行物理攻击，\n要小心。','小熊的物理技能\n被封住了！','由加莉，已经无法\n进行物理攻击了！','顺平先生的物理攻击\n被封住了！','真田先生，物理攻击\n被封住了哦。','美鹤小姐的物理攻击\n被封住，无法使用了。','埃癸斯，不能使用\n物理攻击哦！要小心。','乾，现在不能\n使用物理技能哦。','虎狼丸的物理技能\n被封住了。','荒垣先生不能进行物理攻击。\n要小心。','善，现在不能进行物理攻击，\n要小心。','善，现在不能进行\n物理攻击，要小心。','前辈，现在不能使用物理技能哦。','队长，现在不能使用\n物理攻击。要小心！'],
66:['副队长大人的攻击力似乎下降了……\n又似乎没有……','副队长大人的攻击力\n下降了。','花村阳介先生的攻击力下降了。\n真是……令人失望……','里中千枝小姐的攻击力下降了。\n是的，降得令人不安……','天城雪子小姐的攻击力下降了呢……\n这可真是……损失惨重……','巽完二先生的攻击力下降了。\n确实下降了吧？','白钟直斗小姐的攻击力下降了。\n大概……也许……多半……','小熊大人的攻击力下降了呢……\n这下不知还能否派上用场……','岳羽由加莉小姐的攻击力\n被降低了呢……','伊织顺平先生的攻击力\n似乎下降了。','真田明彦先生的攻击力\n被降低了呢。','桐条美鹤小姐的攻击力……\n确实下降了吧？','埃癸斯小姐的攻击力下降了……\n机械少女的破坏力竟然……','天田乾先生的攻击力下降了。\n下降了吧？的确下降了。','虎狼丸大人的攻击力下降了……\n难道！自豪的尖牙出问题了！？','荒垣真次郎先生的攻击力……\n一下子降下去了。','善大人的攻击力下降了。\n还请小心。','善大人的攻击力下降了。\n还请小心。','队长大人的攻击力下降了……\n还请小心。','队长大人，\n攻击力被降低了……']}
TEXT[64]=[n+'现在\n只能使用物理攻击。' for n in NAMES]
TEXT[64][2]='很遗憾，花村阳介先生现在\n只能使用物理攻击。'
for i in [10,14]:TEXT[64][IDS.index(i)]=NAMES[IDS.index(i)]+'现在\n只能使用物理攻击，请小心。'
TEXT[65]=[n+'的行动被封住了。\n无法闪避或逃跑！' for n in NAMES]
for i in [0,1,7,17]:TEXT[65][IDS.index(i)]=NAMES[IDS.index(i)]+'现在\n无法闪避或逃跑！'
TEXT[65][2]='很遗憾，花村阳介先生现在\n无法闪避或逃跑！'
TEXT[65][IDS.index(18)]='善大人和玲小姐的行动被封住了……\n现在无法闪避或逃跑。'

def main():
    TEXT[61][IDS.index(7)]='白钟直斗小姐如今是混乱王子！\n……是也。'
    TEXT[63][IDS.index(7)]='直斗，现在不能用物理攻击，\n要小心。'
    target=ROOT/'translation/batches/388_elizabeth_binds.generated.json';assert not target.exists()
    catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')};sources=defaultdict(list)
    for member,values in TEXT.items():
        ids=list(range(4)) if member==62 else IDS
        assert len(values)==len(ids)
        source=f'export_dlc/0006/battle/support/bsv121.bvp_({member:03}).BMD.json';doc=read(ROOT/source)
        for i,body in zip(ids,values):
            row=catalog[f'{source}:{i}:0'];assert not row.get('translation')
            old=row['original'];body+='\n';a=TOKEN.sub('',old).splitlines();b=body.splitlines()
            assert not TOKEN.findall(body)
            assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),(member,i)
            full=LEADING.match(old).group()+body+TRAILING.search(old).group()
            assert TOKEN.findall(full)==TOKEN.findall(old)
            sources[source].append([i,0,doc['texts'][i]['id'],body])
    write(target,dict(status='draft',sources=dict(sources),source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},review_notes=['061—066组非dummy全部处理。062/063原文口吻不同，按原文保留，不擅自改成伊丽莎白敬语。','力封：无法物理攻击；魔封：仅能物理攻击；速封：无法闪避或逃跑。保持三个效果的区别。','相似警告统一术语，保留关键个别评价。未确认全部条目实际触发，未做运行测试。']))
    print('Additional DLC pages:',sum(map(len,sources.values())))

if __name__=='__main__':main()
