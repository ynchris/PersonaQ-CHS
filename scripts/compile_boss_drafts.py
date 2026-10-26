"""Compile indexed boss dialogue, keeping explicitly identified placeholders intact."""
import hashlib
import re
from compile_translation import ROOT, read, write, LEADING, TRAILING, TOKEN

PLACEHOLDERS = {
    'クロノス戦開始台詞\nありません\n', 'クロノス戦終了台詞\nありません\n',
    'リザーブ\n', '終了台詞\n', 'ドクター＆ナース戦開始台詞\nありません\n',
    'マーガレット戦\n開始台詞その４\n', 'マーガレット戦\n終了台詞\n',
    'エリザベス４連戦１戦目\n開始台詞その３\n',
    'エリザベス４連戦１戦目\n開始台詞その４\n',
    'エリザベス４連戦１戦目\n終了台詞\n',
    *{f'{n}ページ目\n牧師戦開始台詞はありません\n' for n in '１２３４'},
    *{f'エリザベス４連戦{stage}\n{suffix}\n'
      for stage in ['２戦目', '３戦目', '４戦目ゼウスＡ', '４戦目ゼウスＢ']
      for suffix in ['開始台詞その３', '開始台詞その４', '終了台詞']},
}

def compile_draft(draft):
    source = draft['source']
    assert re.fullmatch(r'export_base/battle/event/boss\d+\.bf\.json', source)
    path = ROOT / source
    assert hashlib.sha256(path.read_bytes()).hexdigest() == draft['sha256']
    doc = read(path)
    names = draft['speaker_names']
    assert set(doc['speakers']) == set(names)
    all_pages = {(i, j) for i, m in enumerate(doc['texts']) for j in range(len(m['lines']))}
    seen, rows = set(), []
    for i, j, text in draft['pages']:
        assert (i, j) in all_pages and (i, j) not in seen
        seen.add((i, j))
        original = TRAILING.sub('', LEADING.sub('', doc['texts'][i]['lines'][j]))
        assert text.strip() and TOKEN.findall(original) == TOKEN.findall(text)
        rows.append([i, j, doc['texts'][i]['id'], text])
    omitted = set()
    for i, j, expected in draft.get('excluded_placeholders', []):
        assert (i, j) in all_pages and (i, j) not in seen | omitted
        original = TRAILING.sub('', LEADING.sub('', doc['texts'][i]['lines'][j]))
        assert original == expected
        assert expected in PLACEHOLDERS
        omitted.add((i, j))
    assert seen | omitted == all_pages
    return {'status': 'draft', 'sources': {source: rows},
            'source_hashes': {source: draft['sha256']},
            'speakers': {source: [[i, jp, names[jp]] for i, jp in enumerate(doc['speakers']) if names[jp] != jp]}}


def main():
    pending = []
    for path in sorted((ROOT/'translation/boss_drafts').glob('*.json')):
        draft = read(path)
        assert re.fullmatch(r'\d+_[a-z0-9_]+\.generated\.json', draft['batch'])
        batch = compile_draft(draft)
        batch['authoring_source'] = str(path.relative_to(ROOT))
        pending.append((ROOT/'translation/batches'/draft['batch'], batch))
    for path, batch in pending:
        write(path, batch)
    print(f'Compiled {sum(len(v) for _, b in pending for v in b["sources"].values())} boss dialogue pages.')


if __name__ == '__main__':
    main()
