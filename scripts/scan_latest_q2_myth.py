"""Freeze latest-reference compendium matches without touching historical audits."""
import hashlib
from collections import defaultdict
from compile_translation import ROOT, read, write
from reuse_q2_exact import body

LATEST = ROOT.parent/'references/PersonaQ2ChsLocalization-latest-20260928/texts/zh_Hans'
def main():
    path = LATEST/'facility/datmyth.bmd.json'
    rows = read(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    index = defaultdict(list)
    for row in rows:
        if row.get('translation') and row['translation'] != row['original']:
            index[row['original'].strip()].append(dict(translation=row['translation'].strip(), reference='facility/datmyth.bmd.json', reference_key=row['key'], stage=row.get('stage'), reference_sha256=digest))
    result = []
    for row in read(ROOT/'translation/catalog.working.json'):
        if row['source'] != 'export_base/facility/datmyth.bmd.json' or row.get('translation'):
            continue
        matches = index.get(body(row['original']), [])
        if matches:
            variants = sorted({r['translation'] for r in matches})
            result.append(dict(key=row['key'], source=row['source'], original=body(row['original']), variants=variants, references=matches, reasons=[] if len(variants)==1 else ['conflicting_translations']))
    write(ROOT/'translation/q2_latest_myth_candidates.generated.json',result)
    print(f'Latest compendium: {len(result)} exact untranslated candidates.')

if __name__ == '__main__':
    main()
