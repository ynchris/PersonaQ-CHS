import hashlib
from compile_translation import ROOT,read,write,LEADING,TRAILING
from prepare_sklcard_428 import replace_slots

TEXT={0:['是的','不需要'],1:['要修改留言，可以吗？\n'],2:['不修改留言，可以吗？\n'],
3:['那我说明一下“救援请求”吧。\n','那个，世界不只有这里，\n据说还有很多和这里相似的世界。\n','而且，那些世界也有“不是你的你”，\n虽然我也不太明白啦。\n','所以，在电视里遇到危险时，\n你可以向“别的世界”里的你，\n发送救援请求。\n','然后，如果“别的世界”里的你\n回应了请求，这个世界的你\n就能收到支援。\n','顺便说一下，发送救援请求\n不用花钱，不如试试看？\n','如果想知道更详细的说明，\n再问我，我就告诉你。\n'],
4:['将修改留言。\n可以吗？\n'],5:['留言不会修改，可以吗？\n'],
6:['明白了，下面就为您\n说明“救援请求”。\n','救援请求是将您的声音\n传达给“别的世界”的功能。\n','所谓“别的世界”，\n是与您此刻所在的世界平行存在的\n“另一个世界”……\n','您发出的救援请求会跨越世界的壁垒，\n传达给生活在众多“别的世界”中的\n“另一个您”。\n','救援请求无需付费，\n在电视里陷入危机时，请务必试试。\n','若您需要进一步的说明，\n请尽管告诉我，不必客气。\n'],
7:['要修改留言…可以吧。\n'],8:['不修改留言…可以吗？\n'],
9:['啊…我说明一下“救援请求”吧。\n','那个…世界不只有这里，\n还有很多和这里相似的世界。\n','那些世界也有“不是你的你”…\n像你一样，过着普通的生活。\n','所以，在电视里遇到危险时，\n你可以向“别的世界”里的你，\n发送救援请求…\n','然后…如果“别的世界”里的你\n回应了请求，这个世界的你\n就能收到支援…\n','…发送救援请求\n不用花钱，你先试试看吧。\n','如果想知道更详细的说明，\n再问我，我会告诉你的…\n']}

def main():
    s='export_base/facility/msg_usercmm.bmd.json';doc=read(ROOT/s)
    path=ROOT/'translation/batches/431_usercmm_tutorial.generated.json';assert not path.exists()
    catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')};rows=[]
    for i,lines in TEXT.items():
        assert len(lines)==len(doc['texts'][i]['lines'])
        for j,plain in enumerate(lines):
            r=catalog[f'{s}:{i}:{j}'];assert not r.get('translation');old=r['original']
            full=replace_slots(old,plain);prefix=LEADING.match(old).group();suffix=TRAILING.search(old).group()
            body=full[len(prefix):len(full)-len(suffix)]
            assert prefix+body+suffix==full
            rows.append([i,j,doc['texts'][i]['id'],body])
    write(path,dict(status='draft',sources={s:rows},source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest()},review_notes=['28页留言修改和三套救援请求说明整文件补译。保留逐字控制码和原有分页。','电视内救援明显属于旧作机制语境，仅补齐资源文本，不宣称PQ具有此功能或本段可达。']))
    print('User communication tutorial:',len(rows))

if __name__=='__main__':main()
