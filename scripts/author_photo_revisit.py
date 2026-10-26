"""Author the fixed two-page photo reinspection scenes; assert exact templates."""
import hashlib
from compile_translation import ROOT, read, write
from reuse_parallel_story import body

NAMES = [('順平','顺平'),('ゆかり','由加莉'),('真田','真田'),('荒垣','荒垣'),
 ('美鶴','美鹤'),('アイギス','埃癸斯'),('風花','风花'),('天田','天田'),('コロマル','虎狼丸'),
 ('{F5 C1 0E 01 01 01 01 01 01 01}','{F5 C1 0E 01 01 01 01 01 01 01}'),
 ('陽介','阳介'),('千枝','千枝'),('雪子','雪子'),('りせ','理世'),('完二','完二'),('直斗','直斗'),
 ('クマ','小熊'),('エリザベス','伊丽莎白'),('マーガレット','玛格丽特'),('テオ','迪奥'),('マリー','玛丽'),('善','善'),('玲','玲')]
scenes = {}
for n,(jp,zh) in enumerate(NAMES,601):
    code=f'e200_{n}'
    path=ROOT/f'export_base/event/e200/{code}.bf.json'
    doc=read(path)
    expected=[f'＞自分と{jp}が、\n　　二人きりで写っている…\n'.replace('　　','　'),'＞どうやら、これは\n　合成写真のようだ…\n']
    assert len(doc['texts'])==1 and [body(s) for s in doc['texts'][0]['lines']]==expected
    scenes[code]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                  'messages':{'0':[f'＞照片上只有自己和{zh}……\n','＞看来，这似乎是合成照片……\n']}}
write(ROOT/'translation/scene_bundles/photo_revisit.json',{'batch_prefix':'107_photo_revisit','scenes':scenes})
print('Authored 46 exact-template photo reinspection pages.')
