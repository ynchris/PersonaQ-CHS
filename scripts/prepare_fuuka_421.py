"""Fuuka confusion/blindness, binds and debuffs with controlled name templates."""
import hashlib
from collections import defaultdict
from compile_translation import ROOT,read,write,TOKEN
from prepare_margaret_393 import IDS
NAMES=dict(zip(IDS,['副队长','副队长','花村','千枝','雪子','巽','直斗','小熊','由加莉','顺平','真田前辈','桐条前辈','埃癸斯','天田','小虎','荒垣前辈','善','善','队长','队长']))
TEXT={
61:['副队长混乱了。\n请振作！','副队长混乱了！','花村混乱了。\n请打起精神！','千枝混乱了！\n保持清醒！','雪子混乱了！\n请保持清醒！','巽混乱了！\n巽，保持清醒！','直斗混乱了！\n直斗，振作点！','小熊混乱了！\n小熊！打起精神！','由加莉混乱了！\n请振作！','顺平混乱了！\n顺平，振作点！','真田前辈混乱了！请振作，\n敌人在那边！','桐条前辈混乱了！\n请保持清醒！','埃癸斯混乱了！\n得赶快修理……！','天田混乱了！\n振作点！','小虎混乱了！\n不行，敌人在那边！','荒垣前辈混乱了！\n前辈，请瞄准敌人！','善和玲混乱了！\n你们两个，保持清醒！','善混乱了！\n善！保持清醒！','队长，保持清醒！\n敌人在那边！','队长！振作点！\n敌人在那边！'],
62:['副队长的视线被挡住了！\n这样打不中！','副队长的视线被挡住了！\n命中率大幅下降！','花村的视线被挡住了！\n命中精度大幅下降！','千枝看不见前面了！\n这样很难打中！','雪子的视线被挡住了！\n命中精度大幅下降！','巽看不见前面了！\n这样攻击打不中！','直斗的视线被挡住了！\n命中精度大幅下降！','小熊的视线被挡住了！\n命中精度大幅下降！','由加莉看不见前面了！\n命中率大幅下降！','顺平看不见前面了。\n这样攻击打不中！','真田前辈看不见前面了！\n命中率大幅下降！','桐条前辈失去视野了。\n命中率大幅下降！','埃癸斯的视力出现异常。\n命中精度下降！','天田看不见了！\n命中精度大幅下降！','小虎看不见前面了！\n现在这样很难打中！','荒垣前辈看不见前面了。\n命中精度大幅下降！','善的视线被挡住了！\n命中精度大幅下降！','善的视线被挡住了！\n命中精度大幅下降！','队长，能治疗眼睛吗？\n看不见会很不利！','队长！现在这样，\n攻击很难打中！']}

def body_for(m,i,original):
    if m in TEXT:return TEXT[m][IDS.index(i)]+'\n'
    name=NAMES[i]
    if i==18 and m in (65,67,68):name='善和玲'
    if m==63:
        main=name+('的物理攻击被封住了。' if '封じ' in original else '无法使用物理攻击。')
    elif m==64:main=name+'现在只能使用物理'+('技能。' if '技' in original else '攻击。')
    elif m==65:main=name+'无法闪避或'+('撤退。' if '撤退' in original else '逃跑。')
    else:main=name+'的'+{66:'攻击力',67:'防御力',68:'速度'}[m]+('下降了。' if '落ち' in original or '低下' in original or '下がっ' in original else '被降低了。')
    extra=''
    if m==68 and i in (20,21):extra='命中率和闪避率均下降。'
    elif 'ダメージ' in original:extra='请小心受到的伤害。'
    elif '注意' in original or '気をつけ' in original:extra='请小心。'
    old=TOKEN.sub('',original).splitlines();width=max(map(len,old))
    # Split only at a phrase boundary; never increase original page height.
    lines=[main]+([extra] if extra else [])
    if max(map(len,lines))>width and not extra and len(old)>1:
        lines=[name,main[len(name):]]
    assert len(lines)<=len(old) and max(map(len,lines))<=width,(m,i,old,lines)
    return '\n'.join(lines)+'\n'

def main():
    target=ROOT/'translation/batches/421_fuuka_binds_debuffs.generated.json';assert not target.exists()
    catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')};sources=defaultdict(list);seen={}
    for m in range(61,69):
        s=f'export_base/battle/support/bsv108.bvp_({m:03}).BMD.json';doc=read(ROOT/s)
        for i in IDS:
            r=catalog[f'{s}:{i}:0'];assert not r.get('translation');body=body_for(m,i,r['original'])
            a=TOKEN.sub('',r['original']).splitlines();b=body.splitlines()
            assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),(m,i,a,b)
            if r['original'] in seen:assert seen[r['original']]==body
            seen[r['original']]=body;sources[s].append([i,0,doc['texts'][i]['id'],body])
    write(target,dict(status='draft',sources=dict(sources),source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},review_notes=['风花061—068有效160页；混乱/视线手译，其余按逐页审阅的同构短句及称呼生成，非Q2新增复用。','063无法物理攻击，064只能物理攻击，065无法闪避/逃跑；068队长补足命中与闪避同时下降。善/善玲按原文分别保留。未运行验证。']))
    print('Fuuka binds/debuffs:',sum(map(len,sources.values())))

if __name__=='__main__':main()
