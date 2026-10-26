"""Extend the runtime-tested byte map without changing existing assignments."""
from compile_translation import ROOT, read, write
from plan_raw_font import allocate
from raw_text_codec import validate


def main():
    trial=ROOT/'full_work/raw_font_trial'
    review=read(trial/'compressed_control/runtime_review.json')
    assert review['status']=='USER_CONFIRMED_BOOT_AND_FOUR_PAGE_GLYPH_PROBE_PASSED'
    path=ROOT/'translation/font_encoding.hex.json'
    saved=read(path if path.exists() else trial/'encoding.hex.json')
    validate(saved)
    manifests=[read(p) for p in (ROOT/'sample_work/fonts').glob('*/*_manifest.json') if not p.stem.startswith('demo_font')]
    assert len(manifests)==6
    original=set().union(*(set(map(ord,m['glyphMap'])) for m in manifests))
    wanted=set(read(ROOT/'translation/required_characters.generated.json')['characters'])-set('\r\n\t')
    try:
        mapping,candidates,missing=allocate(wanted,original,saved,hexadecimal=True)
    except ValueError as exc:
        write(ROOT/'translation/font_capacity_status.generated.json',{
            'status':'blocked_raw_capacity','encoding_file':str(path),
            'live_encoding_unchanged':True,'error':str(exc)})
        raise
    result={ch:c.to_bytes(1 if c<256 else 2,'big').hex().upper() for ch,c in mapping.items()}
    validate(result)
    assert all(result[k]==v for k,v in saved.items())
    write(path,result)
    write(ROOT/'translation/font_capacity_status.generated.json',{
        'status':'planned_raw_byte_encoding','encoding_file':str(path),
        'target_characters':len(result),'new_assignments':len(missing),
        'available_surrogate_slots':len(candidates)-len(missing),
        'original_code_overwrites':0,'font_build_required':True,
        'runtime_scope':'Initial 100 new codes tested in difficulty introduction only; not full-game validation'})
    print(f'Production byte map: {len(result)} characters; {len(candidates)-len(missing)} candidates remain.')


if __name__=='__main__':
    main()
