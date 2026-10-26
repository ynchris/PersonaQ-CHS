"""Experimental byte-addressed font plan; never replaces the production map."""
from pathlib import Path
from compile_translation import read, write
from plan_font import cpcode

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'full_work/raw_font_trial'


def valid_pair(code):
    lead, trail = divmod(code, 256)
    return (0x81 <= lead <= 0x9f or 0xe0 <= lead <= 0xef) and 0x40 <= trail <= 0xfc and trail != 0x7f


def allocate(wanted, original, saved, hexadecimal=False):
    mapping = {ch: int.from_bytes(bytes.fromhex(s) if hexadecimal else s.encode('cp932'), 'big') for ch, s in saved.items()}
    used = set(original) | set(mapping.values())
    for ch in sorted(wanted):
        if ch not in mapping:
            code = cpcode(ch)
            if code is not None and code not in mapping.values():
                mapping[ch] = code
                used.add(code)
    candidates = [c for c in range(0x8140, 0xeffd) if valid_pair(c) and c not in used]
    missing = sorted(wanted - set(mapping))
    if len(missing) > len(candidates):
        raise ValueError(f'Raw capacity exceeded: {len(missing)} > {len(candidates)}')
    mapping.update(zip(missing, candidates))
    assert len(mapping.values()) == len(set(mapping.values()))
    assert all(c < 128 or valid_pair(c) for c in mapping.values())
    return mapping, candidates, missing


def main():
    manifests = [read(p) for p in sorted((ROOT/'sample_work/fonts').glob('*/*_manifest.json')) if not p.stem.startswith('demo_font')]
    assert len(manifests) == 6
    original = set().union(*(set(map(ord, m['glyphMap'])) for m in manifests))
    wanted = set(read(ROOT/'translation/required_characters.generated.json')['characters']) - set('\r\n\t')
    mapping, candidates, missing = allocate(wanted, original, read(ROOT/'translation/font_encoding.generated.json'))
    raw = {ch: c.to_bytes(1 if c < 256 else 2, 'big').hex().upper() for ch, c in mapping.items()}
    write(OUT/'encoding.hex.json', raw)
    report = {'status':'EXPERIMENTAL_RUNTIME_UNVERIFIED', 'required_characters':len(wanted),
              'mapped_characters':len(mapping), 'new_raw_slots_used':len(missing),
              'available_before_allocation':len(candidates), 'remaining_raw_slots':len(candidates)-len(missing),
              'original_code_overwrites':0, 'production_mapping_changed':False,
              'new_assignments':{ch:raw[ch] for ch in missing},
              'warning':'Offline plan only. Unassigned CP932 pairs need in-game validation; not a full-game capacity guarantee.'}
    write(OUT/'plan.json', report)
    print({k:v for k,v in report.items() if k != 'new_assignments'})


if __name__ == '__main__':
    main()
