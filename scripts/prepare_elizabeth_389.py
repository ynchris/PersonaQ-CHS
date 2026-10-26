"""Complete remaining support pages in DLC0006 members 067--122."""
import hashlib
import re
import unicodedata
from collections import Counter,defaultdict
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING
from prepare_elizabeth_388 import IDS,NAMES

DEF=['降得令人不安。','竟然下降了呢……','降得令人失望……','弹一下额头都会痛不欲生……','可不能大意啊……','摔一跤就会没命似的……','是的，确实如此。','就像没了熊毛一样……','真是让在下都担心起来了。','现在若正面挨上一击……','还请小心。','可能会受到不容小觑的伤害……','……一定。不，几乎可以肯定。','让人忍不住再看一眼……','就像全身的毛都被剃光了。','是的，让周围的人都担心了……','当然，两位都是。','若被直接击中，恐怕会很痛……','是的，简直形同赤裸……','在下认为最好提高警惕。']
SPD=['现为您播报速度下降通知。','请提高警惕。','是的，慢得令人失望。','是的，简直像在打太极拳……','是的，简直像在开玩笑……','是的，慢得令人焦急……','是的，看上三遍都还来得及……','是的……仿佛里面没人了……','是的，慢得令人焦急。','实在是慢得令人焦急。','拳头简直像静止了一样……','是的，让人忍不住想催促……','明明已经充分保养过了……','是的……让人有些无语……','是的，简直像在水里行动……','真田明彦先生很担心您呢。','当然，两位一起……是也。','是的，简直像是故意的。','快进一下才刚刚好呢……','是的，鸟都能停下来啄了……']
TEXT={67:[n+'的防御力下降了。\n'+t for n,t in zip(NAMES,DEF)],68:[n+'的速度下降了。\n'+t for n,t in zip(NAMES,SPD)],
79:['只剩１名。\n仅仅１名而已。','只剩下那个敌人！\n……是也。'],80:['敌人还剩２名。','还剩２名。\n请继续努力。'],81:['敌人还剩３名。','剩余敌人３名。\n现在才刚开始！'],82:['敌人还剩４名……\n还剩不少呢……','如您所见，还剩４名。\n请继续努力。'],83:['敌人还剩５名……\n还早得很呢……'],84:['敌人还剩６名……\n真是难以减少呢……'],85:['敌人仍有很多健在！……是也。'],88:['不行……这敌人不给逃跑的机会！'],89:['要上啦！跳回入口！'],90:['哇！这敌人在妨碍我们！'],91:['我这就调查！','分析得清清楚楚！','全都看穿了！','是什么家伙呢……'],92:['这个敌人已经分析过了哦？'],93:['这样就没问题了！','来治疗啦！','恢复！'],94:['人格面具！','要上啦！','上吧！','我也能！','接招！','预备——！'],95:['强化防御！'],96:['攻击力提升！'],97:['速度提升啦！'],98:['人格面具！'],99:['人格面具！'],100:['抢占先机！'],
101:['各位，\n请鼓足干劲。','让我们迅速收拾掉吧。','这场战斗的结局……\n在下也十分好奇……'],102:['哎呀……\n逃走了呢……','敌人溜之大吉了～。'],103:['队长大人……竟在此结束……\n在下唯有遗憾。','队长大人，您竟止步于此……\n真是令人惋惜……'],104:['队长大人……竟在此结束……\n在下唯有遗憾。','队长大人，您竟止步于此……\n真是令人惋惜……'],105:['队长大人……竟变成这样……\n实在出乎意料……','队长大人……您难道是\n会在这种地方结束的人吗？'],106:['副队长大人的死亡……\n决定了各位的终结……','副队长大人……各位……\n竟然在这种地方结束了……'],107:['岳羽由加莉小姐……还有各位……\n虽很遗憾，还请安息……'],108:['伊织顺平先生……只要您没倒下……\n不……这也是命运吗……'],109:['真田明彦先生……真遗憾……\n原本还想再多看看各位的身姿……'],110:['桐条美鹤小姐……竟会变成这样……\n各位的故事也到此终结了……'],111:['天田乾先生……各位……\n让我们……来日再会吧……'],112:['虎狼丸大人……最后的身姿真英勇……\n请与各位一同安息。'],113:['埃癸斯小姐……竟会如此……\n这也是各位的命运……吗……'],114:['荒垣真次郎先生……真遗憾……\n看来这幕戏……也要结束了……'],115:['花村阳介先生……在下唯有……唯有……\n失望而已。'],116:['里中千枝小姐……竟会变成这样……\n在下唯有遗憾……'],117:['天城雪子小姐……还有各位……\n到此为止了……'],118:['巽完二先生……各位的旅程\n竟以这种形式结束……'],119:['小熊大人……竟在这种地方倒下……\n真是……大失所望……'],120:['白钟直斗小姐……还有各位……\n明明接下来才要变得有趣……'],121:['善大人……玲小姐……\n竟迎来这样的终结……真遗憾……'],122:['善大人……还有各位……很遗憾，\n看来要落幕了……']}
TEXT[67][IDS.index(18)]='善大人和玲小姐的防御力下降了。\n当然，两位都是。'
TEXT[68][IDS.index(18)]='善大人和玲小姐的速度下降了。\n当然，两位一起……是也。'
TEXT[68][0]='叮咚叮咚。现为您播报，\n副队长大人的速度下降了。'
for m,attribute in enumerate(['斩击','突击','坏击','火焰','冰冻','电击','疾风','光','暗','万能'],69):
    TEXT[m]=['那个敌人的弱点是……\n“'+attribute+'属性”。']

def main():
    TEXT[91][1]='分析一清二楚！'
    TEXT[92][0]='这敌人已经分析过了哦？'
    TEXT[93][0]='这样就没问题！'
    TEXT[93][1]='治疗啦！'
    TEXT[117][0]='天城雪子小姐……各位……\n到此为止了……'
    target=ROOT/'translation/batches/389_elizabeth_analysis_defeat.generated.json';assert not target.exists()
    sources=defaultdict(list);seen=set()
    for row in read(ROOT/'translation/catalog.working.json'):
        source=row['source']
        if row.get('translation') or not source.startswith('export_dlc/0006/battle/support/'):continue
        m=int(re.search(r'_\((\d+)\)',source)[1]);i=row['message_index'];j=row['line_index']
        if not 67<=m<=122 or 'ダミー' in row['original']:continue
        pos=IDS.index(i) if m in {67,68} else i
        body=TEXT[m][pos]+'\n';old=row['original'];full=LEADING.match(old).group()+body+TRAILING.search(old).group()
        assert TOKEN.findall(full)==TOKEN.findall(old)
        nums=lambda t:Counter(re.findall(r'\d+',unicodedata.normalize('NFKC',TOKEN.sub('',t))))
        assert nums(full)==nums(old),(m,i)
        a=TOKEN.sub('',old).splitlines();b=body.splitlines()
        assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),(m,i)
        doc=read(ROOT/source);sources[source].append([i,j,doc['texts'][i]['id'],body]);seen.add((m,pos))
    assert seen=={(m,i) for m,rows in TEXT.items() for i in range(len(rows))}
    write(target,dict(status='draft',sources=dict(sources),source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},review_notes=['067—122剩余非dummy提示全部处理；弱点属性、敌人数、下降方向不变。','原文通用支援短句的语气保留，未按容器名称强行改为敬语；万能弱点等可能遗留条目不声称会触发。','运行与语音同步未验证。']))
    print('Additional support pages:',len(seen))

if __name__=='__main__':main()
