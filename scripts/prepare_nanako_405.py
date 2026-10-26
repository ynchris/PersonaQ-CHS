"""Nanako confusion, seals and debuffs with childlike wording."""
import hashlib
from collections import defaultdict
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING
from prepare_margaret_393 import IDS
NAMES=['哥哥','副队长','阳介哥哥','千枝姐姐','雪子姐姐','完二哥哥','直斗姐姐','小熊先生','由加莉姐姐','顺平哥哥','真田哥哥','美鹤姐姐','埃癸斯姐姐','乾','小虎','荒垣哥哥','善哥哥和玲姐姐','善哥哥','哥哥','队长']
CONF=['哥哥，振作一点！\n是菜菜子哦？认得吗？','啊，副队长混乱了！\n分不清哪边是敌人了！','阳介哥哥混乱了！\n阳介哥哥，振作一点！','千枝姐姐混乱了……\n一直东张西望的……','雪子姐姐，振作一点！\n还在混乱吗……','完二哥哥混乱了！\n那边才是敌人！','怎么办……\n直斗姐姐混乱了……','小熊先生，不能混乱啊！\n敌人在那边哦！','由加莉姐姐混乱了……\n冷静下来，深呼吸！','哇，顺平哥哥混乱了！\n一会儿朝那边，一会儿朝这边！','啊……真田哥哥，\n混乱了，一直东张西望的……','美鹤姐姐混乱了！\n振作一点！','啊，埃癸斯姐姐，\n好像混乱了……很危险啊！','乾，你混乱了吗？\n敌人在那边！','啊，小虎混乱了！\n尾巴都垂下来了！','荒垣哥哥混乱了，\n好像分不清敌人了……','善哥哥和玲姐姐，\n两个人都混乱了！','善哥哥混乱了！\n快帮他治好！','哥哥，你混乱了吗？\n是菜菜子哦？认得吗？','啊……队长混乱了……\n振作一点！']
PHYS=['哥哥，现在好像只能用\n物理系？……的技能了！','副队长被封印了！\n好像只能用物理系？了。','阳介哥哥被封印了……\n现在好像只能用物理……了。','千枝姐姐现在好像只能用\n物理系？……了哦。','雪子姐姐现在好像只能用\n物理技能？……了！','完二哥哥被封印了！\n好像只能用物理……了哦！','直斗姐姐现在好像只能做\n叫作物理？……的事情了。','小熊先生被封印了！\n只能用物理系？了。','由加莉姐姐现在好像\n只能用物理……？了哦！','顺平哥哥被封印了！\n好像只能用物理？了！','真田哥哥现在好像\n只能用物理系？……了哦。','美鹤姐姐被封印了！\n好像只能用物理？了！','埃癸斯姐姐，\n现在只能用物理系……了！','乾现在被封印了，\n好像只能用物理了哦。','小虎被封印了！\n好像只能用物理系……了！','荒垣哥哥被封印了！\n听说只能用物理？……了！','善哥哥现在好像只能用\n物理系？……了哦！','善哥哥现在好像只能用\n物理系？……了哦！','哥哥！现在被封印了！\n好像只能用物理……了！','队长被封印了！\n好像只能用物理？……了。']
SEAL=['哥哥现在不能躲开，也不能逃跑。\n没事吧？','副队长被封印了！\n不能躲开，也不能逃跑！','阳介哥哥被封印了，\n现在应该不能躲开或逃跑了！','千枝姐姐现在不能躲开或逃跑！\n要小心！','雪子姐姐，要小心！\n现在不能躲开或逃跑！','完二哥哥现在不能躲开，\n也不能逃跑！加油！','直斗姐姐，要小心！\n现在不能躲开或逃跑！','小熊先生被封印了！\n现在不能躲开或逃跑哦！','由加莉姐姐现在不能躲开\n或逃跑，要小心！','顺平哥哥被封印了！\n不能躲开或逃跑！','啊，真田哥哥，\n现在不能躲开或逃跑！','美鹤姐姐现在不能躲开\n或逃跑，要小心！','埃癸斯姐姐，\n现在不能躲开或逃跑哦。','乾现在不能躲开，也不能逃跑。\n忍耐一下！','小虎被封印了……\n这样会全部打中的……','荒垣哥哥被封印了！\n这样会全部打中的……','善哥哥，玲姐姐，\n现在不能躲开或逃跑哦！','善哥哥现在不能躲开或逃跑！\n要小心！','哥哥现在不能躲开，\n也不能逃跑！要小心！','队长现在不能躲开或逃跑，\n要小心！']
DEF_TAIL=['变弱了！要小心！','被降低了……可能会很痛……','变弱了……很危险啊……','被降低了！要小心！','变弱了……','变弱了！会很痛哦！','变弱了！','变弱了！要小心哦！','变弱了……很危险啊！','变弱了！现在很弱哦！','现在变弱了！要小心！','变弱了！','好像被削弱了！','现在变弱了……可能比平时更痛……','变弱了！很危险啊！','现在变弱了！真的哦！','变弱了哦！','现在很弱哦！要注意！','被降低了！要小心！','被降低了！']

