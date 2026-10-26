"""Measure candidate strategies without changing the live encoding/font files."""
from compile_translation import ROOT, read, write
from plan_font import cpcode

def main():
    originals=set()
    for path in (ROOT/'sample_work/fonts').glob('*/*_manifest.json'):
        if not path.stem.startswith('demo_font'):
            originals.update(map(ord,read(path)['glyphMap']))
    mapping=read(ROOT/'translation/font_encoding.generated.json')
    occupied=originals|{cpcode(c) for c in mapping.values()}
    canonical=set()
    undefined=set()
    aliases=set()
    for lead in [*range(0x81,0xa0),*range(0xe0,0xf0)]:
        for trail in range(0x40,0xfd):
            if trail==0x7f:
                continue
            raw=bytes([lead,trail])
            code=int.from_bytes(raw,'big')
            try:
                char=raw.decode('cp932')
                (canonical if char.encode('cp932')==raw else aliases).add(code)
            except UnicodeError:
                undefined.add(code)
    chinese=set()
    for code in range(0x4e00,0xa000):
        try:
            chr(code).encode('gb2312')
            chinese.add(chr(code))
        except UnicodeError:
            pass
    required_new={c for c in chinese if c not in mapping and (cpcode(c) is None or cpcode(c) in {cpcode(x) for x in mapping.values()})}
    write(ROOT/'translation/encoding_capacity.audit.json',{
        'live_mapping_unchanged':True,'original_font_codes':len(originals),
        'canonical_double_byte_slots':len(canonical),
        'free_canonical_slots':len(canonical-occupied),
        'undefined_cp932_slots_not_authorized_for_use':len(undefined-occupied),
        'alias_slots_not_authorized_for_use':len(aliases-occupied),
        'gb2312_han_characters':len(chinese),
        'additional_surrogates_for_full_gb2312':len(required_new),
        'full_gb2312_fits_current_preservation_strategy':len(required_new)<=len(canonical-occupied),
        'runtime_tested':False,
        'constraints':['F0-FF remain reserved for Atlus control instructions',
                       'Undefined or alias slots require custom codec and game-side verification',
                       'Do not overwrite original glyphs while untranslated sources may use them',
                       'Final remapping requires an inventory of residual messages, tables, code strings and user names',
                       'Q2 full-remap approach cannot be copied blindly onto partially translated PQ1']})
    print(f'Capacity audit: {len(canonical-occupied)} canonical slots free; full GB2312 needs {len(required_new)} additional surrogates.')

if __name__=='__main__':
    main()
