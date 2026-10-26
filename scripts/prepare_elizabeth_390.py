"""Finish every non-dummy page of Elizabeth's DLC battle support bank."""
import hashlib
import re
import unicodedata
from collections import Counter,defaultdict
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING
from prepare_elizabeth_388 import IDS,NAMES

TEXT={125:['哎呀……\n扑克牌士兵接连出现……'],126:['又来了呢……'],127:['扑克牌士兵\n再次驾到了。'],128:['敌人，扑克牌士兵……\n……连数都嫌麻烦了……'],129:['不过，刚才那些家伙……\n为什么会在这里？'],130:['现在应该能直接与女王交锋……\n正是良机！……是也。'],131:['啊……\n她把扑克牌士兵召来了……'],132:['看来已经能接近女王了。\n正是进攻时机……'],133:['女王的体力\n似乎开始减少了……'],134:['女王的体力似乎减少了不少……\n请继续保持，猛烈进攻。'],135:['女王的体力\n已经所剩无几了。'],136:['看来……\n那就是这里的守卫呢……'],137:['刚才……似乎说了\n“发誓不动手打人”……'],138:['刚才说……“发誓不使用技能”。\n在下没有听错吧？'],139:['刚才……似乎说了\n“发誓不使用道具”……'],140:['刚才说了“发誓不逞威风”……\n对吧？'],141:['这次是“发誓不动手打人”\n……如是说。'],142:['这次是“发誓不使用技能”\n……如是说。'],143:['这次是“发誓不使用道具”\n……如是说。'],144:['这次是“发誓不逞威风”\n……如是说。'],145:['原来如此……违背所谓的誓言，\n就会遭受那样的惩罚呢……'],146:['哎呀……现在似乎\n没有任何誓言在生效……'],147:['看来有几种行动\n被誓言禁止了……'],148:['牧师的体力\n似乎已经减少了不少。'],149:['这敌人……很有压迫感……\n要是让西奥多看见……嘀咕……'],150:['医生正在蓄力呢……\n不妨先提高警惕？'],151:['这真是……相当有力的攻击……\n虽是敌人，也值得喝彩！'],152:['真是漂亮。\n还剩２名呢。'],153:['这下随从都解决了……\n只剩医生了。'],154:['哎呀……\n医生的体力恢复了呢……'],155:['哦……\n医生的能力提升了。'],156:['医生的体力\n似乎“稍微”减少了。'],157:['医生的体力\n似乎减少了“不少”。'],158:['医生的体力\n似乎减少了“很多”。'],159:['嗯，得先让它安静下来！'],160:['声音真惊人呢……\n是的……简直扰民……'],161:['刚才的攻击威力相当可观……\n若被击中，恐怕不堪一击……'],162:['兔子也很有智慧呢……\n各位是否平安？'],163:['兔子的体力\n似乎稍微减少了。'],164:['兔子的体力\n似乎已经减少了不少。'],165:['兔子的体力所剩无几。\n胜利就在眼前。'],166:['……真令人意外。\n通常早该倒下了……'],167:['一定！一定一定！\n要救出玲！'],168:['看来应该攻击那个头……\n来吧，攻击面部！'],169:['它用前脚\n护住了头部呢……'],170:['先把碍事的脚\n破坏掉吧。'],171:['原来如此……\n每条脚的弱点都不同呢……'],172:['漂亮。\n还剩３条脚。','破坏掉了呢……\n还剩３条。','好一击……\n还剩３条呢。'],173:['破坏掉了呢……\n还剩２条。','精彩！\n还剩２条。','漂亮。\n还剩２条呢。'],174:['漂亮。\n还剩１条。','破坏掉了呢。\n只剩１条了！','真是漂亮的攻击。\n接下来只剩１条。'],175:['蜘蛛的头彻底露出来了！\n……是也。正是进攻时机。'],176:['什么……\n复活了……？'],177:['又复活了……\n真是狡猾的脚……','脚……\n再次复活了……','脚复活了……\n真是没完没了呢……','脚又复活了……\n……令人烦躁……','那些脚……似乎会\n按各自的时间复活……','即使逐一破坏，先打倒的脚\n似乎也会重新复活……'],178:['蜘蛛的体力\n似乎稍微减少了。'],179:['蜘蛛的体力已经减少了不少呢……\n胜利就在眼前！……是也。'],180:['请做好觉悟。\n这恐怕就是最后一战了。'],182:['哎呀……倒计时似乎突然加快了……'],183:['虽然只有一点，\n克洛诺斯的体力开始减少了。'],184:['克洛诺斯的体力\n似乎已经减少了不少。'],185:['克洛诺斯的体力所剩无几了呢……'],186:['违背誓言就会遭到那样的惩罚……\n总之，现在没有任何誓言。']}

def main():
    TEXT[129][0]='不过，刚才那些……\n为什么会在这里？'
    TEXT[176][0]='什么……\n复活了？'
    path=ROOT/'translation/batches/390_elizabeth_completion.generated.json';assert not path.exists()
    names=dict(zip(IDS,NAMES));sources=defaultdict(list)
    for r in read(ROOT/'translation/catalog.working.json'):
        source=r['source']
        if r.get('translation') or not source.startswith('export_dlc/0006/battle/support/bsv121.bvp_') or 'ダミー' in r['original']:continue
        m=int(re.search(r'_\((\d+)\)',source)[1]);i=r['message_index'];j=r['line_index'];old=r['original']
        if m==181:
            body=names[i]+'的倒计时为１。'
            if old.count('\n')==2:body=names[i]+'的倒计时\n为１。'
        else:body=TEXT[m][i]
        body+='\n';full=LEADING.match(old).group()+body+TRAILING.search(old).group()
        assert TOKEN.findall(full)==TOKEN.findall(old)
        nums=lambda t:Counter(re.findall(r'\d+',unicodedata.normalize('NFKC',TOKEN.sub('',t))))
        assert nums(full)==nums(old),(m,i)
        a=TOKEN.sub('',old).splitlines();b=body.splitlines()
        assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),(m,i)
        doc=read(ROOT/source);sources[source].append([i,j,doc['texts'][i]['id'],body])
    assert sum(map(len,sources.values()))==91
    write(path,dict(status='draft',sources=dict(sources),source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},review_notes=['伊丽莎白DLC战斗导航剩余91页全部补齐；dummy保留。','保留誓言禁令、蜘蛛脚数量/各自复活时间、死亡倒计时数字及克洛诺斯译名。','完成范围为bsv121战斗导航文字，不代表全部导航员或游戏运行已验证。']))
    print('Elizabeth remaining pages:',sum(map(len,sources.values())))

if __name__=='__main__':main()
