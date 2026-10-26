"""Human-translated rose poem, across four readings with distinct cue positions.

Only changed Japanese pages enter the batch. English refrain and blank timing
pages stay byte-identical and are not counted as newly translated messages.
"""
import hashlib
import re
from compile_translation import ROOT, read, write, TOKEN, LEADING, TRAILING

SOURCE = 'export_base/event/msg_POEM.bmd.json'
SHA256 = '5c7b3bcadcda2e57a908f688c4181164055385023c0f0baef61caba6d9f466ec'
PHRASES = {
    '「闇と': '「黑暗与', '「闇と薔薇」': '「黑暗与蔷薇」',
    'アタシは': '我要', 'アタシはひとり': '我要独自',
    'アタシは薔薇': '我是蔷薇',
    'アタシは闇に狂い咲く': '我在黑暗中狂放盛开',
    'アンタが流した血を吸って': '吸吮你流下的鲜血',
    'さあ': '来吧', 'さあどうぞ': '就请来吧', 'どうぞ': '尽管来吧',
    'ひとり': '独自', '一輪の薔薇': '一朵蔷薇',
    '最後の花弁が': '直到最后的花瓣',
    '刺し貫いてあげるから': '将你刺穿',
    '咲いてみせるわ': '绽放给你看',
    '哀しき': '悲伤的', '哀しき薔薇': '悲伤的蔷薇',
    '幾多の棘で': '我会用无数尖刺',
    '幾多の棘で　刺し貫いてあげるから': '我会用无数尖刺　将你刺穿',
    '摘みとりたいなら': '若想将我摘下',
    '摘みとりたいなら　さあどうぞ': '若想将我摘下　就请来吧',
    '深紅に咲き誇る': '盛放着深红的',
    '深紅に咲き誇る　哀しき薔薇': '盛放着深红的　悲伤的蔷薇',
    '燃え尽きる刻まで': '燃烧殆尽的时刻',
    '白い花弁を血で染めて': '以鲜血染红洁白的花瓣',
    '荒野に咲いた': '盛开在荒野中的',
    '薔薇': '蔷薇', '薔薇」': '蔷薇」',
}

def main():
    assert hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest() == SHA256
    doc = read(ROOT / SOURCE)
    rows, seen = [], set()
    for mi in range(12):
        msg = doc['texts'][mi]
        assert msg['id'] == f'MSG_CMM_POEM_{mi // 3:02d}_{mi % 3:02d}'
        for li, original in enumerate(msg['lines']):
            body = TRAILING.sub('', LEADING.sub('', original))
            pieces = re.split(r'(\{[0-9A-F ]+\}|\n)', body)
            for i, piece in enumerate(pieces):
                if TOKEN.fullmatch(piece):
                    continue
                core = piece.strip()
                if core in PHRASES:
                    seen.add(core)
                    pieces[i] = piece.replace(core, PHRASES[core], 1)
                elif re.search(r'[\u3041-\u3096\u30a1-\u30fa\u3400-\u9fff]', core):
                    raise ValueError(f'Unreviewed poem fragment: {core!r}')
            translated = ''.join(pieces)
            assert TOKEN.findall(body) == TOKEN.findall(translated)
            assert body.count('\n') == translated.count('\n')
            if translated != body:
                rows.append([mi, li, msg['id'], translated])
    assert seen == set(PHRASES), set(PHRASES) - seen
    assert len(rows) == 24
    write(ROOT / 'translation/batches/071_rose_poem.generated.json', {
        'status': 'draft', 'source_sha256': SHA256,
        'sources': {SOURCE: rows}, 'speakers': {},
        'notes': 'Four readings: cue order, blank lines and English refrain preserved. Other poems are untranslated.'
    })
    print('Compiled 24 translated rose-poem pages; English/blank pages excluded.')

if __name__ == '__main__':
    main()
