"""Conservative translation memory for corresponding P3/P4 route scenes.

Only paired eN00/eN10 scenes (chapters 1 through 6) are searched. Entire message
page bodies (including internal controls) and speakers must match exactly.
Short utterances, ambiguous translations and name-dependent outer controls
are excluded. Source/target evidence is recorded for review.
"""
import argparse
import hashlib
import re
from collections import defaultdict
from compile_translation import ROOT, read, write, TOKEN, LEADING, TRAILING

def body(text):
    return TRAILING.sub('', LEADING.sub('', text))

def name_safe(text):
    outer = LEADING.match(text).group() + TRAILING.search(text).group()
    return not re.search(r'\{F1 8[12]\}|\{F5 C1 (?:0A|0E|10) ', outer)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    rows = read(ROOT/'translation/catalog.working.json')
    target_batch = '098_parallel_routes.generated.json'
    occupied = {r['key'] for r in rows if r['translation'] and r.get('batch') != target_batch}
    index = defaultdict(list)
    for r in rows:
        if r['status'] != 'draft_control_checked' or r.get('batch') == target_batch:
            continue
        if not re.search(r'/e[1-6]00_\d+\.bf\.json$', r['source']):
            continue
        if not name_safe(r['original']):
            continue
        index[(r['source'], r['speaker'], body(r['original']))].append(r)
    evidence, sources, hashes = [], defaultdict(list), {}
    for r in rows:
        if r['key'] in occupied or not name_safe(r['original']):
            continue
        paired = re.sub(r'/e([1-6])10_', r'/e\g<1>00_', r['source'])
        if paired == r['source']:
            continue
        original = body(r['original'])
        plain = TOKEN.sub('', original)
        if len(plain.strip()) < 12 or not re.search(r'[\u3041-\u3096\u30a1-\u30fa]', plain):
            continue
        matches = index.get((paired, r['speaker'], original), [])
        translations = {body(m['translation']) for m in matches}
        if len(translations) != 1:
            continue
        translated = translations.pop()
        if translated == original:
            continue
        assert TOKEN.findall(translated) == TOKEN.findall(original)
        source_row = matches[0]
        sources[r['source']].append([r['message_index'], r['line_index'], r['message_id'], translated])
        evidence.append({'target_key':r['key'], 'source_key':source_row['key'],
                         'speaker':r['speaker'], 'original':original,'translation':translated})
        for path in (r['source'], paired):
            if path not in hashes:
                hashes[path] = hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    report = {'policy':'paired scene + exact speaker + exact body incl internal controls; minimum 12 chars; no outer name insertion',
              'count':len(evidence),'documents':len(sources),'source_hashes':hashes,'matches':evidence}
    write(ROOT/'translation/parallel_reuse_review.generated.json', report)
    if args.apply:
        write(ROOT/'translation/batches'/target_batch, {'status':'draft','sources':sources,
              'speakers':{},'source_hashes':hashes,'review':'parallel_reuse_review.generated.json'})
    print(f'{len(evidence)} exact paired-route pages in {len(sources)} documents; applied={args.apply}')

if __name__ == '__main__':
    main()
