"""Complete Marie boss navigation, leaving explicit placeholders untouched."""
import hashlib,re,unicodedata
from collections import Counter,defaultdict
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING
TEXT={
125:['等等……\n扑克牌士兵太多了……'],126:['哇！？\n又来了！'],127:['真是的，这些家伙没完没了。\n讨厌！'],128:['敌人是扑克牌士兵！\n好多！'],130:['啊，现在没有扑克牌士兵。\n这不是机会吗！'],131:['啊！\n叫来扑克牌士兵了！'],132:['女王走到前面来了。'],133:['啊……女王的体力，\n开始减少了。'],134:['女王的体力，\n已经减少很多了！'],135:['女王变弱了！\n大概就差一点了！'],136:['那个牧师，大概是这里的守卫……\n……我猜的。'],137:['咦……刚才，\n他说“发誓不动手打人”了吗？'],138:['喂，那家伙刚才说了\n“发誓不使用技能”吗？'],139:['咦？喂，刚才他说了\n“发誓不使用道具”吗？'],140:['喂，那家伙刚才说了\n“发誓不逞威风”吗？'],141:['这家伙烦死了！\n这次说“发誓不动手打人”。'],142:['真是的，又来？\n他说“发誓不使用技能”。'],143:['又在说什么了……\n这次说“发誓不使用道具”。'],144:['那家伙就知道叫人发誓……\n这次说“发誓不逞威风”。'],145:['咦！？誓言，\n违背了就会那样？'],146:['啊……\n现在好像没有誓言了。'],147:['哇！怎么一下子，\n被逼着发了好几个誓！！'],148:['那个牧师，\n已经虚弱很多了！'],149:['我、我才不怕怕呢……一点都\n不怕，肯定只是看着吓人而已已……'],150:['咦？\n医生在蓄力？'],151:['刚才那是什么？很危险吧？\n你们没事吧？'],152:['打倒护士了！\n还剩２名！'],153:['干得不错嘛！\n只剩医生了！'],154:['等等，搞什么！\n医生在恢复体力？'],155:['咦……\n医生变强了？'],156:['医生的体力减少了！\n……虽然只有一点。'],157:['医生的体力，\n已经减少不少了。'],158:['医生的体力只剩一点了。\n要加油啊。'],160:['等等……这家伙声音也太大了！\n耳朵都嗡嗡响了！！'],161:['那招是不是很厉害？\n喂，没事吧？'],162:['等等……\n刚、刚才那下没事吧！？'],163:['兔子的体力，\n开始减少了。'],164:['兔子的体力减少很多了。\n感觉不错。'],165:['兔子的体力只剩一点了。\n胜利就在眼前哦。'],166:['咦！？搞什么！我可没听说\n还能复活，搞不懂啊！'],168:['瞄准那个头就行了吧？\n……大概。'],169:['那家伙搞什么！用前脚护住头？\n太狡猾了！！'],170:['话说……\n只能先破坏脚了吧！'],171:['原来如此……\n那些脚的弱点不一样啊……'],172:['不错嘛。还剩３条。','成功了。还剩３条。','感觉不错吧？\n还剩３条。'],173:['哦……成功了。\n还剩２条。','感觉不错吧？\n还剩２条。','成功了。\n还剩２条呢。'],174:['成功了，打坏了！\n还剩１条！','很厉害嘛。\n还剩１条哦。','啊……厉害厉害，\n还剩１条！'],175:['攻击化作咆哮，将面具撕……\n咳咳，头全露出来了！！'],176:['咦！？搞什么，搞不懂！！\n脚还能复活！？太狡猾了吧！？'],177:['这家伙气死人了！\n脚又复活了。','这家伙太狡猾……就是狡猾！\n脚又复活了。','这算什么？搞不懂啊！\n脚又复活了。','什么家伙！卑鄙！狡猾！！\n脚又复活了！！','咦……那些脚，\n是按各自的时间复活的？','要是在相近时间破坏４条脚……\n能不能让头多露出来一会儿？'],178:['啊，蜘蛛的体力，\n开始减少了。'],179:['蜘蛛的体力只剩一点了。\n可不许大意！'],180:['这肯定……是最后一战了……\n一、一定要赢啊！……给我赢！'],
181:['副队长的倒计时到１了哦！','哇！\n副队长，倒计时到１了！','哇，阳介危险了！\n已经到１了！','千枝的倒计时到１了哦？\n你注意到了吧？','啊！\n雪子的倒计时到１了！',None,'完二的倒计时很危险！\n已经到１了！','直斗的倒计时到１了。\n离死就差一步了！','小熊的倒计时到１了吧？\n就是１啊！','有看由加莉的倒计时吗？\n已经到１了！','等等……顺平的倒计时，\n已经到１了！','真田，倒计时到１了哦！','哇！美鹤没问题吗？\n是１啊，１！',None,'等等，注意到了吗？注意到了吧？\n埃癸斯已经到１了！','啊！乾的倒计时到１了！\n离绝境只剩５秒了啊！','哇！看狗狗，看狗狗！\n倒计时到１了！','哇！荒垣已经到１了！',None,'善的倒计时到１了！\n你、你注意到了吧？','你、你的倒计时到１了哦！\n不、不着急吗？','队长的倒计时到１了。\n死亡就在眼前了！'],
182:['哇！？什么啊，不敢相信！！\n倒计时突然加快了！'],183:['克洛诺斯的体力，\n开始减少了，虽然只有一点。'],184:['克洛诺斯的体力，\n减少了不少。感觉不错。'],185:['就、就差一点了！\n加、加油啊！！'],186:['咦！？违背誓言就会那样！？\n可、可是现在誓言没有生效啊。']}

def main():
    TEXT[125][0]='等等……\n扑克牌太多了……'
    TEXT[128][0]='敌人是扑克牌！\n好多！'
    TEXT[131][0]='啊！\n叫来扑克牌了！'
    TEXT[171][0]='原来如此……\n那些脚的弱点不同啊…'
    TEXT[183][0]='克洛诺斯的体力，\n稍微减少了。'
    path=ROOT/'translation/batches/401_marie_completion.generated.json';assert not path.exists()
    rows=read(ROOT/'translation/catalog.working.json');index=defaultdict(list)
    for r in rows:
        if r.get('translation') and '/battle/support/' in r['source']:index[r['original']].append(r)
    sources=defaultdict(list);audit=[];seen=set()
    for r in rows:
        if r.get('translation') or not r['source'].startswith('export_dlc/0008/battle/support/'):continue
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
    write(path,dict(status='draft',sources=dict(sources),source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},reuse_audit=audit,review_notes=['玛丽最后88个有效战斗导航页；克洛诺斯、誓言及数值沿用既有约定。','保留诗句与结巴；未运行验证。']))
    print('Pages:',len(seen),'exact reuse:',len(audit))

if __name__=='__main__':main()
