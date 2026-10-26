"""Compile scoped table drafts; untranslated/dead-data candidates stay separate."""
from compile_translation import ROOT, read, write

def main():
    data=read(ROOT/'translation/tables.catalog.generated.json')
    draft=read(ROOT/'translation/table_phrases.zh-Hans.json')
    used=set()
    count=0
    for row in data:
        if row['source']==draft['source'] and row['member_index'] in draft['member_indices']:
            if row['original'] not in draft['phrases']:
                raise ValueError(f'Missing table phrase: {row["key"]}')
            row['translation']=draft['phrases'][row['original']]
            row['status']='draft_table_reviewed'
            used.add(row['original'])
            count+=1
    if used!=set(draft['phrases']):
        raise ValueError('Unused phrase entries: '+repr(set(draft['phrases'])-used))
    for path in sorted((ROOT/'translation/table_batches').glob('*.json')):
        extra=read(path)
        for member in extra['members']:
            selected=[r for r in data if r['source']==extra['source'] and r['member_index']==member['index']]
            if len(selected)!=len(member['rows']):
                raise ValueError('Unexpected table row count')
            for row,(expected,chinese) in zip(selected,member['rows']):
                if row['member_name']!=member['name'] or row['member_sha256']!=member['sha256'] or row['original']!=expected or row['translation']:
                    raise ValueError('Changed or duplicate additional table row')
                row['translation']=chinese
                row['status']='draft_table_reviewed'
                count+=1
    for reuse in [ROOT/'translation/q2_fixed_rows.review.generated.json',ROOT/'translation/quest_facility_completion.review.json',ROOT/'translation/table_tail_448.review.json',ROOT/'translation/table_expansion_449.review.json']:
        if not reuse.exists():continue
        lookup={r['key']:r for r in data}
        for entry in read(reuse)['entries']:
            row=lookup[entry['key']]
            assert not row['translation']
            for field in ['source','member_index','member_name','member_sha256','row','offset','capacity_bytes','original']:
                assert row[field]==entry[field],(entry['key'],field)
            row['translation']=entry['translation'];row['status']='draft_table_reviewed';count+=1
    from terminology_459 import apply as apply_terminology
    for row in data:
        if row['translation']:
            row['translation']=apply_terminology('tables',row['key'],row['translation'])
    write(ROOT/'translation/tables.catalog.working.json',data)
    print(f'{count} fixed-table draft rows; {len(data)-count} candidate rows not translated')

if __name__=='__main__':
    main()
