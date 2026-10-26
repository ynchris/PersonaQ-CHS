"""Fuuka encounter navigation plus safe exact-original reuse."""
import hashlib,re,unicodedata
from collections import Counter,defaultdict
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING
TEXT={
0:['危、危险！\n请设法撤退！','是ＦＯＥ！请立即撤退！','啊！是ＦＯＥ！快逃！'],1:['这个敌人……请、请快逃！\n总之先逃吧！'],2:['虽然是ＦＯＥ，\n但也并非无法战胜……','现在一定能赢……\n请加油！','这个ＦＯＥ也许能赢……'],
3:['敌人１名！敌方先制攻击！'],4:['敌人２名！对方先攻过来了！'],5:['敌方发动攻击！３名！'],6:['敌人４名！敌方先制！'],7:['被５名敌人抢先，请小心！'],8:['敌人６名发动先制攻击！'],9:['大批敌人先制攻击！\n请撑住！'],10:['啊，是稀有敌人！\n对方先攻过来了！','敌方先制！\n啊，是稀有敌人！','稀有敌人主动攻过来了！\n把它打回去吧！'],11:['啊，是稀有敌人！','有稀有敌人！','那个敌人很稀有！','有稀有敌人！请务必讨伐！','啊！那个敌人很稀有！'],
12:['敌人１名，是资料中没有的类型！','敌方暗影１名！'],13:['敌人２名！有资料中没有的敌人！','敌方暗影２名！'],14:['敌方暗影３名。\n有资料中没有的敌人！','暗影３名！'],15:['敌方暗影４名。\n有资料中没有的敌人！','敌人４名！请小心！'],16:['敌人５名！有资料中没有的敌人！','敌方暗影５名！数量很多！'],17:['敌人６名！有资料中没有的敌人！','敌人６名！数量很多！'],18:['敌方暗影众多！\n有资料中没有的类型！','敌人众多！请小心！'],19:['敌人１名。看起来很强，\n请小心！','敌人１名。是强敌，请小心！'],20:['强敌２名！有资料中没有的敌人！','敌方暗影２名！是强敌！'],21:['强敌３名！还有没资料的敌人！','敌人３名！是强力类型！'],22:['强敌４名！\n其中有资料中没有的敌人！','敌人４名！是强敌，\n请不要勉强！'],23:['强敌５名！还有没资料的敌人！','敌人５名！全都是强敌！'],24:['怎么会……强敌６名！\n资料里也没有！','敌人６名，是强敌！'],25:['敌人众多！怎么会……\n是强敌，资料里也没有！','好……好多强敌！太危险了！'],
26:['敌人１名。是资料里没有的敌人。','敌人１名。稳妥地击倒它吧！'],27:['敌人２名。虽有没资料的敌人，\n但应该不太危险。','敌人２名。这下很轻松呢。'],28:['敌人３名。虽有没资料的敌人，\n但应该能轻松获胜。','敌人３名。\n威胁程度应该较低。'],29:['包括未登记的敌人在内，共４名。\n看起来不强。','敌人４名，但威胁程度较低。'],30:['敌人５名。还有没资料的敌人。\n请不要大意！','虽然各自不强，但有５名。\n请小心！'],31:['敌人６名……战力看似较低，但也有\n没资料的敌人。请小心！','敌人虽不强，但有６名！\n请小心！'],32:['敌人众多。还有没资料的敌人。\n请小心。','虽然各自战力较低，\n但数量众多！请注意！'],
33:['敌人１名！我方先制！'],34:['敌人２名！我方先制攻击！'],35:['敌人３名！我方先制攻击！'],36:['敌人４名！先下手为强吧！'],37:['敌人５名！\n我方可以先发动攻击！'],38:['敌人６名！先制攻击！'],39:['敌人众多！我方先出手！'],40:['虽然是强敌，但我方先制。\n请小心！'],41:['虽然有２名强敌，但我方先制！'],42:['强敌３名！虽然是先制，\n但请不要勉强！'],43:['强敌４名！现在也可以逃走！'],44:['敌人５名。是强敌！\n要不要趁现在撤退！'],45:['强敌６名！撤退就趁现在！'],46:['强敌众多！\n建议趁先制立即撤退！'],47:['啊，稀有敌人！\n先制的现在正是机会！','我方抢先了！\n敌人是稀有类型！','我方先制！敌人是稀有类型！'],48:['ＦＯＥ来袭！请小心！','不好了！ＦＯＥ来了！','ＦＯＥ闯入！敌方战力上升！'],49:['虽然ＦＯＥ闯了进来，\n但这种程度应该没问题！'],50:['怎么会……又有ＦＯＥ来袭！','ＦＯＥ又来了！'],51:['ＦＯＥ就在附近。请注意！','附近有ＦＯＥ！','ＦＯＥ接近，请小心！'],52:['确认狂欢模式生效。\n埃癸斯的战斗力正在上升。','埃癸斯的狂欢模式持续中。\n攻击力提升。'],53:['埃癸斯过热了。\n暂时无法行动。','埃癸斯在冷却结束之前\n都无法行动。']}

def main():
    TEXT[29][0]='含未登记敌人在内，共４名。\n看起来不强。'
    target=ROOT/'translation/batches/419_fuuka_encounters.generated.json';assert not target.exists()
    catalog=read(ROOT/'translation/catalog.working.json');bank=defaultdict(list)
    for r in catalog:
        if r.get('translation'):bank[r['original']].append(r)
    sources=defaultdict(list);audit=[];fresh=0
    for r in catalog:
        if r.get('translation') or not r['source'].startswith('export_base/battle/support/bsv108.'):continue
        s=r['source'];m=int(re.search(r'_\((\d+)\)',s)[1]);i=r['message_index'];j=r['line_index'];old=r['original'];body=None
        refs=bank[old]
        if len({x['translation'] for x in refs})==1:
            body=TRAILING.sub('',LEADING.sub('',refs[0]['translation']));audit.append(dict(target_key=r['key'],reference_key=refs[0]['key'],original=old,translation=refs[0]['translation']))
        elif m in TEXT:
            assert j==0;body=TEXT[m][i]+'\n';fresh+=1
        if body is None:continue
        full=LEADING.match(old).group()+body+TRAILING.search(old).group()
        assert TOKEN.findall(full)==TOKEN.findall(old),r['key']
        a=TOKEN.sub('',old).splitlines();b=TOKEN.sub('',full).splitlines()
        assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),(m,i,a,b)
        nums=lambda t:Counter(re.findall(r'\d+',unicodedata.normalize('NFKC',TOKEN.sub('',t))))
        assert nums(old)==nums(full),r['key']
        sources[s].append([i,j,read(ROOT/s)['texts'][i]['id'],body])
    assert fresh==94 and len(audit)==1,(fresh,len(audit))
    write(target,dict(status='draft',sources=dict(sources),source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},reuse_audit=audit,review_notes=['风花000—053遭遇/先制/FOE/狂欢模式94页及1页精确原文控制码复用。','保持敌人数目、强弱与可能性、礼貌口吻；未运行验证。']))
    print('Fuuka encounters:',fresh,'exact reuse:',len(audit))

if __name__=='__main__':main()
