"""Record reviewed intentional kana without suppressing compiler warnings."""
import hashlib
from collections import Counter
from compile_translation import ROOT, read, write


def main():
    progress = read(ROOT/'translation/progress.generated.json')
    catalog = {r['key']: r for r in read(ROOT/'translation/catalog.working.json')}
    groups = {
        '生字的多种日语读音示例，正文已有中文解释': {'e813_220.bf.json': {'50:1'}},
        '假名发音及宝箱字谜线索，保留原符号和读音以匹配答案': {
            'e823_600.bf.json': {'0:3', '4:3'},
            'e823_610.bf.json': {'0:1', '0:3', '7:1', '7:3'},
            'e823_620.bf.json': {'0:1', '0:3', '5:1', '5:3'},
            'e823_630.bf.json': {'0:1', '0:3', '5:1', '5:3'},
            'e823_615.bf.json': {'0:2', '3:1'},
            'e823_625.bf.json': {'0:2', '3:1'},
            'e823_635.bf.json': {'0:2', '3:1'},
            'e823_640.bf.json': {'0:1', '0:3', '0:4', '4:1', '4:3', '4:4'},
            'datquestdetail_p3.bmd.json': {'135:0'},
            'datquestdetail_p4.bmd.json': {'135:0'},
        },
        '拆字谜中假名作为笔画部件，替换会破坏图形线索': {
            'e723_438.bf.json': {'3:1', '6:1', '17:0'},
            'e723_440.bf.json': {'0:1', '5:0'},
            'e723_441.bf.json': {'4:0'},
            'e723_442.bf.json': {'5:0', '6:0', '7:1'},
        },
    }
    dispositions = []
    for warning in progress['warnings']:
        if warning['kind'] != 'remaining_kana':
            continue
        key = warning['key']
        source, mi, li = key.rsplit(':', 2)
        name = source.rsplit('/', 1)[-1]
        reasons = [reason for reason, files in groups.items() if f'{mi}:{li}' in files.get(name, set())]
        assert len(reasons) == 1, ('Unreviewed kana', key)
        row = catalog[key]
        dispositions.append(dict(key=key, kind='remaining_kana', disposition='intentional_puzzle_or_reading',
                                 reason=reasons[0], original=row['original'], translation=row['translation'],
                                 translation_sha256=hashlib.sha256(row['translation'].encode('utf-8')).hexdigest(),
                                 layout_verified=False, runtime_verified=False))
    assert len(dispositions) == 38
    numeric_path=ROOT/'translation/numeric_review_451.json'
    reviewed_numeric={r['key']:r for r in read(numeric_path)['rows']} if numeric_path.exists() else {}
    reflow_path=ROOT/'translation/reflow_452.review.json'
    reflows={r['key']:r for r in read(reflow_path)['rows']} if reflow_path.exists() else {}
    reflow453=ROOT/'translation/layout_453.review.json'
    if reflow453.exists():
        reflows.update({r['key']:r for r in read(reflow453)['rows'] if r['newline_only']})
    numeric_results=[]
    for warning in progress['warnings']:
        if warning['kind']!='numeric_review':continue
        prior=reviewed_numeric.get(warning['key'])
        matched=bool(prior and prior['disposition']=='reviewed_equivalent' and prior['original']==warning['original'] and prior['translation']==warning['translation'])
        reflow=reflows.get(warning['key'])
        if not matched and prior and reflow:
            matched=(prior['disposition']=='reviewed_equivalent' and prior['original']==warning['original']
                     and prior['translation']==reflow['before'] and warning['translation']==reflow['after']
                     and reflow['before'].replace('\n','')==reflow['after'].replace('\n',''))
        numeric_results.append(dict(key=warning['key'],disposition='reviewed_equivalent' if matched else 'needs_review'))
    counts=Counter(w['kind'] for w in progress['warnings'])
    write(ROOT/'translation/warning_disposition.generated.json', dict(
        compiler_warnings_preserved=True, warning_counts=dict(Counter(w['kind'] for w in progress['warnings'])),
        reviewed_intentional_kana=dispositions, numeric_dispositions=numeric_results,
        numeric_review_pending=sum(r['disposition']=='needs_review' for r in numeric_results), layout_review_pending=counts['layout_review'],
        note='Only current text snapshots were reviewed; any text change requires a new review. No layout or puzzle runtime pass implied.'))
    print('Intentional kana:',len(dispositions),'numeric reviewed:',sum(r['disposition']=='reviewed_equivalent' for r in numeric_results),'layout pending:',counts['layout_review'])


if __name__ == '__main__':
    main()
