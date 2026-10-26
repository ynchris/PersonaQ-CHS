"""Read-only Q2 name comparison; never apply reference translations automatically."""
import hashlib
import json
from equipment_names import ROOT, load_drafts


def main():
    _, _, names, drafts = load_drafts()
    source = ROOT.parent / 'references/PersonaQ2ChsLocalization/texts/zh_Hans/init/itemtbl.bin.json'
    reference = json.loads(source.read_text(encoding='utf-8-sig'))
    by_original = {}
    for row in reference:
        by_original.setdefault(row['original'], []).append(row)
    matches = []
    for index, translation in sorted(drafts.items()):
        candidates = by_original.get(names[index], [])
        if candidates:
            matches.append(dict(index=index, original=names[index], current=translation,
                                candidates=[{k: r.get(k) for k in ('key', 'translation', 'stage', 'context')} for r in candidates]))
    report = dict(reference=str(source), reference_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  equipment_names=len(drafts), exact_original_matches=len(matches), applied=0,
                  caveat='Exact Japanese names are candidates only: context, translation quality and reuse permission require review.',
                  matches=matches)
    output = ROOT / 'translation/equipment_q2_reference.generated.json'
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'{len(matches)} exact-name reference candidates; no translations applied.')


if __name__ == '__main__':
    main()
