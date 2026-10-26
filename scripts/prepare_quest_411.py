"""Reuse reviewed quest titles in cancellation messages; retain debug text."""
import hashlib,re
from collections import defaultdict
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING

DEADLINE='なお、こちらの依頼には\n期限が設けられております。\nお早めにお引き受けください。'

def main():
    target=ROOT/'translation/batches/411_quest_cancel_deadline.generated.json';assert not target.exists()
    tables=read(ROOT/'translation/tables.catalog.working.json')
    names={r['original']:r for r in tables if r.get('member_name')=='qstQuestNameText.qtd' and r.get('translation')}
    sources=defaultdict(list);audit=[];counts=defaultdict(int)
    for r in read(ROOT/'translation/catalog.working.json'):
        if r.get('translation') or not r['source'].startswith('export_base/quest/'):continue
        plain=TOKEN.sub('',r['original']).strip().replace('\r\n','\n')
        match=re.fullmatch('“(.+)”を\n破棄いたします。',plain)
        if match and match[1] in names:
            ref=names[match[1]];body='取消委托\n“'+ref['translation']+'”。\n'
            audit.append({'target':r['key'],'reference_table_key':ref['key'],'original_title':ref['original'],'translated_title':ref['translation']});counts['title_reuse']+=1
        elif plain==DEADLINE:
            body='另外，这项委托\n设有{F2 01 03 01}期限{F2 01 01 01}。\n请尽早接受。\n';counts['deadline']+=1
        else:continue
        full=LEADING.match(r['original']).group()+body+TRAILING.search(r['original']).group()
        assert TOKEN.findall(full)==TOKEN.findall(r['original'])
        a=plain.splitlines();b=TOKEN.sub('',body).splitlines()
        assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),r['key']
        doc=read(ROOT/r['source']);i=r['message_index'];j=r['line_index']
        sources[r['source']].append([i,j,doc['texts'][i]['id'],body])
    assert counts['title_reuse']==47,counts
    write(target,dict(status='draft',sources=dict(sources),source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},title_reuse_audit=audit,review_notes=['取消提示复用已审定的47个委托名，不另译同名任务。','测试、仮文本和空号不在本批范围；期限提示不改变任务实际期限。未运行验证。']))
    print(dict(counts))

if __name__=='__main__':main()
