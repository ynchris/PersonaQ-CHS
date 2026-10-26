"""Nanako encounters: preserve childlike counting and original omissions."""
import hashlib,re,unicodedata
from collections import Counter,defaultdict
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING
TEXT={
0:['啊，是Ｆ……什么来着！\n得快点逃！','啊，Ｆ……什么来着，来了！\n得快点逃！很危险哦！','菜、菜菜子怕这个敌人！\n快点逃吧！'],1:['不、不行……这个敌人……\n快……快点逃……快点！'],2:['咦……虽然是ＦＯＥ……\n但现在好像没那么可怕了……','这个ＦＯＥ的话，\n菜菜子不怎么害怕！','这个ＦＯＥ……\n好像不怎么强……'],3:['啊，是敌人！\n它们先来！'],4:['有２名敌人！\n它们先过来了！'],5:['啊，有３名敌人！\n它们先过来了！'],6:['敌人有，一……二……\n等一下啦！'],7:['哇，好多敌人啊！\n先轮到它们！'],8:['来了６名敌人！\n好像是它们先来！'],9:['敌人好多好多啊！\n怎么办！'],10:['啊，闪闪发光的先来！','啊，有闪闪发光的！\n不过，好像先轮到它们。','啊……闪闪发光的来了！\n这个很少见，对吧？'],11:['啊，那个敌人闪闪发光！\n好漂亮啊……','哇，有闪闪发光的！\n菜菜子想摆在房间里！','啊，那个很少见，对吧？\n得加油打倒它！','啊，是闪闪发光的！\n不快点就要逃走了！','那个闪闪发光的敌人……\n为什么会闪闪发光呢？'],12:['有１名不认识的。','有１名敌人！加油！'],13:['有２名敌人。也有不认识的！','敌人有２名哦！'],14:['那个……有３名敌人！\n也有不认识的。','有３名敌人哦。\n要小心哦！'],15:['敌人有……一……二……\n啊，也有不认识的……','敌人有……那个……\n一……二……４名哦！'],16:['哇哇……那个……敌人……\n也有不认识的……那个……','哇，敌人好多啊！\n没事吧？'],17:['那个……有不认识的……\n一共……６名！','哇哇哇，来了６名！\n好多啊！'],18:['总之，有好多敌人！\n还有不认识的！','哇，有好多！\n不要勉强哦。'],19:['呜……虽然不太清楚……\n菜菜子怕这个敌人……','啊，是很强的敌人！\n要小心！'],20:['哇哇……好像很强！\n还有不认识的……','啊，这个敌人很强！\n不要勉强哦！'],21:['啊，来了３名很强的敌人！\n也有不认识的！','有３名很强的！\n怎么办……'],22:['来了４名很强的敌人！\n也有不认识的！','哇哇，有４名很强的！'],23:['啊，来了５名很强的敌人！\n还有不认识的！','来了５名很强的！'],24:['哇哇，好多很强的！\n也有不认识的哦！','啊！全是很强的！\n很危险哦！'],25:['啊，好多很强的敌人！\n也有不太认识的！','全是很强的敌人！\n我们快逃吧！'],26:['这个敌人……菜菜子已经不怕了。'],27:['这个敌人不怎么可怕。\n虽然也有不认识的……','这个敌人的话，不可怕！'],28:['有３名敌人。虽然也有不认识的，\n但一定没事的。','有３名敌人。\n已经不是可怕的敌人了。'],29:['有４名不太可怕的敌人。\n啊……有不认识的。','敌人有４名。\n但不是可怕的哦！'],30:['嗯……虽然不是可怕的敌人……\n但也有不认识的，要小心哦。','虽然不是可怕的敌人，\n但数量很多。要小心哦！'],31:['有好多啊……\n好像也有不认识的。','哇……来了好多……\n这么多，没问题吗？'],32:['这么多，太狡猾了……\n还有不认识的。','哇……来了好多……\n菜菜子有点害怕……'],33:['有１名敌人。\n先轮到我们！'],34:['有２名敌人。\n现在也许是个机会！'],35:['啊，先轮到我们哦！\n敌人有３名！'],36:['敌人有……一……二……\n啊，不过先轮到我们！'],37:['敌人有５名！\n不过先轮到我们！'],38:['有好多敌人！\n不过是我们先来！'],39:['敌人好多好多啊！\n虽然先轮到我们，但怎么办？'],40:['那个敌人好像很强……\n虽然先轮到我们，但怎么办？'],41:['那个敌人……好像很强……\n虽然我们先来……要加油吗？'],42:['哇……有３名很强的……\n虽然我们先来，但怎么办？'],43:['有４名可怕的敌人……\n虽然我们先来，但要怎么办？'],44:['有好多很强的敌人……\n虽然我们先来，但菜菜子好怕……'],45:['哇，全是可怕的敌人！\n我们快逃吧！'],46:['啊……好多好多可怕的敌人……\n不能跟这样的家伙打架啊……'],47:['啊，有闪闪发光的！\n这是个机会，对吧？','我们先来哦！\n还有闪闪发光的！！','啊，是闪闪发光的！\n趁现在打倒它吧！'],48:['啊，ＦＯＥ，\n闯进来了！','啊！ＦＯＥ来了！','啊，ＦＯＥ！\n明明不能过来的……'],49:['虽然ＦＯＥ来了……\n但好像不是很可怕的。'],50:['怎么办……\nＦＯＥ又来了……','真是的……ＦＯＥ又来了！\n怎么办……'],52:['哇！埃癸斯姐姐，\n好厉害！','菜菜子知道哦，埃癸斯姐姐\n变得好强！'],53:['哇！埃癸斯姐姐，\n动不了了！','埃癸斯姐姐，\n好像得冷却以后才能动。']}
TEXT[26].append('啊，这个敌人我认识！\n不过，已经不可怕了。')

