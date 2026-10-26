"""Plan an additive CP932 font mapping, retaining every original font code.

Includes GB2312 Han characters up front, plus actual translated punctuation.
This is an offline encoding plan, not a claim of emulator compatibility.
"""
import argparse
import json
from pathlib import Path
from compile_translation import read, write

ROOT = Path(__file__).resolve().parent

def cpcode(char):
    try:
        raw = char.encode('cp932')
        if not ((len(raw)==1 and 0x20<=raw[0]<0x80) or (len(raw)==2 and 0x81<=raw[0]<0xf0)):
            return None
        if raw.decode('cp932') != char:
            return None
        return int.from_bytes(raw, 'big')
    except UnicodeError:
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--all-gb2312', action='store_true')
    args = parser.parse_args()
    manifests = {}
    for path in sorted((ROOT/'sample_work/fonts').glob('*/*_manifest.json')):
        if path.stem.startswith('demo_font'):
            continue
        manifests[path.parent.name] = read(path)
    if len(manifests) != 6:
        raise ValueError('Expected six principal original font manifests')
    original_codes = set().union(*(set(map(ord,m['glyphMap'])) for m in manifests.values()))
    wanted = set(read(ROOT/'translation/required_characters.generated.json')['characters'])
    wanted.difference_update('\r\n\t')
    for code in range(0x4e00,0xa000) if args.all_gb2312 else ():
        ch = chr(code)
        try:
            ch.encode('gb2312')
            wanted.add(ch)
        except UnicodeError:
            pass
    saved_path=ROOT/'translation/font_encoding.generated.json'
    saved=read(saved_path) if saved_path.exists() else {}
    mapping={}
    for char,encoded in saved.items():
        code=cpcode(encoded)
        if code is None:
            raise ValueError('Previous mapping contains control-range bytes; preserve and investigate')
        mapping[char]=chr(code)
    wanted.update(mapping)
    used = set(original_codes)|set(map(ord,mapping.values()))
    for ch in sorted(wanted):
        if ch in mapping:
            continue
        code = cpcode(ch)
        if code is not None and chr(code) not in mapping.values():
            mapping[ch] = chr(code)
            used.add(code)
    candidates = []
    # F0-FF are Atlus message controls, not available CP932 lead bytes.
    for lead in list(range(0x81,0xa0))+list(range(0xe0,0xf0)):
        for trail in range(0x40,0xfd):
            if trail == 0x7f:
                continue
            raw=bytes([lead,trail])
            code=int.from_bytes(raw,'big')
            try:
                ch=raw.decode('cp932')
                if ch.encode('cp932') == raw and code not in used:
                    candidates.append(code)
            except UnicodeError:
                pass
    missing=sorted(wanted-set(mapping))
    if len(missing)>len(candidates):
        write(ROOT/'translation/font_capacity_status.generated.json',{
            'status':'blocked_capacity','required_new_surrogates':len(missing),
            'available_surrogate_slots':len(candidates),
            'unallocated_characters':''.join(missing),
            'live_encoding_unchanged':True,'font_build_required':True,
            'note':'Draft translation may continue; do not package it with old fonts.'})
        raise ValueError(f'Encoding capacity exceeded: {len(missing)} > {len(candidates)}')
    for ch,code in zip(missing,candidates):
        mapping[ch]=chr(code)
    if len(set(mapping.values()))!=len(mapping):
        raise ValueError('Mapping collision')
    encoding={ch:ord(code).to_bytes(2,'big').lstrip(b'\0').decode('cp932') for ch,code in mapping.items()}
    for ch,code in mapping.items():
        assert int.from_bytes(encoding[ch].encode('cp932'),'big')==ord(code)
        if cpcode(ch) is None:
            assert ord(code) not in original_codes
    report={
        'scope':'GB2312 Han plus draft characters' if args.all_gb2312 else 'Actual draft characters only',
        'target_characters':len(mapping), 'new_surrogate_codes':len(missing),
        'reserved_original_codes':len(original_codes), 'remaining_candidate_codes':len(candidates)-len(missing),
        'original_code_overwrites':0, 'runtime_tested':False, 'fonts':[]}
    for name,m in manifests.items():
        added=set(mapping.values())-set(m['glyphMap'])
        count=max(m['glyphMap'].values())+1+len(added)
        per=m['textureInfo']['sheetInfo']['cols']*m['textureInfo']['sheetInfo']['rows']
        report['fonts'].append({'name':name,'original_glyphs':max(m['glyphMap'].values())+1,
                               'added_glyphs':len(added),'planned_glyphs':count,
                               'original_sheets':m['textureInfo']['sheetCount'],
                               'planned_sheets':(count+per-1)//per})
    write(ROOT/'translation/font_encoding.generated.json',encoding)
    write(ROOT/'translation/font_plan.generated.json',report)
    write(ROOT/'translation/font_capacity_status.generated.json',{
        'status':'planned','available_surrogate_slots':len(candidates)-len(missing),
        'target_characters':len(mapping),'font_build_required':True})
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':
    # Retain cpcode and the old planner as reference, but do not let the usual
    # command overwrite the active capacity status with the obsolete CP932 limit.
    import sys
    if len(sys.argv)>1:
        raise SystemExit('Legacy planner options are retired; use plan_production_font.py for the active byte map.')
    from plan_production_font import main as production_main
    production_main()
