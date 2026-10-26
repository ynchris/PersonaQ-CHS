import hashlib
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING

T={
62:['看来不需要\n我的忠告呢。'],
63:['进展十分出色。','正是社群构成了您的“世界”…\n还请不要忘记…'],
64:['进展相当不错呢。','正是社群构成了您的“世界”…\n还请不要忘记…'],
65:['我想，您应该更加珍惜羁绊。','正是社群构成了您的“世界”…\n还请不要忘记…'],
66:['请更加珍惜羁绊。\n在您身边，一定能找到的。','正是社群构成了您的“世界”…\n还请不要忘记…'],
67:['哎呀…？','看来，您的社群完成率\n已经超过５０％了…','真了不起。\n那么…请收下这个吧。','社群越充实，\n您的“世界”也就越充实…','我很期待\n您的“世界”呢。'],
68:['真了不起…','您终于将所有社群\n都培育成了真正的羁绊呢…','这可不是谁都能做到的…','您果然…和我想的一样。','您的“世界”…\n究竟是什么样的呢。','如果可以的话，\n真希望您也带我去那个“世界”…','…那么，请收下这个。\n这是我花了漫长岁月制作的。','它一定会保护您的。\n代替我…'],
73:['看来您还没有“{F2 44 01 01}”社群。\n不过，建立“{F2 44 01 01}”社群，\n似乎还需要一段时间…','虽然不会获得新的力量，\n确定选择这个人格面具吗？'],
74:['看来您还没有“{F2 44 01 01}”社群。\n不过，我想也快出现了…','虽然不会获得新的力量，\n确定选择这个人格面具吗？'],
75:['看来您还没有“{F2 44 01 01}”社群。','虽然不会获得新的力量，\n确定选择这个人格面具吗？'],
76:['看来您没有对应的“社群”…\n这样就无法获得新的力量了。','确定选择这个人格面具吗？'],
86:['对应的“社群”等级为１０…','哦…这无疑会\n带着强大的力量诞生。','确定选择这个人格面具吗？'],
}
T[68][5]='如果可以，也请带我\n去那个“世界”吧…'
for i,n in enumerate('１２３４５６７８９',77):
    strength=('那么…究竟会获得多少力量呢。' if i==77 else '诞生时应该能获得一些力量…' if i<=79 else '诞生时看来能获得不俗的力量。' if i<=81 else '诞生时看来能获得相当强的力量。' if i<=83 else '诞生时将会获得很强的力量…')
    T[i]=[f'对应的“社群”等级为{n}…\n{strength}','确定选择这个人格面具吗？']

def main():
    s='export_base/facility/msg_combine.bmd.json';d=read(ROOT/s)
    p=ROOT/'translation/batches/438_combine_social.generated.json';assert not p.exists()
    cat={r['key']:r for r in read(ROOT/'translation/catalog.working.json')};rows=[]
    for i,lines in sorted(T.items()):
        for j,line in enumerate(lines):
            r=cat[f'{s}:{i}:{j}'];assert not r.get('translation');old=r['original'];body=line+'\n'
            full=LEADING.match(old).group()+body+TRAILING.search(old).group()
            assert TOKEN.findall(full)==TOKEN.findall(old),(i,j)
            a=TOKEN.sub('',old).splitlines();b=TOKEN.sub('',full).splitlines()
            assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),(i,j)
            rows.append([i,j,d['texts'][i]['id'],body])
    assert len(rows)==51
    write(p,dict(status='draft',sources={s:rows},source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest()},review_notes=['社群进度、奖励及合体加成51页；保留等级数字、动态社群名称和控制码。属于旧作遗留机制文本，未验证运行时可达性。']))
if __name__=='__main__':main()
