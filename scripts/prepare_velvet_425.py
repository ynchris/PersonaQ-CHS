import hashlib
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING
TEXT={(1,0):'那么，再会。\n',(2,0):'欢迎您再次光临。\n',(3,0):'欢迎来到天鹅绒房间……\n',(4,0):'那么……\n您想做些什么？\n',(5,0):'欢迎来到天鹅绒房间……\n',(8,0):'哎呀……\n这一刻终于到来了呢。\n',(8,1):'弟弟妹妹也马上就到，\n你真的已经准备好了吗？\n',(9,0):'准备好了',(9,1):'稍等一下',(10,0):'呵呵……来一场激烈的战斗吧。\n',(11,0):'这样啊……\n那么，下次再说吧……\n'}

def main():
    TEXT[11,0]='这样啊……\n那么，下次再说……\n'
    target=ROOT/'translation/batches/425_velvet_entry_challenge.generated.json';assert not target.exists()
    s='export_base/facility/cmbtalk.bf.json';doc=read(ROOT/s)
    catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')};rows=[]
    for (i,j),body in TEXT.items():
        r=catalog[f'{s}:{i}:{j}'];assert not r.get('translation');old=r['original']
        full=LEADING.match(old).group()+body+TRAILING.search(old).group()
        assert TOKEN.findall(full)==TOKEN.findall(old)
        a=TOKEN.sub('',old).splitlines();b=TOKEN.sub('',full).splitlines()
        assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),(i,j,a,b)
        rows.append([i,j,doc['texts'][i]['id'],body])
    write(target,dict(status='draft',sources={s:rows},source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest()},review_notes=['天鹅绒房间迎送及挑战准备分支11页，保留声音/表情及选择控制码。','6/7解禁事件予定、12测试文字不动；未据此判断其余遗留场景可见性。未运行验证。']))
    print('Velvet entry/challenge pages:',len(rows))

if __name__=='__main__':main()
