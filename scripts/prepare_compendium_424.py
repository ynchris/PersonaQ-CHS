import hashlib,re
from collections import defaultdict
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING
NEW={
(113,2):'持有这个，\n从人格面具全书中召唤的费用，\n就可以享受折扣。\n',
(115,0):'今后，当您创造出更多\n人格面具时，我仍会……\n',
(116,1):'那么，就按约定，\n由我送上一份礼物。\n',
(118,0):'持有这个，\n从人格面具全书中召唤的费用，\n就可以享受更多折扣。\n',
(119,2):'哎呀……\n差点忘了。\n这个送给你。\n',
(121,0):'人格面具全书就快完成了……\n希望这个能助你一臂之力。\n',
(122,2):'为赞赏你的努力，\n我将送上最好的礼物。\n',
(124,0):'持有这个，\n人格面具全书使用起来\n应该会更加方便。\n',
(125,2):'持有这个，\n从人格面具全书中召唤的费用，\n就可以享受折扣。\n',
(127,0):'今后，当您创造出更多\n人格面具时，我仍会……\n',
(128,1):'那么，就按照约定，\n为您送上一份礼物吧。\n',
(130,0):'持有这个，\n从人格面具全书中召唤的费用，\n就可以享受更多折扣。\n',
(131,2):'那么，就按照约定，\n请您收下这个。\n',
(133,0):'人格面具全书就快完成了……\n请务必善加利用\n这份礼物。\n',
(134,3):'那么，请收下这个。\n这是我为您准备的最好的礼物。\n',
(136,0):'持有这个，\n人格面具全书使用起来\n应该会更加方便。\n'}

def main():
    target=ROOT/'translation/batches/424_compendium_rewards.generated.json';assert not target.exists()
    catalog=read(ROOT/'translation/catalog.working.json');bank=defaultdict(list)
    for r in catalog:
        if r.get('translation'):bank[r['original']].append(r)
    s='export_base/facility/cmbtalk.bf.json';doc=read(ROOT/s);rows=[];audit=[]
    for r in catalog:
        i=r['message_index'];j=r['line_index']
        if r['source']!=s or not 113<=i<=136:continue
        assert not r.get('translation');old=r['original'];refs=bank[old]
        if len({x['translation'] for x in refs})==1:
            body=TRAILING.sub('',LEADING.sub('',refs[0]['translation']))
            audit.append(dict(target_key=r['key'],reference_key=refs[0]['key'],original=old,translation=refs[0]['translation']))
        elif (i,j) in NEW:body=NEW[i,j]
        elif 'を手に入れた！' in old:
            full=old.replace('＞','＞获得了').replace('を手に入れた！','！')
            body=TRAILING.sub('',LEADING.sub('',full))
        else:
            match=re.search(r'([０-９]+)％',old);assert match,r['key']
            body='＞从全书中召唤的费用\n　现在可减免'+match[1]+'％！\n'
        full=LEADING.match(old).group()+body+TRAILING.search(old).group()
        assert TOKEN.findall(old)==TOKEN.findall(full),r['key']
        a=TOKEN.sub('',old).splitlines();b=TOKEN.sub('',full).splitlines()
        assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),(i,j,a,b)
        rows.append([i,j,doc['texts'][i]['id'],body])
    write(target,dict(status='draft',sources={s:rows},source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest()},reuse_audit=audit,review_notes=['补齐cmbtalk的113—136两套全书奖励流程，精确原文/控制码相同且译文唯一者直接复用并记录出处。','折扣按原文减免百分比译，不改成对应折数，保留动态道具名。未运行验证。']))
    print('Compendium reward pages:',len(rows),'exact reused:',len(audit))

if __name__=='__main__':main()
