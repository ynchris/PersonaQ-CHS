import hashlib
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING

TEXT={51:['要强化这个人格面具吗？\n'],52:['您目前装备着的人格面具，\n我无法代为保管……\n'],53:['看来您没有可作为\n强化素材的人格面具……\n'],54:['要中止强化，\n取回这个人格面具吗？\n'],55:['目前代为保管的人格面具，\n状态如您所见。\n'],56:['目前代为保管的人格面具，\n状态如您所见。\n'],57:['目前代为保管的人格面具，\n状态如您所见。\n'],58:['真是令人遗憾的结果……\n'],59:['看来您无法携带更多人格面具了……\n请腾出空位后再来领取。\n'],60:['人格面具的技能似乎要强化了。\n','“{F2 01 02 01}{F2 44 01 01}{F2 01 01 01}”，要强化吗？\n'],61:['＞{F4 45 04 01 00 00 01 01}已获得。\n']}

def main():
    s='export_base/facility/msg_combine.bmd.json';doc=read(ROOT/s)
    path=ROOT/'translation/batches/430_combine_strengthening.generated.json';assert not path.exists()
    catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')};rows=[]
    for i,lines in TEXT.items():
        for j,body in enumerate(lines):
            r=catalog[f'{s}:{i}:{j}'];assert not r.get('translation');old=r['original']
            full=LEADING.match(old).group()+body+TRAILING.search(old).group()
            assert TOKEN.findall(full)==TOKEN.findall(old)
            a=TOKEN.sub('',old).splitlines();b=TOKEN.sub('',full).splitlines()
            assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),(i,j)
            rows.append([i,j,doc['texts'][i]['id'],body])
    write(path,dict(status='draft',sources={s:rows},source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest()},review_notes=['强化、保管、取回及技能强化提示整段51—61，共12页。保留动态技能/道具名、颜色、获得提示控制码。','上下文含旧作遗留机制，尚未确认本段运行时可达性；不视为新增PQ功能或剧情。']))
    print('Strengthening prompts:',len(rows))

if __name__=='__main__':main()
