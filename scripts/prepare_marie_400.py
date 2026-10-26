"""Marie analysis and defeat; exact-source reuse only."""
import hashlib,re,unicodedata
from collections import Counter,defaultdict
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING
TEXT={
69:['那个敌人弱于斩击属性。就是那种\n斩断一切的英杰之剑！之类的。'],70:['那个敌人弱于突击属性吧。\n贯穿一切的闪光之枪……之类的。'],71:['那个敌人弱于坏击属性。\n粉碎一切的毁灭铁锤！……那种。'],72:['那个敌人弱于火焰属性吧。\n烧尽一切的炼狱之炎……之类的。'],73:['那个敌人弱于冰冻属性。就是那种\n冻结一切的寒冰之棺……之类的。'],74:['那个敌人弱于电击属性。就是那种\n审判一切的制裁之雷……之类的。'],75:['那个敌人弱于疾风属性。\n撕裂一切的真空之刃……之类的。'],76:['那个敌人弱于光属性。\n净化漆黑的神圣之光……那种。'],77:['那个敌人弱于暗属性。就是那种\n吞噬一切的地狱深渊……之类的。'],78:['那个敌人弱于万能属性。\n毁灭一切的创世之力……那种。'],
79:['敌人还剩１名。','敌人还剩１名哦。'],80:['敌人还剩２名。','还剩２名哦。'],81:['还有３名呢。','还有３名哦。'],82:['还剩４名。\n话说，好多。','敌人还剩４名。'],83:['敌人还有５名。'],84:['呜哇……还有６名。'],85:['还有好多呢。'],101:['高呼胜利吧！','啊……打得不错。','好像……好厉害……\n我、我也在给你们加油啊！'],102:['啊！逃走了！\n简直不敢相信！！','哇！？逃、逃跑什么的，\n搞不懂啊！'],
103:['啊！你！！怎么会……以后不能\n一起出去玩了吗？我不要这样……','咦！你！？被打倒了……？\n骗人的，我才不信！！'],104:['啊！你！！怎么会……以后不能\n一起出去玩了吗？我不要这样……','咦！你！？被打倒了……？\n骗人的，我才不信！！'],105:['等等……队长！！咦……为什么？\n我可没听说会这样……骗人的吧！','咦！队长！？骗人，骗人，\n骗人的吧？回答我啊！！'],106:['啊！副队长！那就全灭了……？\n这……这种事……怎么可能！！','咦！副队长！怎么会……\n等等……谁来回答我啊！'],107:['啊！由加莉！！……咦，全灭？\n骗人的……这算什么啊！'],108:['啊！顺平！！怎么会……\n全灭了吗？这……糟透了……'],109:['哇！真田！！被打倒了……？\n那就全灭了……骗人吧？喂！'],110:['啊！美鹤！那大家都……？\n怎么会……不可能！骗人的吧！'],111:['哇！乾！！……怎么会……\n还有人吗？回答我啊！喂！'],112:['啊！狗狗！……怎么会……\n全灭什么的都是假的……谁回答我！'],113:['啊！埃癸斯！骗人……为什么……\n肯定还有人没事！这不可能！'],114:['咦！荒垣……被打倒了？\n等等……这样就结束了？骗人的吧……'],115:['咦！阳介！！被打倒了……？\n开玩笑吧，假的吧？喂，谁来啊！'],116:['咦！千枝！被打倒了……？\n等等……得有人去救她……谁来……喂！'],117:['啊！雪子！怎么会……\n谁来回答我啊！喂！谁来啊！'],118:['咦！完二！那、那大家都……？\n不可能……这不可能啊！'],119:['咦！小熊！！你在干什么……\n什么到此为止……不该这样啊！'],120:['啊！直斗！！……骗、骗人……\n搞不懂，不该这样啊！！'],121:['啊！善，玲！咦……那就\n全灭了吗……？这都是骗人的！'],122:['啊！善！被……打倒了……？\n全灭了吗？怎么会……没人了吗？']}

def main():
    TEXT[70][0]='那个敌人弱于突击属性吧。\n贯穿一切的闪光之枪…之类的。'
    TEXT[101][2]='好像……好厉害……\n我、我也在给你们加油！'
    path=ROOT/'translation/batches/400_marie_analysis_defeat.generated.json';assert not path.exists()
    rows=read(ROOT/'translation/catalog.working.json');index=defaultdict(list)
    for r in rows:
        if r.get('translation') and '/battle/support/' in r['source']:index[r['original']].append(r)
    sources=defaultdict(list);audit=[];seen=set()
    for r in rows:
        if r.get('translation') or not r['source'].startswith('export_dlc/0008/battle/support/'):continue
        m=int(re.search(r'_\((\d+)\)',r['source'])[1]);i=r['message_index'];j=r['line_index']
        if not 69<=m<=122 or TOKEN.sub('',r['original']).strip()=='ダミーだよ':continue
        body=TEXT[m][i]+'\n';refs=index.get(r['original'],[])
        if refs and len({x['translation'] for x in refs})==1:
            body=TRAILING.sub('',LEADING.sub('',refs[0]['translation']));audit.append({'key':r['key'],'reference':refs[0]['key']})
        a=TOKEN.sub('',r['original']).splitlines();b=body.splitlines()
        assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),(m,i,max(map(len,b)),max(map(len,a)))
        nums=lambda t:Counter(re.findall(r'\d+',unicodedata.normalize('NFKC',TOKEN.sub('',t))))
        assert nums(body)==nums(r['original']);assert j==0
        doc=read(ROOT/r['source']);sources[r['source']].append([i,j,doc['texts'][i]['id'],body]);seen.add((m,i))
    assert seen=={(m,i) for m,v in TEXT.items() for i in range(len(v))}
    write(path,dict(status='draft',sources=dict(sources),source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},reuse_audit=audit,review_notes=['玛丽分析、剩余敌人数、声援和战败独有提示；保留夸张修辞。','万能弱点等文本不表示运行中确认触发；未运行测试。']))
    print('Pages:',len(seen),'exact reuse:',len(audit))

if __name__=='__main__':main()
