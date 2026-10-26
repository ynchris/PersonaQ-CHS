"""Quest helper messages with dynamic item and color controls preserved."""
import hashlib,re
from collections import defaultdict
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING
REPLACE={
'“スキルカード”':'“技能卡”',
'は、\n使用する事で“メイン”のペルソナに\nスキルを覚えさせる事ができるアイテムです。':'是能让“主人格面具”\n学会技能的道具。\n使用后即可习得技能。',
'＞手放してしまわない内に\n　報告しておいた方が良さそうだ…':'＞趁还没把它交出去，\n　先去报告比较好……',
'アイテムを整理して、\n再度報告を行ってください。':'请整理道具后，\n再次前来报告。',
'お渡しした':'先前交给您的',
'は\nこちらで預からせていただきます。':'，\n就由我们收回保管。',
'＞そう言えば、依頼にあった\n　':'＞说起来，已取得委托要求的\n　',
'を入手している…':'……',
'＞向こう側から押さえられているのか\n　扉は開かない…':'＞难道被从另一边抵住了？\n　门打不开……',
'＞今はＦ．Ｏ．Ｅの正体を確かめよう…':'＞现在先查明Ｆ．Ｏ．Ｅ的真面目吧……'}

def main():
    target=ROOT/'translation/batches/412_quest_helpers.generated.json';assert not target.exists()
    sources=defaultdict(list)
    for r in read(ROOT/'translation/catalog.working.json'):
        if r.get('translation') or not r['source'].startswith('export_base/quest/'):continue
        q=int(re.search(r'quest_(\d+)',r['source'])[1])
        if q>47 or any(x in r['original'] for x in ('テスト','仮','クエスト４','破棄')):continue
        full=r['original']
        for old,new in REPLACE.items():full=full.replace(old,new)
        assert full!=r['original'],r['key']
        assert TOKEN.findall(full)==TOKEN.findall(r['original']),r['key']
        body=TRAILING.sub('',LEADING.sub('',full))
        assert LEADING.match(r['original']).group()+body+TRAILING.search(r['original']).group()==full
        a=TOKEN.sub('',r['original']).splitlines();b=TOKEN.sub('',full).splitlines()
        assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),r['key']
        doc=read(ROOT/r['source']);i=r['message_index'];j=r['line_index'];sources[r['source']].append([i,j,doc['texts'][i]['id'],body])
    total=sum(map(len,sources.values()));assert total==25,total
    write(target,dict(status='draft',sources=dict(sources),source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},review_notes=['25页委托帮助与交还/报告提醒；重复句按同一译文生成。','保留动态道具名和高亮控制码，排除测试/仮文本和48/49预留委托。未运行验证。']))
    print('Quest helper pages:',total)

if __name__=='__main__':main()
