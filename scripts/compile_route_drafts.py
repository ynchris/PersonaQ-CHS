"""Compile explicitly authored route-difference pages without replacing reuse rows."""
import hashlib
from compile_translation import ROOT, read, write, LEADING, TRAILING, TOKEN

def main():
    total = 0
    names = {}
    for path in (ROOT/'translation/story').glob('*.json'):
        for jp, zh in read(path)['speaker_names'].items():
            assert jp not in names or names[jp] == zh
            names[jp] = zh
    paths = sorted((ROOT/'translation/route_drafts').glob('*.json'))
    for path in paths:
        for jp, zh in read(path).get('speaker_names', {}).items():
            assert jp not in names or names[jp] == zh, ('Ambiguous speaker', jp)
            names[jp] = zh
    pending = []
    for path in paths:
        draft = read(path)
        sources, hashes, speakers = {}, {}, {}
        for code, scene in draft['scenes'].items():
            source = f'export_base/event/e{code[1]}00/{code}.bf.json'
            doc = read(ROOT/source)
            digest = hashlib.sha256((ROOT/source).read_bytes()).hexdigest()
            assert digest == scene['sha256'], (code, 'Source changed')
            hashes[source] = digest
            rows, seen = [], set()
            for mi, li, zh in scene['pages']:
                assert (mi, li) not in seen, (code, mi, li)
                seen.add((mi, li))
                msg = doc['texts'][mi]
                jp = TRAILING.sub('', LEADING.sub('', msg['lines'][li]))
                assert isinstance(zh, str) and zh.strip()
                assert TOKEN.findall(jp) == TOKEN.findall(zh), (code, mi, li, 'Controls')
                assert 'イベントです。' not in jp, (code, mi, li, 'Developer placeholder')
                rows.append([mi, li, msg['id'], zh])
            sources[source] = rows
            assert set(doc['speakers']) <= set(names), (code, 'Missing speaker translation')
            speakers[source] = [[i,jp,names[jp]] for i,jp in enumerate(doc['speakers']) if jp != names[jp]]
            total += len(rows)
        pending.append((ROOT/'translation/batches'/draft['batch'], {'status':'draft','sources':sources,
              'speakers':speakers,'source_hashes':hashes,'authoring_source':str(path.relative_to(ROOT))}))
    # A bad page must not leave earlier batches regenerated and later ones stale.
    for path, batch in pending:
        write(path, batch)
    print(f'Compiled {total} explicitly authored route-difference pages.')

if __name__ == '__main__':
    main()
