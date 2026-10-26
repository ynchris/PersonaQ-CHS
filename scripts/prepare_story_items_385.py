"""Complete meaningful key-item descriptions; retain unused slots verbatim."""
import hashlib
import re
import unicodedata
from collections import Counter
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING

SOURCE='export_base/init/dateventitemhelp.bmd.json'
TEXT={
1:'与懦弱之魔影和嬉笑之桌战斗后，\n拾到的空白卡片。\n',
4:'园艺用的洒水壶。将水洒在\n涂了红色颜料的白玫瑰上，就会……\n',
5:'生锈的钥匙。陈旧的木牌上\n写着“北栋”。\n',
6:'生锈的钥匙。陈旧的木牌上\n写着“实习栋”。\n',
7:'生锈的钥匙。陈旧的木牌上\n写着“南栋”。\n',
8:'在黑暗中捡到的神秘黑色钥匙。\n不知为何，一开灯就会消失。\n',
9:'玲找到的红色门禁卡。\n用于打开上锁的门。\n',
10:'玲找到的黄色门禁卡。\n用于打开上锁的门。\n',
11:'玲找到的蓝色门禁卡。\n用于打开上锁的门。\n',
12:'善制作的简陋火把。\n点燃后便能携带火焰。\n',
13:'从Ｆ．Ｏ．Ｅ那里获得的黑色兜裆布。\n不知原本就是黑色，还是被弄脏了。\n',
14:'绣着“ＮＩＫＯ”字样的\n陈旧兔子玩偶。\n',
15:'如同夜市摊上售卖的\n儿童玩具戒指。\n',
16:'一缕修长而美丽的头发。\n',
17:'写着“安息吧　有希”的\n留言卡片。\n',
18:'善为绘制地图而准备的\n皮封面笔记本。\n',
19:'喝下缩小药后获得的\n用于打开迷宫内房门的钥匙。\n',
20:'全书登记率达到２５％的证明。\n从全书召唤时费用减免１０％。\n',
21:'全书登记率达到５０％的证明。\n从全书召唤时费用减免１５％。\n',
22:'全书登记率达到７５％的证明。\n从全书召唤时费用减免２０％。\n',
23:'全书登记率达到１００％的证明。\n从全书召唤时费用减免２５％。\n',
26:'生锈的钥匙。陈旧的木牌上\n写着“理科准备室”。\n',
27:'在不可思议之国的你中\n获得的白玫瑰。\n',
28:'在联谊咖啡厅中获得的\n神秘心形标记。\n',
29:'在放学后的恶灵俱乐部中\n获得的可疑注射器。\n',
30:'在稻羽乡土展中获得的\n拧成绳状的头巾。\n',
31:'掉在钟楼２层的齿轮。\n似乎能用于某种机械。\n',
200:'玛格丽特和伊丽莎白赠送的贝壳。\n轻轻贴在耳边，便能听到某种声音。\n',
}
for i in [2,3,24,25]:TEXT[i]=TEXT[1]

def main():
    target=ROOT/'translation/batches/385_story_key_items.generated.json'
    assert not target.exists()
    doc=read(ROOT/SOURCE)
    catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')}
    materials={r['message_index']:r for r in catalog.values() if r['source']=='export_base/init/datmaterialhelp.bmd.json'}
    reuse=[]
    for i,j in [(64,368),(65,371),(66,374),(67,377)]:
        row=materials[j];old=doc['texts'][i]['lines'][0]
        assert TOKEN.sub('',row['original'])==TOKEN.sub('',old) and row.get('translation')
        TEXT[i]=TRAILING.sub('',LEADING.sub('',row['translation']))
        reuse.append({'index':i,'catalog_key':row['key'],'translation':TEXT[i]})
    sources={SOURCE:[[i,0,doc['texts'][i]['id'],v] for i,v in sorted(TEXT.items())]}
    quote='export_base/event/e000/e020_001.bf.json'
    sources[quote]=[[0,0,read(ROOT/quote)['texts'][0]['id'],'「命运会将\n　　你的灵魂带往\n　　　　　　最适合你的地方\n　　　　　　　　――William Shakespeare」\n']]
    for source,rows in sources.items():
        original=read(ROOT/source)
        for i,j,mid,body in rows:
            row=catalog[f'{source}:{i}:{j}'];assert not row.get('translation')
            old=original['texts'][i]['lines'][j]
            full=LEADING.match(old).group()+body+TRAILING.search(old).group()
            assert TOKEN.findall(old)==TOKEN.findall(full)
            numbers=lambda t:Counter(re.findall(r'\d+',unicodedata.normalize('NFKC',TOKEN.sub('',t))))
            assert numbers(old)==numbers(full)
            before=TOKEN.sub('',old).splitlines();after=TOKEN.sub('',full).splitlines()
            assert len(after)<=len(before) and max(map(len,after))<=max(map(len,before)),(source,i)
    write(target,{'status':'draft','sources':sources,'source_hashes':{s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},'review_notes':['贵重品非占位说明全部补齐，四项Boss材料说明复用已审校的一代正文。','敌名沿用已导入二代名称；开场引文按游戏日文翻译，不额外断言现实引文出处。','不翻译调试或旧作残留来提高覆盖率；运行未验证。']})
    write(ROOT/'translation/385_story_key_items.audit.generated.json',{'local_reuse':reuse,'key_item_indices':sorted(TEXT),'excluded_indices':[r['message_index'] for r in catalog.values() if r['source']==SOURCE and not r.get('translation') and r['message_index'] not in TEXT],'runtime_tested':False})
    print('Story-related descriptions and opening quote:',sum(map(len,sources.values())))

if __name__=='__main__':main()
