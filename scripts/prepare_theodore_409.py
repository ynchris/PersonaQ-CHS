"""Theodore sleep, paralysis and curse warnings."""
import hashlib
from collections import defaultdict
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING
from prepare_margaret_393 import IDS
TEXT={
58:['啊！副队长大人，请醒醒！\n现在受到攻击会很危险！','怎么会……副队长大人竟在小睡……\n敌人可就在眼前啊！','花村大人，请快醒醒！\n哪、哪位能狠狠扇他一巴掌！','里中大人睡得正香！\n连梦话都说起来了！','天城大人，请醒醒！\n敌人就在眼前啊！','巽大人！现在可不是\n说梦话的时候……敌人就在眼前！','不好！白钟大人睡着了！\n现在被盯上会受到重创！','小熊大人……这样下去，\n会被敌人打醒的！','岳羽大人，请醒醒！\n淑女怎能睡在那种地方……','伊织大人……您睡着了吗？\n请哪位赏他一巴掌！','面对敌人还能如此熟睡……\n……真田大人果然不同凡响。','不、不愧是桐条大人……\n竟然站着睡着了……','埃癸斯大人……您睡着了吗？\n……原来您也会睡觉吗？','不好！天田大人睡着了！\n现在被盯上会受到重创！','虎、虎狼丸大人，怎能轻易睡着，\n这有损地狱看门犬刻耳柏洛斯之名！','啊，荒垣大人睡着了！\n不快叫醒他，敌人的攻击就……','善大人，玲大人，请醒醒！\n敌人要过来了！','啊，不好！善大人，请醒醒！\n这一觉会要了您的命！','不行，队长大人！\n别输给困意，快醒醒！','队、队长大人，竟在敌前打鼾，\n未免太过大胆了！'],
59:['副队长大人麻痹了。\n这……也许会无法行动。','副队长大人麻痹了。\n事已至此，只能祈祷还能行动！','花村大人麻痹了。\n也许会因无法行动而大失所望……','里中大人麻痹了。\n若无法行动，该怎么办呢……','天城大人麻痹了，\n似乎无法自如行动！','巽大人麻痹了。\n这……不知能否行动……','白钟大人麻痹了。\n也许会无法行动。','小熊大人麻痹了。\n恐怕不能期待他的表现了！','岳羽大人麻痹了。\n这……不知能否行动……','伊织大人的麻痹似乎还没解除。\n这……也许会无法行动……','真田大人麻痹了。\n能否行动……实在难以判断。','桐条大人麻痹了。\n不知能否正常行动……','不好，埃癸斯大人麻痹了。\n不知能否行动……','天田大人麻痹了。\n恐怕也有无法行动的可能。','虎狼丸大人似乎麻痹了。\n也许会无法行动……','荒垣大人麻痹了。\n也请考虑无法行动的情况。','善大人和玲大人麻痹了。\n也许会无法行动……','善大人麻痹了。\n也请考虑无法行动的情况。','队长大人麻痹了。\n这也许会导致无法行动。','队长大人的麻痹还没解除呢……\n行动可能会受到影响。'],
60:['副队长大人被诅咒了……\n现在攻击敌人很危险！','副队长大人被诅咒了！\n若发动攻击，自身恐怕也会受伤。','花村大人被诅咒了。\n现在攻击，会落得失望的结果！','里中大人，请暂缓攻击。\n您被诅咒了。','天城大人被诅咒了。\n不如暂缓攻击？','巽大人被诅咒了……\n对好战的您而言，真是最糟的状况。','白钟大人，您被诅咒了。\n发动攻击，自身也会受伤。','小熊大人被诅咒了。\n……明明不像会被诅咒的人……','岳羽大人被诅咒了……\n不建议现在发动攻击。','伊织大人被诅咒了。\n明明看起来不像会被诅咒的人……','真田大人，您现在被诅咒了！\n恐怕应当避免好战的行动……','桐条大人被诅咒了……\n现在攻击，自身也会受伤……','埃癸斯大人被诅咒了！\n……原来诅咒对您也有效呢……','天田大人被诅咒了。\n恐怕暂缓攻击才稳妥……','虎狼丸大人被诅咒了……\n还请暂缓攻击。','荒垣大人，您现在被诅咒了。\n攻击敌人恐怕很危险！','善大人和玲大人被诅咒了……\n尤其是善大人，请暂缓攻击。','善大人，您现在被诅咒了。\n不建议攻击敌人。','队长大人被诅咒了……\n现在攻击，自身也会受伤……','队长大人，您被诅咒了。\n现在攻击，自身也会受到伤害……']}

def main():
    TEXT[58][IDS.index(16)]='虎、虎狼丸大人，怎能轻易睡着，\n这有损地狱看门犬克鲁贝洛斯之名！'
    TEXT[58][IDS.index(6)]='巽大人！现在可不是\n说梦话的时候…敌人就在眼前！'
    TEXT[58][IDS.index(11)]='面对敌人还能如此熟睡……\n…真田大人果然不同凡响。'
    path=ROOT/'translation/batches/409_theodore_statuses_b.generated.json';assert not path.exists()
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
    write(path,dict(status='draft',sources=dict(sources),source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},reuse_audit=audit,review_notes=['西奥多058—060有效60页，保留敬称和独有调侃。','诅咒为主动攻击伤及自身；麻痹保留可能性，睡眠受击风险不反译；运行未验证。']))
    print('Pages:',sum(map(len,sources.values())),'exact reuse:',len(audit))

if __name__=='__main__':main()
