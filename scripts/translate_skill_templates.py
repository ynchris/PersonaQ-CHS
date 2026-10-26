"""Expand reviewed PQ effect-description sentence templates into indexed drafts.

Only whole sentences match, and only the inspected first 280 skill records.
Unmatched descriptions and internal placeholders remain untranslated.
"""
import re
from pathlib import Path
from compile_translation import read, write, LEADING, TRAILING

ROOT=Path(__file__).resolve().parent
TARGET={'１体':'１名敌人','全体':'所有敌人','１列':'１列敌人'}
ALLY={'１体':'１名同伴','全体':'所有同伴','１列':'１列同伴'}
ATTR={'火炎':'火炎','氷結':'冰冻','電撃':'电击','疾風':'疾风','万能':'万能','斬':'斩击','壊':'打击','突':'突刺'}
SIZE={'小':'少量','中':'中量','大':'大量','特大':'巨量'}
CHANCE={'低':'低','中':'中等','高':'高'}
STATUS={'毒':'中毒','混乱':'混乱','盲目':'失明','睡眠':'睡眠','呪い':'诅咒','麻痺':'麻痹','力封じ':'力封印','魔封じ':'魔封印','速封じ':'速封印'}

def translate(body):
    compact=body.replace('\n','')
    physical=compact.startswith('《物理》')
    if physical:
        compact=compact[len('《物理》'):]
    prefix='《物理》\n' if physical else ''
    m=re.fullmatch(r'敵(１体|全体|１列)に(火炎|氷結|電撃|疾風|万能|斬|壊|突)(?:＋(火炎|氷結|電撃|疾風))?属性の(小|中|大|特大)ダメージを(与える。|[０-９～]+回与える。)',compact)
    if m:
        target,attr,extra,size,ending=m.groups()
        attack=ATTR[attr]+('＋'+ATTR[extra] if extra else '')
        repeats=ending.removesuffix('回与える。')+'次' if ending!='与える。' else ''
        return prefix+f'对{TARGET[target]}造成{repeats}{SIZE[size]}{attack}属性伤害。\n'
    m=re.fullmatch(r'敵(１体|全体|１列)に(火炎|氷結|電撃|疾風|万能|斬|壊|突)属性の(小|中|大|特大)ダメージを与え、(.+)',compact)
    if m:
        target,attr,size,tail=m.groups()
        endings={'対象の隣にも拡散ダメージを与える。':'并对相邻目标造成扩散伤害。',
                 '後列の敵にも貫通ダメージを与える。':'并对后排敌人造成贯穿伤害。',
                 '中確率で敵をダウンさせる。':'并以中等概率使敌人倒地。',
                 '中確率で対象をダウンさせる。':'并以中等概率使目标倒地。'}
        for jp,zh in STATUS.items():
            endings[f'中確率で{jp}効果を与える。']=f'并以中等概率附加{zh}效果。'
        if tail in endings:
            return ('《物理》' if physical else '')+f'对{TARGET[target]}造成{SIZE[size]}{ATTR[attr]}伤害，\n'+endings[tail]+'\n'
    m=re.fullmatch(r'敵(１体|全体)に(低|中|高)確率で(光|闇)属性の即死効果を与える。',compact)
    if m:
        target,chance,attr=m.groups()
        return f'以{CHANCE[chance]}概率对{TARGET[target]}\n施加'+('光' if attr=='光' else '暗')+'属性即死效果。\n'
    m=re.fullmatch(r'敵(１体|全体)に(低|中|高)確率で(.+)効果を与える。',compact)
    if m and m[3] in STATUS:
        return f'以{CHANCE[m[2]]}概率对{TARGET[m[1]]}\n附加{STATUS[m[3]]}效果。\n'
    m=re.fullmatch(r'(戦闘中、)?味方(１体|全体|１列)のＨＰを(小|中|全)回復する。',compact)
    if m:
        lead='战斗中，' if m[1] else ''
        return lead+{'小':'少量恢复','中':'中量恢复','全':'完全恢复'}[m[3]]+ALLY[m[2]]+'的ＨＰ。\n'
    m=re.fullmatch(r'(戦闘中、)?味方(１体|全体|１列)の(状態異常|封じ)を治療する。',compact)
    if m:
        return ('战斗中，' if m[1] else '')+'解除'+ALLY[m[2]]+'的'+('异常状态' if m[3]=='状態異常' else '封印')+'。\n'
    m=re.fullmatch(r'(戦闘中、)?味方(１体|全体|１列)の弱体効果を全て打ち消す。',compact)
    if m:
        return ('战斗中，' if m[1] else '')+'消除'+ALLY[m[2]]+'的全部能力降低效果。\n'
    return None

def main():
    source='export_base/init/datskillhelp.bmd.json'
    doc=read(ROOT/source)
    rows=[]
    for mi,msg in enumerate(doc['texts'][:280]):
        for li,old in enumerate(msg['lines']):
            body=TRAILING.sub('',LEADING.sub('',old))
            new=translate(body)
            if new is not None:
                rows.append([mi,li,msg['id'],new])
    write(ROOT/'translation/batches/005_skill_templates.generated.json',{
        'status':'draft_PQ_effect_templates_pending_layout_review',
        'generator':'translate_skill_templates.py', 'sources':{source:rows}})
    print(f'{len(rows)} exact-template skill description drafts generated')

if __name__=='__main__':
    main()
