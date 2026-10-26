"""Marie confusion, seals and debuffs, preserving character observations."""
import hashlib
from collections import defaultdict
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING
from prepare_margaret_393 import IDS
NAMES=['副队长','副队长','阳介','千枝','雪子','完二','直斗','小熊','由加莉','顺平','真田','美鹤','埃癸斯','乾','狗狗','荒垣','善和玲','善','你','队长']
CONF=['咦……副队长好像怪怪的……\n抱着头，摇摇晃晃的……','副队长的样子有点怪。\n还东张西望的……','阳介是不是有点怪？\n东张西望，还大喊大叫……','咦……千枝怎么了？\n一直东张西望的……','雪子没事吧？\n怎么摇摇晃晃的。','完二有点怪。\n抬着头，不知道在说什么……','直斗有点怪啊。\n到处指来指去的……','小熊……怎么了？\n好像……在跳舞？','由加莉的样子有点怪。\n混乱了？','顺平怎么了？\n抱着头大喊大叫的……','真田怎么了？\n一直东张西望的……','咦……美鹤没事吧？\n她是不是把剑朝向这边了？','埃癸斯有点怪啊。\n一直抱着头……','乾有点怪。\n抱着头，还东张西望的……','咦……狗狗怎么了？\n一直在低吼……','荒垣好像有点怪。\n一直东张西望的。','善和玲怎么了？\n玲怎么……一直东张西望的……','善有点怪。\n把武器朝向各个方向……','咦……你怎么了？\n混乱了？','队长，混乱了？\n喂——？']
DEF=['被打中肯定很痛哦。','肯定比平时更痛哦。','低得叫人失望。','现在被打中会很痛的。','被打中应该会很痛……','这不危险吗？','还是小心一点吧。','被打中应该会很痛。','被打中肯定很痛哦。','大概会比平时更痛吧。','挨打肯定很痛哦。','现在挨打会很痛哦。','被打中也许会很痛呢……','被打中应该会很痛。','被打中也许会很痛。','被打中应该会比平时更痛。','被打中肯定很痛哦。','还是小心一点吧……','挨打应该会很痛。大概。','受到攻击肯定很痛哦。']
SPD=['动作变慢了。','动作怎么……看着真着急。','动作一点都不利索了……','啊……难道是太极拳？','话说，好慢。','看着就着急。','动作好慢。','咦……没事吧？','动作怎么……慢悠悠的。','速度下降了哦。','动作怎么……轻飘飘的。','动作怎么……沉甸甸的……','好慢……简直是慢吞吞的。','……话说，好慢。','动作变得好迟钝……','毕竟这么慢……看着就着急……','两个人都好慢。','动作好慢。','动作好慢。','动作变慢了哦。']

def body_for(m,i,k,n):
    if m==61:return CONF[k]+'\n'
    if m in (64,66) and i==18:n='善'
    if m==64:
        first=n+'被封印了。'
        if i in (0,15,18,19):first='啊……'+first
        if i==10:first='啊……顺平被封印了……'
        if i==7:first='直斗好像被封印了。'
        tail='现在只能用物理攻击。'
        if i==2:tail='只能用物理攻击，真叫人失望。'
        return first+'\n'+tail+'\n'
    if m==65:
        first=n+'的行动被封印了。'
        if i==21:first='队长，行动被封印了？'
        tail='现在没法回避或逃跑。'
        if i==15:tail='躲不了，也逃不掉。……绝对。'
        return first+'\n'+tail+'\n'
    if m==66:
        if i==16:return '狗狗变弱了。\n攻击力下降了……\n'
        if i==21:return '队长，下降了哦。\n攻击力。\n'
        return n+'的攻击力下降了。'+('\n……还是小心一点比较好……' if i==0 else '\n比平时弱了。' if i==20 else '')+'\n'
    if m==67:return n+'的防御力下降了。\n'+DEF[k]+'\n'
    if m==68:
        first=n+'的速度下降了。'
        if i in (12,17,20):first=n+'的速度下降了吧？'
        if i==10:first='顺平变慢了。'
        return first+'\n'+SPD[k]+'\n'
    raise AssertionError(m)

def main():
    CONF[IDS.index(6)]='完二有点怪。\n抬着头，不知在说什么……'
    path=ROOT/'translation/batches/399_marie_binds_debuffs.generated.json';assert not path.exists()
    rows=read(ROOT/'translation/catalog.working.json');catalog={r['key']:r for r in rows};index=defaultdict(list)
    for r in rows:
        if r.get('translation') and '/battle/support/' in r['source']:index[r['original']].append(r)
    sources=defaultdict(list);reuse=[]
    for m in (61,64,65,66,67,68):
        source=f'export_dlc/0008/battle/support/bsv124.bvp_({m:03}).BMD.json';doc=read(ROOT/source)
        for k,(i,n) in enumerate(zip(IDS,NAMES)):
            row=catalog[f'{source}:{i}:0'];assert not row.get('translation');body=body_for(m,i,k,n)
            refs=index.get(row['original'],[])
            if refs and len({r['translation'] for r in refs})==1:
                body=TRAILING.sub('',LEADING.sub('',refs[0]['translation']));reuse.append({'target':row['key'],'reference':refs[0]['key']})
            a=TOKEN.sub('',row['original']).splitlines();b=body.splitlines()
            assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),(m,i,max(map(len,b)),max(map(len,a)))
            sources[source].append([i,0,doc['texts'][i]['id'],body])
    write(path,dict(status='draft',sources=dict(sources),source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},review_notes=['玛丽061/064—068共120页；062/063既有共用译文保留。','完整原文及控制码精确匹配优先复用，独有语气单独翻译；运行未验证。'],reuse_audit=reuse))
    print('Pages:',sum(map(len,sources.values())),'exact reused:',len(reuse))

if __name__=='__main__':main()
