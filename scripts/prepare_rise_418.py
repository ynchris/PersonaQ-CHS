import hashlib
from collections import defaultdict
from compile_translation import ROOT,read,write,TOKEN

def main():
    target=ROOT/'translation/batches/418_rise_speaker_completion.generated.json';assert not target.exists()
    sources=defaultdict(list)
    for r in read(ROOT/'translation/catalog.working.json'):
        if r.get('translation') or not any(t in str(r.get('speaker')) for t in ('りせ','理世')):continue
        text=TOKEN.sub('',r['original'])
        if text.strip()=='リザーブ':continue
        if text=='持ってないけど、いいの？\n':body='没带，没关系吗？\n'
        else:
            assert text=='先輩、その扉の向こう側に敵が居るよ、\n気を付けて。\n',r['key']
            body='前辈，那扇门后面有敌人哦，\n要小心。\n'
        s=r['source'];i=r['message_index'];j=r['line_index']
        sources[s].append([i,j,read(ROOT/s)['texts'][i]['id'],body])
    assert sum(map(len,sources.values()))==3
    write(target,dict(status='draft',sources=dict(sources),source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},review_notes=['按理世四种说话人标记交叉检查补3页，两个门后警告为资源副本，保留动态道具名前缀。','12页リザーブ原样保留；这不证明没有未标注说话人的关联台词或未提取资源。未运行验证。']))
    print('Rise named-speaker omissions:',3)

if __name__=='__main__':main()