def body_for(m,i,k,n):
    if m==61:return CONF[k]+'\n'
    if m==64:return PHYS[k]+'\n'
    if m==65:return SEAL[k]+'\n'
    if m==66:
        if i==18:n='善哥哥'
        if i==4:return '怎么办……雪子姐姐，\n攻击变弱了！\n'
        if i==7:return '直斗姐姐，要小心！\n攻击被削弱了！\n'
        if i==17:return '怎么办……荒垣哥哥的\n攻击变弱了……\n'
        return n+'攻击的力量，\n'+('好像变弱了！' if i in (1,8,10,12,14,15,16) else '被降低了！' if i==20 else '变弱了！')+'\n'
    if m==67:
        if i==4:return '怎么办……雪子姐姐\n保护自己的力量……变弱了……\n'
        if i==7:return '直斗姐姐，很危险啊！\n保护自己的力量变弱了！\n'
        return n+'保护自己的力量，\n'+DEF_TAIL[k]+'\n'
    if m==68:
        if i==2:return '阳介哥哥变慢了。\n变慢了哦——。\n'
        if i==8:return '小熊先生慢慢地动着……\n和平时不一样了……\n'
        if i==11:return '真田哥哥变慢了！\n这也是敌人害的吗？\n'
        if i==16:return '小虎变慢了！\n连菜菜子都能追上了！\n'
        if i==17:return '怎么办……荒垣哥哥，\n动作变慢了！\n'
        if i==20:return '哥哥现在没法动得很快，\n要小心！\n'
        tail='好像没法动得很快了！' if i in (3,4,7,9,12) else '没法动得很快了！' if i==18 else '动作变慢了！'
        if i==7:tail+='要小心！'
        return n+'，\n'+tail+'\n'
    raise AssertionError(m)

def main():
    path=ROOT/'translation/batches/405_nanako_binds_debuffs.generated.json';assert not path.exists()
    rows=read(ROOT/'translation/catalog.working.json');catalog={r['key']:r for r in rows};index=defaultdict(list)
    for r in rows:
        if r.get('translation') and '/battle/support/' in r['source']:index[r['original']].append(r)
    sources=defaultdict(list);audit=[]
    for m in (61,64,65,66,67,68):
        source=f'export_dlc/0009/battle/support/bsv125.bvp_({m:03}).BMD.json';doc=read(ROOT/source)
        for k,(i,n) in enumerate(zip(IDS,NAMES)):
            row=catalog[f'{source}:{i}:0'];assert not row.get('translation');body=body_for(m,i,k,n)
            refs=index.get(row['original'],[])
            if refs and len({r['translation'] for r in refs})==1:
                body=TRAILING.sub('',LEADING.sub('',refs[0]['translation']));audit.append({'key':row['key'],'reference':refs[0]['key']})
            a=TOKEN.sub('',row['original']).splitlines();b=body.splitlines()
            assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),(m,i,max(map(len,b)),max(map(len,a)))
            sources[source].append([i,0,doc['texts'][i]['id'],body])
    write(path,dict(status='draft',sources=dict(sources),source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},reuse_audit=audit,review_notes=['菜菜子六组120页；062/063已复用文本保留。','保留不熟悉物理术语的问句、保护自己的力量等儿童表达；不添加原文未提机制。运行未验证。']))
    print('Pages:',sum(map(len,sources.values())),'exact reuse:',len(audit))

if __name__=='__main__':main()
