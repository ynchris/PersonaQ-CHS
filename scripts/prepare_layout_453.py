"""Whole-queue conservative punctuation reflow and reviewed compact help text."""
import re,sys
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING
from audit_layout_metrics import measure,font_width_functions
from prepare_reflow_452 import wrap_line

HELP={
20:'对１列敌人造成２～３次\n少量疾风属性伤害。\n',
32:'对所有敌人造成２～４次\n中量冰冻属性伤害。\n',
47:'对所有敌人造成６次\n大量电击属性伤害。\n',
168:'《物理》对所有敌人造成５～７次\n中量斩击属性伤害。\n',
220:'战斗中，消除１列同伴的\n全部能力降低效果。\n',
340:'《情报支援用》选目标时显示\n攻击是否有效。未知耐性时无效。\n',
406:'回合结束时少量恢复自身与\n同列同伴的ＨＰ，持续３回合。\n',
415:'同列同伴攻击时，追击其目标，\n持续３回合。\n',
356:'《情报支援用》３回合内\n提升所有同伴的攻击力。\n',
357:'《情报支援用》３回合内\n提升所有同伴的防御力。\n',
380:'《情报支援用》迷宫中每走一步，\n少量恢复所有同伴的ＨＰ。\n',
381:'《情报支援用》迷宫中每走一步，\n恢复所有同伴的ＨＰ。\n',
382:'《情报支援用》迷宫中每走一步，\n少量恢复所有同伴的ＳＰ。\n',
332:'《情报支援用》提升稀有素材概率，\n并有时增加采集次数。\n',
}
for i,effect in [(83,'混乱'),(85,'中毒'),(87,'失明'),(89,'睡眠'),(91,'诅咒')]:
    HELP[i]=f'１名敌人中等概率\n陷入{effect}。\n'
    HELP[i+1]=f'所有敌人中等概率\n陷入{effect}。\n'


def restore_controls(old_body,new_plain):
    """Place zero-width color tokens at exactly the same visible-character index."""
    assert TOKEN.sub('',old_body).replace('\n','')==new_plain.replace('\n','')
    controls={};offset=0
    for part in re.split('('+TOKEN.pattern+')',old_body):
        if TOKEN.fullmatch(part):controls.setdefault(offset,[]).append(part)
        else:offset+=len(part.replace('\n',''))
    result=[];offset=0
    for char in new_plain:
        if char!='\n':
            result.extend(controls.pop(offset,[]));offset+=1
        result.append(char)
    result.extend(controls.pop(offset,[]));assert not controls
    return ''.join(result)


def main():
    audit=ROOT/'translation/layout_453.review.json';assert not audit.exists()
    path=ROOT/'translation/text_corrections.review.json';prior=read(path);existing={r['key'] for r in prior['rows']}
    catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')};widths=font_width_functions();selected=[]
    for warning in read(ROOT/'translation/progress.generated.json')['warnings']:
        if warning['kind']!='layout_review':continue
        row=catalog[warning['key']]
        if row['key'] in existing or row['message_id'].startswith('SEL'):continue
        before=row['translation'];pre=LEADING.match(before).group();suf=TRAILING.search(before).group()
        body=before[len(pre):len(before)-len(suf)] if suf else before[len(pre):]
        if any(not re.fullmatch(r'\{F2 01 [0-9A-F]{2} 01\}',t) for t in TOKEN.findall(body)):continue
        old_measure=[measure(row['original'],f[0]) for f in widths.values()]
        if any(m['missing'] for m in old_measure):continue
        plain=TOKEN.sub('',body);old_lines=TOKEN.sub('',row['original']).splitlines()
        if not 2<=len(old_lines)<=5 or '\n\n' in plain:continue
        functions=[f[1] for f in widths.values()];caps=[m['max_width'] for m in old_measure]
        if any(f(c) is None for c in plain if c!='\n' for f in functions):continue
        manual=row['source']=='export_base/init/datskillhelp.bmd.json' and row['message_index'] in HELP
        if manual:
            assert not TOKEN.search(body)
            candidate=HELP[row['message_index']]
        else:
            lines=wrap_line(plain.replace('\n',''),functions,caps)
            if lines is None:continue
            candidate='\n'.join(lines)+ ('\n' if plain.endswith('\n') else '')
            candidate=restore_controls(body,candidate)
        after=pre+candidate+suf
        if before==after or len(TOKEN.sub('',after).splitlines())>len(old_lines):continue
        if any(measure(after,f)['max_width']>cap for f,cap in zip(functions,caps)):continue
        assert TOKEN.findall(before)==TOKEN.findall(after)
        selected.append(dict(key=row['key'],original=row['original'],before=before,after=after,
                             reason='453精简技能说明，保留对象/次数/回合/效果' if manual else '453全队列标点换行，字词和控制码位置不变',
                             newline_only=not manual))
    print('Candidates:',len(selected),'manual skill help:',sum(not r['newline_only'] for r in selected))
    for row in selected[:12]:print(row['key'],repr(TOKEN.sub('',row['after'])))
    if '--apply' in sys.argv:
        write(audit,dict(rows=selected,runtime_tested=False))
        prior['rows'].extend(selected);write(path,prior)


if __name__=='__main__':main()
