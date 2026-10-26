import hashlib
from collections import defaultdict
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING
TEXT={
'scrgotodungeon.bf.json':{
(1,0):'＞完成已接受的委托，\n　需要伙伴的协助。\n　要重新调整队伍吗……\n',
(2,0):'＞玛格丽特的委托要求\n　２位不羁能力者一同前往。\n　要重新调整队伍吗……\n　',
(3,0):'“从最深到达层开始”{F2 01 01 01}，\n即可从最后到达的楼层\n开始探索了。\n',
(4,0):'＞……！？\n　在迷宫里得到的\n　{F4 84 04 01 01 01 09 07}不见了。\n',
(4,1):'＞看来在离开迷宫时\n　就消失了。\n'},
'scrpartyedit.bf.json':{
(1,0):'随着新成员加入，\n现在可以将导航分为战斗和迷宫，\n分别交给两个人负责。\n　\n可在队伍编成菜单的\n{F2 01 03 01}“导航设置”{F2 01 01 01}中\n进行设置。\n',
(2,0):'若将战斗和迷宫的导航分别交给两人，\n{F2 01 03 01}就只能使用在各自负责的场合\n有效的技能{F2 01 01 01}，\n请注意。\n',
(3,0):'已经为您登记了推荐队伍。\n　\n可以通过\n{F2 01 03 01}“调用已登记队伍”{F2 01 01 01}进行调用，\n不知如何编队时，请使用此功能。\n'}}

def main():
    target=ROOT/'translation/batches/423_navigation_party_tutorials.generated.json';assert not target.exists()
    catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')};sources=defaultdict(list)
    for filename,entries in TEXT.items():
        s='export_base/facility/'+filename;doc=read(ROOT/s)
        for (i,j),body in entries.items():
            r=catalog[f'{s}:{i}:{j}'];assert not r.get('translation');old=r['original']
            full=LEADING.match(old).group()+body+TRAILING.search(old).group()
            assert TOKEN.findall(old)==TOKEN.findall(full),(s,i,j)
            a=TOKEN.sub('',old).splitlines();b=TOKEN.sub('',full).splitlines()
            assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),(s,i,j,a,b)
            sources[s].append([i,j,doc['texts'][i]['id'],body])
    write(target,dict(status='draft',sources=dict(sources),source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},review_notes=['8页迷宫出发与导航/队伍编成教程；动态道具参数、颜色控制序列保留。','明确两位不羁能力者共同出发条件及导航技能按场合生效限制；未运行验证。']))
    print('Facility tutorials:',sum(map(len,sources.values())))

if __name__=='__main__':main()
