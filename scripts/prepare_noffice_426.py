import hashlib
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING

TEXT={(3,0):'您是否忘记了\n有期限的委托呢？\n',
      (3,1):'若是忘记了，请尽早完成，\n并向我报告。\n',
      (4,0):'委托的期限\n已经快到了。\n',
      (4,1):'建议您再确认一下\n委托内容。\n',
      (5,0):'有委托\n已经过期了。\n',
      (5,1):'下次可别再忘记委托，\n也别忘了我……\n',
      (6,0):'另外，我也准备了\n下一批限时委托。\n',
      (6,1):'若是忘记了，请尽早完成，\n并向我报告。\n',
      (7,0):'另外，下一份委托的期限\n也已经快到了。\n',
      (7,1):'建议您再确认一下\n委托内容。\n',
      (11,0):'欢迎您再次光临。\n',(12,0):'欢迎您再次光临。\n'}

def main():
    target=ROOT/'translation/batches/426_noffice_deadlines.generated.json';assert not target.exists()
    s='export_base/facility/noffice.bf.json';doc=read(ROOT/s)
    catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')};rows=[]
    for (i,j),body in TEXT.items():
        r=catalog[f'{s}:{i}:{j}'];assert not r.get('translation');old=r['original']
        full=LEADING.match(old).group()+body+TRAILING.search(old).group()
        assert TOKEN.findall(full)==TOKEN.findall(old)
        a=TOKEN.sub('',old).splitlines();b=TOKEN.sub('',full).splitlines()
        assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),(i,j,a,b)
        rows.append([i,j,doc['texts'][i]['id'],body])
    write(target,dict(status='draft',sources={s:rows},source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest()},review_notes=['保健室委托期限提醒、过期及送客12页，保留控制序列。','8/9 dummy会话与13/14设施脚本说明保持不变；未验证这些分支的运行时可达性。']))
    print('Noffice deadline/goodbye pages:',len(rows))

if __name__=='__main__':main()
