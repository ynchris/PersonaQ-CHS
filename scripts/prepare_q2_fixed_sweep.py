"""Apply every usable exact fixed-table candidate; exclude documented legacy menus."""
import hashlib
from compile_translation import ROOT,read,write
from scan_latest_q2_myth import LATEST
from scan_q2_sweep import normalized

def main():
    target=ROOT/'translation/q2_fixed_rows.review.generated.json'
    assert not target.exists()
    entries=[];excluded=[]
    fixes={'登录':'登记','瞬缘笔记':'擦肩笔记','不可思议国度的你':'不可思议之国的你','放学后的恶灵社':'放学后的恶灵俱乐部','调合':'调配','编辑队伍':'编成队伍'}
    for r in read(ROOT/'translation/q2_sweep_384.tables.generated.json'):
        legacy=(r['source']=='init/cmptable.bin' or
                r['member_name']=='fclSimpleHelp.ftd' and r['row'] in {8,11,12,25} or
                r['member_name']=='fclSuggestTypeName.ftd' and r['row']==3)
        if legacy:excluded.append({'key':r['key'],'reason':'legacy_quest_or_mechanic_or_placeholder'});continue
        same=[x for x in r['references'] if x['reference'].endswith(r['member_name']+'.json')]
        refs=same or r['references'];variants={x['translation'] for x in refs}
        assert len(variants)==1,(r['key'],variants)
        text=next(iter(variants)).strip()
        for a,b in fixes.items():text=text.replace(a,b)
        for ref in refs:
            p=LATEST/ref['reference']
            assert hashlib.sha256(p.read_bytes()).hexdigest()==ref['sha256']
            assert normalized(ref['original'])==normalized(r['original'])
        entries.append({**r,'translation':text,'references':refs,'status':'draft_table_reviewed'})
    write(target,{'reference_commit':'15ca3ffda260133bfb090fc8a5b5ea896553f37c','entries':entries,'excluded':excluded,'runtime_tested':False})
    print('Fixed rows',len(entries),'excluded legacy/placeholders',len(excluded))

if __name__=='__main__':main()
