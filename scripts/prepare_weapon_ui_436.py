import hashlib
from compile_translation import ROOT,read,write,LEADING,TRAILING,TOKEN
T={(9,0):'在“达伊达拉”出售“素材道具”，\n就能增加武器、防具和饰品的种类。\n　\n“素材道具”光留在身上没有用，\n尽管拿来出售吧。\n',(13,0):'欢迎光临。今天下雨啊…\n',(13,1):'这种日子，总让人创作欲高涨。\n不知道能不能弄到些稀奇的素材啊…\n',(15,0):'那是{F4 45 04 01 00 00 01 01}！？\n居然能弄到这样的稀罕货…\n',(15,1):'稍等一下！\n',(30,0):'…做了不少啊。\n还有没有什么有趣的素材呢…\n',(31,0):'“{F2 01 03 01}{F2 44 01 01}{F2 01 01 01}”，要是有就好了…\n感觉能做出点有趣的东西啊…\n',(32,0):'“{F2 01 03 01}{F2 44 01 01}{F2 01 01 01}”，要是再多些…\n{F2 44 02 01}的新作似乎就能做出来了…\n',(33,0):'＞要离开“达伊达拉”。\n　确定吗？\n'}
def main():
    s='export_base/facility/msg_weapon.bmd.json';d=read(ROOT/s)
    path=ROOT/'translation/batches/436_weapon_ui.generated.json';assert not path.exists()
    cat={r['key']:r for r in read(ROOT/'translation/catalog.working.json')};rows=[]
    for (i,j),body in T.items():
        r=cat[f'{s}:{i}:{j}'];assert not r.get('translation');old=r['original']
        full=LEADING.match(old).group()+body+TRAILING.search(old).group();assert TOKEN.findall(full)==TOKEN.findall(old)
        a=TOKEN.sub('',old).splitlines();b=TOKEN.sub('',full).splitlines();assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),(i,j)
        rows.append([i,j,d['texts'][i]['id'],body])
    write(path,dict(status='draft',sources={s:rows},source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest()},review_notes=['补齐武器店9页素材、制作及离店提示；保留动态名称，开发说明11/12/18不改。旧作店铺资源，未验证可达性。']))
if __name__=='__main__':main()
