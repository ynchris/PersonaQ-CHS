"""Reuse only byte-identical source text from the completed DLC navigator."""
import hashlib
from collections import defaultdict,Counter
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING

def main():
    target=ROOT/'translation/batches/391_shared_dlc_navigation.generated.json';assert not target.exists()
    rows=read(ROOT/'translation/catalog.working.json');index=defaultdict(list)
    for row in rows:
        if row.get('translation') and row['source'].startswith('export_dlc/0006/battle/support/bsv121.bvp_'):
            index[row['original']].append(row)
    sources=defaultdict(list);audit=[];hashes={}
    for row in rows:
        source=row['source']
        if row.get('translation') or not source.startswith('export_dlc/') or '/battle/support/' not in source:continue
        refs=index.get(row['original'],[])
        if not refs:continue
        values={r['translation'] for r in refs}
        assert len(values)==1,row['key']
        full=values.pop();old=row['original']
        assert 'ダミー' not in TOKEN.sub('',old)
        assert TOKEN.findall(full)==TOKEN.findall(old)
        body=TRAILING.sub('',LEADING.sub('',full))
        assert LEADING.match(old).group()+body+TRAILING.search(old).group()==full
        i=row['message_index'];j=row['line_index'];doc=read(ROOT/source)
        sources[source].append([i,j,doc['texts'][i]['id'],body])
        reference=refs[0]
        for s in [source,reference['source']]:hashes[s]=hashlib.sha256((ROOT/s).read_bytes()).hexdigest()
        audit.append(dict(key=row['key'],reference_key=reference['key'],reference_batch=reference['batch'],original=old,translation=full))
    counts=Counter(s.split('/')[1] for s,entries in sources.items() for _ in entries)
    assert counts=={'0005':50,'0007':50,'0008':50,'0009':50},counts
    write(target,dict(status='draft',sources=dict(sources),source_hashes=hashes,review_notes=['仅复用完整日文及控制码完全一致的DLC导航文本，译文冲突时拒绝导入。','这是本地一代导航之间的复用，不是新增二代复用；不改变独有角色语气。','所有占位保留；运行未验证。']))
    write(ROOT/'translation/391_shared_dlc_navigation.audit.generated.json',dict(entries=audit,counts=dict(counts),runtime_tested=False))
    print('Exact local reuse:',len(audit),'pages',dict(counts))

if __name__=='__main__':main()
