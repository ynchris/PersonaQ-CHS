"""Account for every remaining warning without inventing textbox capacities."""
import re,hashlib
from collections import Counter
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING

def main():
    catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')}
    metrics=read(ROOT/'translation/layout_metrics.generated.json')['rows'];rows=[]
    warnings={w['key'] for w in read(ROOT/'translation/progress.generated.json')['warnings'] if w['kind']=='layout_review'}
    assert {r['key'] for r in metrics}==warnings
    for metric in metrics:
        r=catalog[metric['key']];t=r['translation']
        assert metric['translation_sha256']==hashlib.sha256(t.encode('utf-8')).hexdigest()
        pre=LEADING.match(t).group();suf=TRAILING.search(t).group()
        body=t[len(pre):len(t)-len(suf)] if suf else t[len(pre):]
        embedded=TOKEN.findall(body)
        variables=[x for x in TOKEN.findall(t) if re.match(r'\{(?:F1 8[0-9A-F]|F2 44|F4 (?:45|84)|F5 C1 (?:0D|0E|0F|10|11|12))\b',x)]
        unknown=[x for x in embedded if not re.fullmatch(r'\{F2 01 [0-9A-F]{2} 01\}',x)]
        if not metric['static_metrics_complete']:category='source_glyph_metrics_incomplete'
        elif r['message_id'].startswith('SEL'):category='selection_box_dimensions_required'
        elif variables or unknown:category='control_expansion_or_behavior_required'
        elif (metric['max_growth_px']<=0 and all(m['translation']['line_count']<=m['original']['line_count'] for m in metric['metrics'].values())):
            category='literal_extent_not_increased_runtime_unverified'
        else:category='textbox_dimensions_required'
        rows.append(dict(key=r['key'],category=category,translation_sha256=metric['translation_sha256'],
                         max_static_growth_px=metric['max_growth_px'],potential_variable_tokens=variables,
                         embedded_unmodeled_controls=unknown,original=r['original'],translation=t,
                         runtime_verified=False))
    counts=dict(Counter(r['category'] for r in rows))
    write(ROOT/'translation/layout_queue.generated.json',dict(total=len(rows),categories=counts,rows=rows,
         all_remaining_warnings_accounted_for=True,all_layout_complete=False,
         notes=['Growth over the Japanese text does not establish overflow; actual textbox dimensions are unknown.',
                'Zero static glyph cost for a control is not a bound on its runtime output.',
                'Even literal non-increase does not prove font selection or runtime fit.',
                'User currently has only an opening save; later scenes and DLC navigation remain runtime-unverified.']))
    print('Whole remaining queue:',len(rows),counts)

if __name__=='__main__':main()
