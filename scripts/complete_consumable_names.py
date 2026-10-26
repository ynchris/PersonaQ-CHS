"""Finish the bounded consumable-name section without changing item records."""
from compile_translation import ROOT,read,write
from equipment_names import load_drafts,EXPECTED_SHA
from q2_item_names import load as load_items
from q2_name_banks import load as load_banks,excluded

DRAFT=ROOT/'translation/consumable_names_completion.review.json'

def main():
    assert not DRAFT.exists()
    _,_,names,_=load_drafts();existing=load_items()
    group=next(g for g in load_banks()['groups'] if g['source']=='battle/table/skillnametable.tbl')
    index={}
    for r in group['rows']:
        if r['original'] in index:assert index[r['original']]['translation']==r['translation']
        index[r['original']]=r
    local={'盲目の香':'失明之香','医療キット':'医疗套件','贖罪の羊':'赎罪羔羊'}
    rows=[];retained=[]
    for i in range(1280,1536):
        name=names[i]
        if i in existing:continue
        if i==1280 or excluded(name):retained.append(dict(index=i,original=name));continue
        ref=index.get(name)
        value=ref['translation'] if ref else local[name]
        rows.append(dict(index=i,original=name,translation=value,skill_index=ref['index'] if ref else None))
    write(DRAFT,dict(source='init/itemtbl.bin',source_sha256=EXPECTED_SHA,range_start=1280,range_end_exclusive=1536,rows=rows,retained=retained,runtime_tested=False))
    print('Added consumables:',len(rows),'total display names:',sum(i in existing for i in range(1280,1536))+len(rows),'retained:',len(retained))

if __name__=='__main__':main()
