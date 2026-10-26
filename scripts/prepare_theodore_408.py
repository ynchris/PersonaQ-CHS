"""Theodore first four status groups."""
import hashlib
from collections import defaultdict
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING
from prepare_margaret_393 import IDS
TEXT={
54:['怎么会！\n副队长大人无法战斗了！','啊，副队长大人\n倒下了！','花村大人无法战斗了！！\n真是……令人失望……','啊……里中大人无法战斗了！\n我方战力下降了！','天城大人无法战斗了。\n哪位能帮忙恢复吗？','啊！巽大人无法战斗了！\n这可不行……','不好！\n白钟大人无法战斗了！','小熊大人无法战斗了。\n哪位能帮忙治疗吗？','岳羽大人无法战斗了！\n请哪位帮忙恢复！','啊！伊织大人倒下了！\n已经瘫软无力了！','怎么会……真田大人\n被击倒了！！','不好！\n桐条大人无法战斗了！','不好……\n埃癸斯大人无法战斗了！','天田大人无法战斗了！\n请问哪位能够帮忙恢复？','怎么会……\n虎狼丸大人无法战斗了！','荒垣大人无法战斗了！\n似乎站不起来了！','善大人，玲大人！！\n两位都无法战斗了！','啊！善大人无法战斗了。\n需要恢复！','啊！队长大人无法战斗了！\n哪、哪位能帮忙恢复！','不好！队长大人无法战斗了！\n请求救援！'],
55:['副队长大人，以这点体力\n继续战斗很危险。','副队长大人的体力所剩无几。\n还请安排恢复！','花村大人的体力所剩无几！\n当务之急应是先行恢复！','里中大人的伤势很严重。\n还请多加照应。','天城大人的体力所剩无几！\n请尽快安排恢复！','巽大人……以这点体力战斗，\n未免太过勉强！','白钟大人的体力已十分危险。\n啊……敌人正盯着她！','小熊大人的体力所剩无几。\n请小心！','岳羽大人的体力所剩无几。\n恐怕需要立即恢复！','伊织大人，以这点体力战斗\n实在勉强……请爱惜自己！','即使是真田大人，\n以这点体力战斗也太鲁莽了！','桐条大人的伤势很严重。\n请立即恢复！','埃癸斯大人的伤势，\n已经严重到不能忽视了！','天田大人，您还好吗？\n伤势似乎很严重……','请替虎狼丸大人恢复。\n实在可怜得让人不忍直视。','请留意荒垣大人的体力。\n已经减少很多了！','善大人和玲大人的体力告急。\n请帮助他们。','善大人的伤势很严重。\n请优先替他恢复。','队长大人，您受伤太重了吧……\n建议立即恢复。','队长大人！体力所剩无几。\n请小心！'],
56:['副队长大人变成石头了！\n还高举着拳头！！','不好，副队长大人，\n变得像石像一样……','啊，花村大人……即使成为石像，\n那股令人失望的气息也没消失呢……','里中大人变成石像了！\n……那是……白鹤架势！？','天城大人……摆着舞姿变成石头……\n……莫非有什么讲究吗……','巽大人的石像……\n这姿态……简直能用来辟邪！！','啊！白钟大人成了石化王子！\n啊……不……失礼了……','石化后的小熊大人，\n怎么看都像是什么地方的摆件……','啊……岳羽大人变成石头了……\n硬邦邦的……','啊……伊织大人变成石头了！\n嗯……倒是安静下来了……','啊……真田大人……\n保持着战斗姿势变成石头了……','怎么会！桐条大人成了石像！\n……不过，这样也很美丽……','埃癸斯大人变成石头了！\n虽、虽然她本来就很坚硬……','天田大人被石化了！\n防御力似乎提高了，不过……','啊！虎狼丸大人成了石像！\n可爱得真想摆在房间里……','话说回来，荒垣大人即使变成石头，\n也依然很有魄力呢。','善大人和玲大人变成石头了！\n连石化都是两位一起！','啊！善大人变成石头了！\n面无表情变得更面无表情了！！','怎么会这样……\n队长大人变成石头了……','啊！队长大人！\n简直像石像一样……'],
57:['副队长大人，您中毒了！\n必须赶快解毒！','副队长大人似乎中毒了。\n请问哪位能够解毒？','花村大人中毒了。\n不尽快解毒，之后可有苦头吃……','里中大人中毒了！\n尽快解毒才是上策！','天城大人中毒了。\n应当尽早解毒，刻不容缓！','巽大人中毒了。\n看那脸色便一目了然！','白钟大人中毒了。\n来，快点解毒！','小熊大人中毒了！\n各位有解毒的手段吗？','岳羽大人，您中毒了吗？\n脸色都变紫了！','伊织大人中毒了。\n不赶快解毒，之后可有苦头吃……','真田大人似乎中毒了。\n必须赶快解毒！','啊……桐条大人的脸色发紫……\n这也是毒的缘故吗……','埃癸斯大人中毒了。\n可以替她解毒吗？','天田大人中毒了。\n请立即安排解毒！','怎么会这样……\n虎狼丸大人中毒了！','荒垣大人中毒了！\n请问哪位能够解毒？','善大人和玲大人中毒了！\n两位的脸色都变紫了！','善大人中毒了！\n迅速解毒才是团队和睦的秘诀！','啊……队长大人的脸色发紫……\n请赶快解毒！','啊，队长大人中毒了……\n请立即解毒！']}

def main():
    TEXT[56][IDS.index(9)]='啊…岳羽大人石化了…\n硬邦邦的……'
    TEXT[56][IDS.index(19)]='啊！善大人变成石头了！\n更面无表情了！！'
    TEXT[56][IDS.index(20)]='怎么会这样……\n队长大人石化了……'
    path=ROOT/'translation/batches/408_theodore_statuses_a.generated.json';assert not path.exists()
    rows=read(ROOT/'translation/catalog.working.json');catalog={r['key']:r for r in rows};index=defaultdict(list)
    for r in rows:
        if r.get('translation') and '/battle/support/' in r['source']:index[r['original']].append(r)
    sources=defaultdict(list);audit=[]
    for m,values in TEXT.items():
        assert len(values)==20
        source=f'export_dlc/0005/battle/support/bsv123.bvp_({m:03}).BMD.json';doc=read(ROOT/source)
        for i,body in zip(IDS,values):
            row=catalog[f'{source}:{i}:0'];assert not row.get('translation');body+='\n'
            refs=index.get(row['original'],[])
            if refs and len({r['translation'] for r in refs})==1:
                body=TRAILING.sub('',LEADING.sub('',refs[0]['translation']));audit.append({'key':row['key'],'reference':refs[0]['key']})
            a=TOKEN.sub('',row['original']).splitlines();b=body.splitlines()
            assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),(m,i,max(map(len,b)),max(map(len,a)))
            sources[source].append([i,0,doc['texts'][i]['id'],body])
    write(path,dict(status='draft',sources=dict(sources),source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},reuse_audit=audit,review_notes=['西奥多054—057有效80页；保留敬称、石化调侃和状态含义。','占位不改，石化提升防御等仅按原文翻译，不代表运行确认；未运行验证。']))
    print('Pages:',sum(map(len,sources.values())),'exact reuse:',len(audit))

if __name__=='__main__':main()
