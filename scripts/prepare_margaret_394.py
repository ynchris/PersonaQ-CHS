"""Margaret confusion, seals and debuffs; preserve already reused groups 062/063."""
import hashlib
from collections import defaultdict
from compile_translation import ROOT,read,write,TOKEN
from prepare_margaret_393 import IDS,NAMES

CONFUSION=['……没有人能治好吗……','……但愿不会攻击我们……','似乎已经分不清敌我了。','千枝小姐，敌人在那边。','建议尽早处理。','似乎已经分不清敌我了呢。','请警惕她攻击同伴。','……真是拿小熊先生没办法……','各位有治疗的手段吗？','也许会攻击同伴呢……','请警惕同伴相残。','似乎已经分不清敌我了。','请立即恢复。','……但愿不会攻击同伴……','请警惕它攻击同伴。','请小心他攻击同伴。','建议立即处理。','请警惕他攻击同伴。','扇一巴掌能治好吗……','请警惕同伴相残。']
DEFENSE=['请小心受到的伤害。','还请多加警惕。','请警惕敌人的攻击。','请充分留意受到的伤害。','请小心敌人的攻击。','请小心受到的伤害。','请小心敌人造成的伤害。','请警惕受到的伤害。','请小心受到的伤害。','请千万小心受到的伤害。','请更加警惕受到的伤害。','请小心敌人的攻击。','请警惕敌人的攻击。','恐怕需要警惕受到的伤害。','请小心受到的伤害。','请小心受到的伤害。','请小心受到的伤害。','请警惕敌人的攻击。','请小心受到的伤害。','请小心受到的伤害。']

def body_for(m,i,k,name):
    if m in (64,66) and i==18:name='善先生'
    if m==61:return name+'陷入混乱了。\n'+CONFUSION[k]+'\n'
    if m==64:return name+'被封印了。\n现在只能使用物理攻击。\n'
    if m==65:
        if i==18:return '善先生和玲小姐现在无法\n回避或逃跑。请小心。\n'
        if i==21:return '队长现在无法回避或逃跑。\n请多加小心。\n'
        return name+'的行动被封印了。\n现在无法回避或逃跑。\n'
    if m==66:
        if i==7:return name+'的攻击力下降了。\n还请多加小心。\n'
        if i==8:return name+'的攻击力下降了呢……\n……没问题吗……\n'
        if i in (18,19):return name+'的攻击力下降了。\n恐怕难以像平时那样发挥……\n'
        return name+'的\n'+('攻击力似乎比平时低了。' if i==16 else '攻击力下降了。')+'\n'
    if m==67:return name+'的防御力下降了。\n'+DEFENSE[k]+'\n'
    if m==68:
        if i==6:return name+'的速度下降了。\n……虽然原本也不算快……\n'
        if i in (4,7,9,11,12,19,20):return name+'的速度下降了。\n请多加小心。\n'
        if i in (3,10,15):return name+'的速度下降了。\n'
        return name+'的\n速度下降了。\n'
    raise AssertionError(m)

def main():
    path=ROOT/'translation/batches/394_margaret_binds_debuffs.generated.json';assert not path.exists()
    catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')};sources=defaultdict(list)
    for m in [61,64,65,66,67,68]:
        source=f'export_dlc/0007/battle/support/bsv122.bvp_({m:03}).BMD.json';doc=read(ROOT/source)
        for k,(i,name) in enumerate(zip(IDS,NAMES)):
            row=catalog[f'{source}:{i}:0'];assert not row.get('translation')
            body=body_for(m,i,k,name);a=TOKEN.sub('',row['original']).splitlines();b=body.splitlines()
            assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),(m,i,max(map(len,b)),max(map(len,a)))
            assert not TOKEN.findall(body)
            sources[source].append([i,0,doc['texts'][i]['id'],body])
    write(path,dict(status='draft',sources=dict(sources),source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},review_notes=['玛格丽特六组120页：混乱、魔封、速封、攻击/防御/速度下降。062/063已有共用翻译不覆盖。','保留064/066第18条仅提到善，与其他组善和玲两人有别；保留混乱调侃与速度下降调侃。']))
    print('Margaret binds/debuffs:',sum(map(len,sources.values())))

if __name__=='__main__':main()
