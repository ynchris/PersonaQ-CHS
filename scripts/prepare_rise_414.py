import hashlib,re,unicodedata
from collections import Counter,defaultdict
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING

TEXT={
0:['糟了，ＦＯＥ！？快逃！','遇到ＦＯＥ了！\n这家伙太危险了！快逃！','快、快逃！\n这家伙绝对不行！'],1:['不行，这家伙太危险了！\n快逃啊！'],2:['这家伙也不是打不赢吧！','现在能赢吧……要上吗？','虽说是ＦＯＥ，\n但这家伙应该能赢吧？'],
3:['敌人１名！被抢先了！'],4:['敌人２名……啊，敌人先制！'],5:['小心！\n敌人攻过来了！３名！'],6:['敌人４名！攻过来了！'],7:['被５名敌人抢先！撑住！'],8:['敌人先制攻击！足足６名！'],9:['哇，敌人好多！攻过来了！'],
10:['啊，稀有敌人攻过来了！','稀有敌人先制！\n把它打回去！','敌人抢先了！\n……咦，是稀有敌人！'],11:['啊，那个是稀有敌人！','稀有敌人！一定要打倒！','稀有敌人来啦！\n可不能放跑它！','别放跑了，那是稀有敌人！','啊，稀有敌人！好机会！'],
12:['敌人１名！没有它的资料！','敌方暗影１名！别大意！'],13:['敌人２名！有没资料的家伙！','敌人２名！'],14:['暗影３名！\n有还没资料的家伙！','敌人３名，加油！'],15:['敌方暗影４名！\n有没资料的家伙！','敌人４名！加油！'],16:['哇，敌人５名！\n有没资料的家伙！','哇，敌人５名！\n数量多，要小心！'],17:['哇，敌人６名！\n有没资料的家伙！','哇，敌方暗影６名！好多！'],18:['敌人太多了！\n好像还有没资料的家伙！','敌人太多了！鼓起干劲撑过去！'],
19:['这家伙看着很强！小心！','只有１名但很强，要小心！'],20:['强敌２名！\n有没资料的家伙，要小心！','敌人２名！很强，要小心！'],21:['强敌３名！\n还有没资料的家伙！','敌人３名，都是强敌，小心！'],22:['强敌４名！\n好像还有没资料的家伙！','敌方暗影４名，都是强敌！'],23:['敌人５名！很强！\n还有没资料的家伙！','敌人５名！很危险！'],24:['不会吧……强敌６名！\n还有不认识的！','不会吧……\n敌人６名！很危险！'],25:['什么啊……好多强敌，\n还有没资料的家伙！','糟了，糟了！好多强敌！'],
26:['虽没资料，但应该轻松就能赢。','这种敌人，轻松就能赢吧！'],27:['敌人２名……还有没资料的\n家伙呢。不过看着不强……','虽有２名，但很容易对付吧！'],28:['敌人３名，还有不认识的。\n看着都不强！','虽有３名，但没什么可怕的吧！'],29:['敌人４名。虽有没资料的\n家伙，但似乎都不危险。','这４名都有资料，\n应该没问题吧！'],30:['虽然不强，但有５名。\n还有没资料的，要小心！','虽然不强，但数量多！\n要小心！'],31:['哇……足足６名……\n还有没资料的家伙。','哇……足足６名……虽然不强，\n也不能大意哦？'],32:['敌人好多！还有不认识的，\n可别大意！','哇，好多弱敌！\n还是小心点哦！'],
33:['敌人１名！我们抢先了！'],34:['敌人２名！现在可以抢先出手！'],35:['敌人３名！先下手为强！'],36:['敌人４名！我们可以先出手！'],37:['先制攻击的机会！敌人５名！'],38:['敌人６名！\n虽多，但我们先出手！'],39:['虽多，但我们先出手！\n加油！'],40:['虽然是强敌，但我们先出手！'],41:['强敌２名！我们能先出手！'],42:['强敌３名！\n虽是先制……怎么办？'],43:['强敌４名！\n现在还能逃？怎么办？'],44:['强敌５名！好多！\n要不趁现在撤退？'],45:['强敌足足６名……\n要逃就趁现在！'],46:['好多强敌！\n即使先制也该撤退！'],
47:['来啦！送上门的肥羊！','对稀有敌人先制，好走运！','哇，抢在稀有敌人前出手了！\n好机会！'],48:['糟了，ＦＯＥ来了！','咦，还能这样！？\nＦＯＥ闯进来了！','ＦＯＥ来了！小心！'],49:['虽说是增援……\n这个ＦＯＥ应该没问题吧。'],50:['什么！又是ＦＯＥ！？','真不敢信，又是ＦＯＥ！？'],
52:['狂欢模式好厉害！\n埃癸斯的攻击力大幅提高了！','埃癸斯正处于狂欢模式！\n尽情进攻吧！'],53:['埃癸斯过热了！\n暂时动不了了！','埃癸斯冷却完成之前，\n都无法行动。']}

def main():
    TEXT[24][0]='不会吧…强敌６名！\n还有不认识的！'
    TEXT[26][1]='这种敌人，轻松能赢吧！'
    path=ROOT/'translation/batches/414_base_navigation.generated.json';assert not path.exists()
    catalog=read(ROOT/'translation/catalog.working.json');bank=defaultdict(list)
    for r in catalog:
        if r.get('translation'):bank[r['original']].append(r)
    sources=defaultdict(list);audit=[];fresh=0
    for r in catalog:
        if r.get('translation') or not r['source'].startswith('export_base/battle/support/'):continue
        old=r['original'];matches=bank[old];body=None
        if len({m['translation'] for m in matches})==1:
            ref=matches[0];body=TRAILING.sub('',LEADING.sub('',ref['translation']))
            audit.append(dict(target_key=r['key'],reference_key=ref['key'],original=old,translation=ref['translation']))
        elif r['source'].startswith('export_base/battle/support/bsv105.'):
            group=int(re.search(r'_\((\d+)\)',r['source'])[1])
            if group in TEXT:
                assert r['line_index']==0
                body=TEXT[group][r['message_index']]+'\n';fresh+=1
        if body is None:continue
        full=LEADING.match(old).group()+body+TRAILING.search(old).group()
        assert TOKEN.findall(full)==TOKEN.findall(old),r['key']
        a=TOKEN.sub('',old).splitlines();b=TOKEN.sub('',full).splitlines()
        assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),(r['key'],a,b)
        nums=lambda t:Counter(re.findall(r'\d+',unicodedata.normalize('NFKC',TOKEN.sub('',t))))
        assert nums(old)==nums(full),r['key']
        i=r['message_index'];j=r['line_index'];mid=read(ROOT/r['source'])['texts'][i]['id']
        sources[r['source']].append([i,j,mid,body])
    write(path,dict(status='draft',sources=dict(sources),source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},reuse_audit=audit,review_notes=['本体bsv105遭遇/先制/F.O.E/狂欢模式提示；本体导航完全相同原文及控制码的已有译稿直接复用。','复用来源记录到每条目录键；不声称本轮新增译文来自Q2。未运行验证。']))
    print('New translations:',fresh,'Exact reuse:',len(audit),'Total:',sum(map(len,sources.values())))

if __name__=='__main__':main()
