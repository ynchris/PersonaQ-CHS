"""Additional item names; exact Q2 item-bank references, original slots retained."""
import hashlib
import re
import sys
from compile_translation import ROOT, read, write
from equipment_names import load_drafts, EXPECTED_SHA
from scan_latest_q2_myth import LATEST
from q2_name_banks import excluded, CHOICES

DRAFT=ROOT/'translation/q2_item_names.review.generated.json'

def load():
    draft=read(DRAFT)
    data,start,names,existing=load_drafts()
    assert draft['source_sha256']==EXPECTED_SHA
    rows={}
    for r in draft['rows']:
        i=r['index']
        assert 1280<=i<len(names) and i not in existing and i not in rows
        assert names[i]==r['original'] and not excluded(names[i])
        rows[i]=r['translation']
    extra_path=ROOT/'translation/consumable_names_completion.review.json'
    if extra_path.exists():
        extra=read(extra_path)
        assert extra['source_sha256']==EXPECTED_SHA
        for r in extra['rows']:
            i=r['index']
            assert 1281<=i<1536 and i not in rows and names[i]==r['original']
            assert not excluded(names[i])
            rows[i]=r['translation']
    remaining_path=ROOT/'translation/item_names_completion.review.json'
    if remaining_path.exists():
        remaining=read(remaining_path)
        assert remaining['source_sha256']==EXPECTED_SHA
        for r in remaining['rows']:
            i=r['index']
            assert 1536<=i<len(names) and i not in rows and names[i]==r['original']
            assert not excluded(names[i])
            rows[i]=r['translation']
    return rows

def prepare():
    assert not DRAFT.exists() or sys.argv[1:]==['--refresh']
    data,start,names,existing=load_drafts()
    path=LATEST/'init/itemtbl.bin.json'; refs=read(path)
    skillpath=LATEST/'battle/table/skillnametable.tbl.json'; skills=read(skillpath)
    rows=[]; skipped=[]; pending=[]
    choices={**CHOICES,'耐風ミスト':'耐风喷雾'}
    for i,name in enumerate(names):
        if i in existing:continue
        matches=[r for r in refs if r['original']==name and r.get('translation')]
        reference='init/itemtbl.bin.json'
        if not matches and i>=2560:
            matches=[r for r in skills if r['original']==name and r.get('translation')]
            reference='battle/table/skillnametable.tbl.json'
        reason=None
        if i<1280 or excluded(name) or re.search(r'開始|条件つき',name):reason='placeholder_or_internal'
        elif not matches:reason='no_exact_item_reference'
        if reason:skipped.append(dict(index=i,original=name,reason=reason));continue
        variants={r['translation'].strip() for r in matches}
        if len(variants)>1 and name not in choices:pending.append((i,name,sorted(variants)));continue
        value=choices.get(name,next(iter(variants)));assert value in variants
        if re.search(r'[\u3041-\u3096\u30a1-\u30fa{}\[\]\r\n\x00]',value) or len(value)>10:
            pending.append((i,name,value));continue
        rows.append(dict(index=i,original=name,translation=value,reference=reference,references=matches))
    write(ROOT/'translation/q2_item_names.pending.generated.json',pending)
    if pending:print('Pending:',pending);return
    write(DRAFT,dict(source_sha256=EXPECTED_SHA,reference='init/itemtbl.bin.json',reference_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),skill_reference_sha256=hashlib.sha256(skillpath.read_bytes()).hexdigest(),rows=rows,excluded=skipped,runtime_tested=False))
    print('Additional item slots:',len(rows))

if __name__=='__main__':prepare()
