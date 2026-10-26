"""Nanako final boss warnings and countdowns."""
import hashlib,re,unicodedata
from collections import Counter,defaultdict
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING
TEXT={
125:['哇！扑克牌\n好多啊！'],126:['啊！扑克牌们，\n又来了！'],127:['又来了！！\n太多了啊！'],128:['扑克牌，\n有好多啊！'],130:['现在只有女王！\n就趁现在！'],131:['啊！她叫来扑克牌了！'],132:['啊，女王走到前面来了！'],133:['啊！女王，\n好像有点痛了！'],134:['女王的体力，\n好像减少很多了！'],135:['一定就差一点了！\n加油！'],136:['这个人，\n一定就是这里的守卫吧。'],137:['刚才……发誓不动手打人……\n……他是这么说的吧？'],138:['刚才他说，发誓不使用技能……\n……是这么说的。'],139:['刚才他说，发誓不使用道具……\n……是这么说的吗？'],140:['什么意思？他说发誓不逞威风，\n是吧？这是什么意思呢……'],141:['这次他说，发誓不动手打人！\n菜菜子听见了！'],142:['这次是，发誓不使用技能……\n……他说的。技能是什么？'],143:['啊，这次是，\n发誓不使用道具。'],144:['这次他说，\n发誓不逞威风！'],145:['咦……违背誓言，\n就会被这样对待吗？'],146:['咦！？现在好像\n什么都不用发誓了！'],147:['哇！好像有好几件\n不能做的事！'],148:['啊！好像快要赢了！\n加油！！'],149:['呜……菜、菜菜子，\n好怕这个敌人啊。'],150:['咦？医生好像\n正在使劲蓄力！！'],151:['哇，刚、刚才好厉害啊！\n没事吧？'],152:['太好了！打赢护士了！\n只剩两个人了呢！'],153:['啊，太好了！\n只剩那个医生了呢！'],154:['哇，医生恢复了！'],155:['啊！医生好像\n变强了！'],156:['啊，医生在喊痛！'],157:['医生开始累了！\n加油！！'],158:['好像就差一点就能赢了！！\n加油啊！'],160:['嗯……耳朵嗡嗡响……\n刚才的声音好大啊……'],161:['哇哇，它做了好厉害的事！\n没事吧？'],162:['哇哇哇，没事吧！？\n刚才那下好厉害啊！！'],163:['啊，兔子，\n可能有点虚弱了！'],164:['兔子，\n好像已经很累了！'],165:['啊！好像快要赢了！\n加油啊！'],166:['哇哇哇！兔子，\n又精神起来了！'],168:['好像只要瞄准\n那个头就行了！'],169:['咦！？\n它用脚把头护住了！'],170:['有那些脚挡着，\n就瞄不到头了呢……'],171:['原来如此……那些脚，\n害怕的东西都不一样啊……'],172:['太好了！\n还剩一……二……３条哦！','啊，脚消失了！\n还剩３条哦！','太好了，太好了！\n还剩３条哦！'],173:['啊，脚消失了！\n还剩２条呢！','太好了！\n还剩２条哦！','啊，脚不见了！\n还剩２条呢！'],174:['成功了！\n还剩１条哦！','好厉害！\n还剩１条脚哦！'],175:['啊！头露出来了！\n现在就能瞄准了！'],176:['咦！？\n脚恢复了……'],177:['好厉害……\n蜘蛛又把脚治好了……','脚又恢复了！\n这太狡猾了啊！','哇，脚又恢复了……\n难道能一直恢复吗……','呜……脚又恢复了……\n为什么……','那些脚，\n好像过一会儿就恢复了……','原来如此，好像是按\n被破坏的顺序恢复的！'],178:['啊，蜘蛛好像\n开始累了！'],179:['啊！好像就差一点就能赢了！\n加油啊！'],180:['我觉得……这一定\n就是最后一战了。'],
181:['哥哥，要小心！\n数字是１哦！','副队长的数字\n变成１了！','啊！阳介哥哥的数字，\n已经变成１了！','千枝姐姐的数字是１哦！','啊！雪子姐姐！\n数字是１哦！',None,'完二哥哥，数字是１哦！\n得小心才行！','不好了！直斗姐姐的数字\n只剩１了！','小熊先生的数字，\n只剩１了哦！','啊！由加莉姐姐的数字，\n已经是１了！','顺平哥哥，要小心！\n数字变成１了！','真田哥哥，\n已经变成１了！','美鹤姐姐，要小心！\n数字是１哦！',None,'埃癸斯姐姐的数字，\n只剩１了哦！','啊！乾的数字，\n已经是１了！','啊！小虎的数字，\n已经只剩１了！','荒垣哥哥！\n数字已经是１了哦！',None,'善哥哥！数字是１哦！','哥哥！\n数字已经是１了哦！！','不好了！队长的数字，\n只剩１了！'],
182:['咦！？为什么！？\n数字突然变快了！！'],183:['克洛诺斯，\n好像有点累了！'],184:['啊！克洛诺斯的体力，\n减少好多了！'],185:['就差一点就能赢了！！\n加油啊！！'],186:['违背……誓言，好可怕啊……\n啊，不过现在好像做什么都行！']}
TEXT[174].append('加油啊！\n还剩１条哦！')

def main():
    TEXT[136][0]='这个人，\n一定是这里的守卫吧。'
    path=ROOT/'translation/batches/407_nanako_completion.generated.json';assert not path.exists()
    rows=read(ROOT/'translation/catalog.working.json');index=defaultdict(list)
    for r in rows:
        if r.get('translation') and '/battle/support/' in r['source']:index[r['original']].append(r)
    sources=defaultdict(list);audit=[];seen=set()
    for r in rows:
        if r.get('translation') or not r['source'].startswith('export_dlc/0009/battle/support/'):continue
        m=int(re.search(r'_\((\d+)\)',r['source'])[1]);i=r['message_index'];j=r['line_index']
        if m<123 or TOKEN.sub('',r['original']).strip() in ('ダミーだよ','ダミーのまま入れ込む'):continue
        body=TEXT[m][i]+'\n';refs=index.get(r['original'],[])
        if refs and len({x['translation'] for x in refs})==1:
            body=TRAILING.sub('',LEADING.sub('',refs[0]['translation']));audit.append({'key':r['key'],'reference':refs[0]['key']})
        a=TOKEN.sub('',r['original']).splitlines();b=body.splitlines()
        assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),(m,i,max(map(len,b)),max(map(len,a)))
        nums=lambda t:Counter(re.findall(r'\d+',unicodedata.normalize('NFKC',TOKEN.sub('',t))))
        assert nums(body)==nums(r['original']),(m,i);assert j==0
        doc=read(ROOT/r['source']);sources[r['source']].append([i,j,doc['texts'][i]['id'],body]);seen.add((m,i))
    assert len(seen)==88
    write(path,dict(status='draft',sources=dict(sources),source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},reuse_audit=audit,review_notes=['菜菜子最后88个有效战斗导航页，保留数字称呼、儿童反应及原文复活顺序描述。','沿用克洛诺斯和誓言术语；不强套其他导航复活时间描述，未运行验证。']))
    print('Pages:',len(seen),'exact reuse:',len(audit))

if __name__=='__main__':main()
