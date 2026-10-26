"""Isolated runtime probe: 100 missing characters in the difficulty introduction.

Not a translation release. Never deploys or replaces an existing Citra mod.
"""
import hashlib
import shutil
import struct
import sys
from compile_translation import ROOT, read, write
from build_sample import run, DOTNET, HELPER
from check_roundtrip import members


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    work=ROOT/'full_work/raw_font_trial'
    plan=read(work/'plan.json')
    assignments=plan['new_assignments']
    assert assignments
    doc=read(ROOT/'test_json/difficultyselect.bin_difficultyselect.bmd.json')
    chars=list(assignments)
    assert len(chars)<=112, 'Probe needs additional pages'
    chunks=[chars[i:i+28] for i in range(0,len(chars),28)]
    expected=[]
    display=[]
    for n,chunk in enumerate(chunks):
        # ASCII labels distinguish the four pages without needing new glyphs.
        text=f'RAW FONT {n+1}/{len(chunks)}\n'
        for i,ch in enumerate(chunk):
            text+='{'+bytes.fromhex(assignments[ch]).hex(' ').upper()+'}'
            if i==13:
                text+='\n'
        text+='\n'
        expected.append(text)
        display.append(''.join(chunk))
    assert len(chunks)==len(doc['texts'][0]['lines']), 'Keep original page structure'
    doc['texts'][0]['lines']=['{F2 05 FF FF}{F1 41}'+s+'{F1 21}'+('{00}' if i==len(chunks)-1 else '') for i,s in enumerate(expected)]
    write(work/'probe_json/difficultyselect.bin_difficultyselect.bmd.json',doc)
    run([DOTNET,HELPER,'import','-i',ROOT/'test_input','-j',work/'probe_json','-o',work/'probe_rebuilt'])
    original=ROOT/'test_input/difficultyselect.bin'
    before=members(original)
    imported=dict(members(work/'probe_rebuilt/difficultyselect.bin'))
    new=imported['difficultyselect.bmd']
    # Verify exact contiguous runs, not decoder output (CP932 decoders lose undefined pairs).
    for chunk in chunks:
        for start in (0,14):
            run_bytes=b''.join(bytes.fromhex(assignments[c]) for c in chunk[start:start+14])
            if run_bytes:
                assert new.count(run_bytes)==1, 'Importer changed literal glyph bytes'
    source=original.read_bytes()
    result=bytearray(source[:4])
    pos=4
    for name,data in before:
        if name=='difficultyselect.bmd':
            result+=source[pos:pos+32]+struct.pack('<I',len(new))+new
        else:
            result+=source[pos:pos+36+len(data)]
        pos+=36+len(data)
    output=work/'probe_payload/title/difficultyselect.bin'
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_bytes(result)
    after=members(output)
    assert all(a==b for a,b in zip(before,after) if a[0]!='difficultyselect.bmd')
    report={'status':'PROBE_BINARY_VERIFIED_RUNTIME_PENDING','pages':display,
            'tested_characters':len(chars),'exact_byte_sequences_verified':True,
            'nontext_members_preserved':True,'sha256':hashlib.sha256(result).hexdigest(),
            'runtime_tested':False,'deployed':False}
    fonts=read(work/'font_build.generated.json')
    assert len(fonts)==6 and all(f['roundtrip_verified'] and f['original_pixels_preserved'] for f in fonts)
    for path in (work/'font_payload').glob('*.bcfnt'):
        target=work/'probe_payload/font'/path.name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(path,target)
    write(work/'probe_report.json',report)
    print(report)


if __name__=='__main__':
    main()