def main():
    TEXT[14][0]='那个……３名敌人！\n也有不认识的。'
    TEXT[43][0]='有４名可怕的敌人……\n虽然我们先来，要怎么办？'
    TEXT[44][0]='有好多很强的敌人……\n我们先来，但菜菜子好怕……'
    target=ROOT/'translation/batches/402_nanako_encounters.generated.json';assert not target.exists()
    rows=read(ROOT/'translation/catalog.working.json');index=defaultdict(list)
    for r in rows:
        if r.get('translation') and '/battle/support/' in r['source']:index[r['original']].append(r)
    sources=defaultdict(list);audit=[];seen=set()
    for r in rows:
        if r.get('translation') or not r['source'].startswith('export_dlc/0009/battle/support/'):continue
        m=int(re.search(r'_\((\d+)\)',r['source'])[1]);i=r['message_index'];j=r['line_index']
        if m>53:continue
        body=TEXT[m][i]+'\n';refs=index.get(r['original'],[])
        if refs and len({x['translation'] for x in refs})==1:
            body=TRAILING.sub('',LEADING.sub('',refs[0]['translation']));audit.append({'key':r['key'],'reference':refs[0]['key']})
        a=TOKEN.sub('',r['original']).splitlines();b=body.splitlines()
        assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),(m,i,max(map(len,b)),max(map(len,a)))
        nums=lambda t:Counter(re.findall(r'\d+',unicodedata.normalize('NFKC',TOKEN.sub('',t))))
        assert nums(body)==nums(r['original']),(m,i);assert j==0
        doc=read(ROOT/r['source']);sources[r['source']].append([i,j,doc['texts'][i]['id'],body]);seen.add((m,i))
    assert seen=={(m,i) for m,v in TEXT.items() for i in range(len(v))};assert len(seen)==91
    write(target,dict(status='draft',sources=dict(sources),source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},reuse_audit=audit,review_notes=['菜菜子000—053有效剩余91页；保留数数、闪闪发光及记不住F.O.E名称的口吻。','不补原文未给出的敌人数目；051旧译保留，运行未验证。']))
    print('Pages:',len(seen),'exact reuse:',len(audit))

if __name__=='__main__':main()
