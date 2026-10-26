"""Freeze the manually reviewed numeric warnings and five precise corrections."""
import hashlib
from compile_translation import ROOT, read, write, TOKEN


def main():
    target=ROOT/'translation/text_corrections.review.json'
    audit=ROOT/'translation/numeric_review_451.json'
    assert not target.exists() and not audit.exists(), 'Never refresh reviewed snapshots implicitly'
    catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')}
    changes={
        'export_base/event/e800/e823_610.bf.json:7:2':('平假名不属于同一类','１个平假名不属于同一类'),
        'export_base/event/e800/e823_620.bf.json:5:2':('平假名不属于同一类','１个平假名不属于同一类'),
        'export_base/event/e800/e823_630.bf.json:5:2':('平假名不属于同一类','１个平假名不属于同一类'),
        'export_base/event/e800/e823_640.bf.json:0:3':('“とー（too）”“けー（kee）”“いー（ii）”……','“とー（too）”、\n“けー（kee）”、“いー（ii）”……'),
        'export_base/event/e800/e823_640.bf.json:4:3':('就是“とー（too）”“けー（kee）”“いー（ii）”……','就是“とー（too）”、\n“けー（kee）”、“いー（ii）”……'),
    }
    rows=[]
    for key,(old,new) in changes.items():
        r=catalog[key];before=r['translation'];assert before.count(old)==1
        after=before.replace(old,new)
        assert TOKEN.findall(before)==TOKEN.findall(after)
        rows.append(dict(key=key,original=r['original'],before=before,after=after,
                         reason='恢复原文一个假名的数量限定' if '１个' in new else '将读音列表分行，保留全部谜题读音与控制码；需实测文本框'))
    special={
        'export_base/event/e200/e210_506.bf.json:9:1':'日文36度8分与中文36.8度数值等价',
        'export_base/event/e800/e803_220.bf.json:16:0':'4択改为4选1，增加的1是题型语义而非改题数',
        'export_base/event/e700/e724_240.bf.json:6:1':'1歩ずつ改为1步1步，重复数词表达逐步前进',
        'export_base/event/e700/e724_400.bf.json:5:1':'1区画に1つ改为每个区域各1座，4座总数不变',
    }
    reviewed=[]
    warnings=[w for w in read(ROOT/'translation/progress.generated.json')['warnings'] if w['kind']=='numeric_review']
    assert len(warnings)==236
    for w in warnings:
        key=w['key'];r=catalog[key]
        reason=special.get(key,'已逐条对照；中文数词、量词、序数或习惯表达保留原数量含义（含百分数和分数）')
        disposition='reviewed_equivalent'
        if key in changes:
            reason='原译省略一个假名的限定，已提交精确纠正';disposition='correction_pending_compile'
        reviewed.append(dict(key=key,original=r['original'],translation=r['translation'],
                             translation_sha256=hashlib.sha256(r['translation'].encode('utf-8')).hexdigest(),
                             disposition=disposition,reason=reason))
    write(target,dict(rows=rows,status='reviewed_corrections_runtime_untested'))
    write(audit,dict(rows=reviewed,reviewed_count=236,compiler_warnings_preserved=True,
                    note='Snapshot review only; changed translations invalidate approval. No runtime or layout approval implied.'))
    print('Frozen 236 numeric reviews and 5 exact text corrections.')


if __name__=='__main__':main()
