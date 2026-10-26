"""Expand reviewed scene bundles, sharing only exact authored repeated pages."""
import hashlib
from compile_translation import ROOT, read, write, LEADING, TRAILING, TOKEN

def main():
    names = {}
    for path in (ROOT/'translation/story').glob('*.json'):
        for jp, zh in read(path)['speaker_names'].items():
            if jp in names:
                assert names[jp] == zh, ('Ambiguous speaker', jp)
            names[jp] = zh
    total = 0
    for path in sorted((ROOT/'translation/scene_bundles').glob('*.json')):
        bundle = read(path)
        for jp, zh in bundle.get('speaker_names', {}).items():
            assert jp not in names or names[jp] == zh, ('Ambiguous speaker', jp)
            names[jp] = zh
        shared = bundle.get('shared', {})
        for code, draft in bundle['scenes'].items():
            source = f'export_base/event/e{code[1]}00/{code}.bf.json'
            assert hashlib.sha256((ROOT/source).read_bytes()).hexdigest() == draft['sha256'].lower()
            doc = read(ROOT/source)
            messages = draft['messages'].copy()
            omitted = set(draft.get('excluded_placeholder_indices', []))
            for i, msg in enumerate(doc['texts']):
                original = [TRAILING.sub('', LEADING.sub('', s)) for s in msg['lines']]
                if i in omitted:
                    assert str(i) not in messages
                    assert original in [['＞一枚絵イベントです。\n'], ['＞一枚絵のイベントです。\n'], ['＞特殊イベントです。\n'], ['＞アニメイベントです。\n']]
                    continue
                if str(i) not in messages:
                    assert all(s in shared for s in original), (code, i, 'Missing authored page')
                    messages[str(i)] = [shared[s] for s in original]
                assert len(messages[str(i)]) == len(original), (code, i)
                for a, b in zip(original, messages[str(i)]):
                    assert TOKEN.findall(a) == TOKEN.findall(b), (code, i, 'Control mismatch')
            assert set(messages) == {str(i) for i in range(len(doc['texts'])) if i not in omitted}
            speaker_names = {jp:names[jp] for jp in doc['speakers']}
            write(ROOT/'translation/story'/f'{code}.json', {
                'source':source,'source_sha256':draft['sha256'].lower(),
                'batch':f'{bundle["batch_prefix"]}_{code}.generated.json',
                'speaker_names':speaker_names,'messages':messages,
                'excluded_placeholder_indices':sorted(omitted),
                'authoring_bundle':str(path.relative_to(ROOT))})
            total += sum(map(len, messages.values()))
    print(f'Expanded {total} authored bundle pages.')

if __name__ == '__main__':
    main()
