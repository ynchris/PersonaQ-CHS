"""Conservative newline-only reflow of collapsed static dialogue paragraphs."""
import sys
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING
from audit_layout_metrics import font_width_functions,measure

FORBIDDEN_START=set('，。！？、：；）》】」』…,.!?;:)]}')
FORBIDDEN_END=set('（《【「『([{')
AUTHORED={
    '＞玛格丽特露出完成了一件大事般的笑容……\n':'＞玛格丽特露出\n完成了一件大事般的\n笑容……\n',
    '＞在不太安稳的气氛中，茶会开始了……\n':'＞在不太安稳的气氛中，\n茶会开始了……\n',
    '＞好不容易绽放的花朵落在了泥土上……\n':'＞好不容易绽放的花朵\n落在了泥土上……\n',
    '＞和伙伴们度过了一段愉快的时光……\n':'＞和伙伴们度过了\n一段愉快的时光……\n',
    '＞美鹤似乎对不习惯的身份感到困惑……\n':'＞美鹤似乎对不习惯的\n身份感到困惑……\n',
    '现在，就让您见证研究的最终成果……\n':'现在，就让您见证\n研究的最终成果……\n',
    '＞顺平、由加莉和阳介正在玩打靶……\n':'＞顺平、由加莉和阳介\n正在玩打靶……\n',
    '总觉得最近，\n我和大家的实力差距越来越大了……\n':'总觉得最近，\n我和大家的实力差距\n越来越大了……\n',
    '是因为冷吗？\n还是说，里面装着什么重要的东西……\n':'是因为冷吗？\n还是说，里面装着\n什么重要的东西……\n',
    '＞真田和天田再次迈开了脚步……\n':'＞真田和天田\n再次迈开了脚步……\n',
}


def valid_break(text,pos):
    if pos==len(text):return True
    if text[pos] in FORBIDDEN_START or text[pos-1] in FORBIDDEN_END:return False
    if text[pos-1].isascii() and text[pos].isascii() and text[pos-1].isalnum() and text[pos].isalnum():return False
    # Do not split Chinese words blindly. Automated candidates are limited to
    # punctuation/whitespace; longer unpunctuated clauses need authored breaks.
    return text[pos-1] in '，。！？；：、' or text[pos-1].isspace()


def wrap_line(text,widths,caps):
    result=[]
    while text:
        accepted=[]
        for end in range(1,len(text)+1):
            if any(sum(fn(c) for c in text[:end])>cap for fn,cap in zip(widths,caps)):break
            if valid_break(text,end):accepted.append(end)
        if not accepted:return None
        end=accepted[-1]
        # Prefer natural punctuation near the furthest allowable break.
        natural=[i for i in accepted if i>=end*0.75 and text[i-1] in '，。！？；：、']
        if end<len(text) and natural:end=natural[-1]
        result.append(text[:end]);text=text[end:]
    return result or ['']


def main():
    path=ROOT/'translation/text_corrections.review.json'
    previous=read(path);existing={r['key'] for r in previous['rows']}
    audit_path=ROOT/'translation/reflow_452.review.json'
    assert not audit_path.exists(), 'Do not silently regenerate reviewed reflow'
    metrics=font_width_functions();selected=[]
    catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')}
    for warning in read(ROOT/'translation/progress.generated.json')['warnings']:
        if warning['kind']!='layout_review':continue
        row=catalog[warning['key']]
        if row['key'] in existing or not row['source'].startswith('export_base/event/'):continue
        before=row['translation'];plain=TOKEN.sub('',before)
        old_lines=TOKEN.sub('',row['original']).splitlines()
        if not 2<=len(old_lines)<=3 or len(plain.splitlines())>=len(old_lines):continue
        pre=LEADING.match(before).group();suf=TRAILING.search(before).group()
        body=before[len(pre):len(before)-len(suf)] if suf else before[len(pre):]
        if TOKEN.search(body):continue  # dynamic variables and embedded controls require manual placement
        measured=[measure(row['original'],f[0]) for f in metrics.values()]
        if any(r['missing'] for r in measured):continue
        new_widths=[f[1] for f in metrics.values()];caps=[r['max_width'] for r in measured]
        if any(fn(c) is None for c in plain if c!='\n' for fn in new_widths):continue
        if body in AUTHORED:
            candidate=AUTHORED[body]
            if len(candidate.splitlines())<=len(old_lines) and all(measure(candidate,fn)['max_width']<=cap for fn,cap in zip(new_widths,caps)):
                assert candidate.replace('\n','')==body.replace('\n','')
                selected.append(dict(key=row['key'],original=row['original'],before=before,after=pre+candidate+suf,
                                     reason='452手工选择语义换行；字词与控制码不变、六字体静态宽度和行数不超过原文'))
                continue
        lines=[]
        for line in body.splitlines():
            wrapped=wrap_line(line,new_widths,caps)
            if wrapped is None:break
            lines.extend(wrapped)
        else:
            if len(lines)>len(old_lines):continue
            after=pre+'\n'.join(lines)+ ('\n' if body.endswith('\n') else '')+suf
            if after==before:continue
            assert after.replace('\n','')==before.replace('\n','')
            assert TOKEN.findall(after)==TOKEN.findall(before)
            assert all(measure(after,fn)['max_width']<=cap for fn,cap in zip(new_widths,caps))
            selected.append(dict(key=row['key'],original=row['original'],before=before,after=after,
                                 reason='452静态对白仅恢复换行；六字体最大静态宽度不超过原文、行数不增；运行未验证'))
    print('Newline-only candidates:',len(selected))
    for row in selected[:15]:print(row['key'],repr(TOKEN.sub('',row['after'])))
    if '--apply' in sys.argv:
        assert selected
        write(audit_path,dict(rows=selected,scope='static base event dialogue only',runtime_tested=False))
        previous['rows'].extend(selected)
        write(path,previous)


if __name__=='__main__':main()
