import hashlib
from collections import defaultdict
from compile_translation import ROOT,read,write,LEADING,TRAILING,TOKEN
from audit_remaining_text import classify_row
def main():
    p=ROOT/'translation/batches/441_exact_reuse.generated.json';assert not p.exists()
    cat=read(ROOT/'translation/catalog.working.json');index=defaultdict(list)
    for r in cat:
        if r.get('translation'):index[r['original']].append(r)
    sources=defaultdict(list);hashes={};audit=[]
    for r in cat:
        if r.get('translation') or classify_row(r)[0]!='needs_review':continue
        # Speaker-specific first-person wording needs context rather than exact-text reuse.
        if r['source']=='export_base/facility/party_edit_msg.bmd.json':continue
        refs=index[r['original']]
        if len({x['translation'] for x in refs})!=1:continue
        full=refs[0]['translation'];old=r['original'];s=r['source'];i=r['message_index'];j=r['line_index']
        pre=LEADING.match(old).group();suf=TRAILING.search(old).group()
        assert full.startswith(pre) and full.endswith(suf) and TOKEN.findall(full)==TOKEN.findall(old)
        body=full[len(pre):len(full)-len(suf)]
        sources[s].append([i,j,read(ROOT/s)['texts'][i]['id'],body])
        hashes[s]=hashlib.sha256((ROOT/s).read_bytes()).hexdigest()
        audit.append(dict(target_key=r['key'],reference_key=refs[0]['key'],original=old,translation=full))
    assert len(audit)==37
    write(p,dict(status='draft',sources=dict(sources),source_hashes=hashes,reuse_audit=audit,review_notes=['逐条审阅37页原文和控制码完全相同、译文唯一的现有译文复用；排除带老夫自称的角色台词，避免跨说话者误用。非新增Q2匹配；包含遗留资源，不推断可达性。']))
if __name__=='__main__':main()
