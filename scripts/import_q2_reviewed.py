"""Import explicitly selected exact matches with recorded local review amendments."""
import hashlib
import re
import sys
from collections import Counter
import unicodedata
from compile_translation import ROOT, read, write, LEADING, TRAILING, TOKEN
from reuse_q2_exact import REF, body


def main(plan_path):
    plan = read(ROOT/plan_path)
    target = ROOT/'translation/batches'/plan['batch']
    if target.exists():
        raise ValueError('Refusing to overwrite existing draft')
    reference_root = (ROOT/plan['reference_root']).resolve() if 'reference_root' in plan else REF
    candidates = {r['key']: r for r in read(ROOT/plan.get('candidates', 'translation/q2_exact_candidates.generated.json'))}
    current = {r['key']: r for r in read(ROOT/'translation/catalog.working.json')}
    sources, hashes, audit = {}, {}, []
    cache = {}
    for source, indices in plan['selections'].items():
        doc = read(ROOT/source)
        hashes[source] = hashlib.sha256((ROOT/source).read_bytes()).hexdigest()
        sources[source] = []
        for selection in indices:
            mi, li = selection if isinstance(selection, list) else (selection, 0)
            slot = f'{mi}:{li}' if li else str(mi)
            key = f'{source}:{mi}:{li}'
            row, candidate = current[key], candidates[key]
            overrides = plan['overrides'].get(source, {})
            assert not row.get('translation')
            assert not candidate['reasons'] or (candidate['reasons'] == ['conflicting_translations'] and slot in overrides)
            assert body(row['original']) == candidate['original']
            for reference in candidate['references']:
                path = reference_root/reference['reference']
                if path not in cache:
                    cache[path] = (hashlib.sha256(path.read_bytes()).hexdigest(), read(path))
                digest, items = cache[path]
                assert digest == reference['reference_sha256']
                assert any(r.get('key') == reference['reference_key'] and r['original'].strip() == candidate['original'] and r['translation'].strip() == reference['translation'] for r in items)
            value = candidate['variants'][0]
            if plan.get('compact_before_review'):
                value = value.replace('\n', '')
            for old, new in plan['replacements'].items():
                value = value.replace(old, new)
            for old, new in plan.get('phrase_fixes', {}).get(source, {}).get(slot, []):
                assert old in value, (key, old)
                value = value.replace(old, new)
            value = overrides.get(slot, value)
            if source in plan.get('reflow_sources', []):
                width = max(map(len, candidate['original'].splitlines()))
                compact = value.replace('\n', '')
                value = '\n'.join(compact[i:i+width] for i in range(0, len(compact), width))
            old_body = TRAILING.sub('', LEADING.sub('', row['original']))
            if old_body.endswith('\n'):
                value += '\n'
            full = LEADING.match(row['original']).group()+value+TRAILING.search(row['original']).group()
            assert TOKEN.findall(full) == TOKEN.findall(row['original'])
            assert not re.search(r'[{}\u3041-\u3096\u30a1-\u30fa]', value)
            def numbers(s):
                return Counter(re.findall(r'\d+', unicodedata.normalize('NFKC', s)))
            assert numbers(value) == numbers(candidate['original']), key
            sources[source].append([mi, li, doc['texts'][mi]['id'], value])
            audit.append({**candidate, 'final_body': value, 'amended': value.strip() != candidate['variants'][0]})
    write(target, dict(status='draft', sources=sources, source_hashes=hashes, review_notes=plan['notes']))
    write(ROOT/'translation'/plan['batch'].replace('.generated.json','.audit.generated.json'),dict(entries=audit, plan_sha256=hashlib.sha256((ROOT/plan_path).read_bytes()).hexdigest(), runtime_tested=False))
    print(f'Imported {len(audit)} rows; {sum(r["amended"] for r in audit)} amended for terminology or meaning.')


if __name__ == '__main__':
    main(sys.argv[1])
