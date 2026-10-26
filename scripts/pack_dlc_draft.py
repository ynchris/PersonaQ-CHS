"""Build and re-extract an internal DLC CPK; never modify the original CIA."""
import hashlib
import shutil
import sys
import tempfile
from pathlib import Path
from compile_translation import ROOT, read, write
from cpk_tools import run_logged

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()

def main(scope):
    assert scope in {'0005','0006','0007','0008','0009'}
    original=ROOT/'dlc'/('content_'+scope)/'data'
    build=read(ROOT/'translation'/f'dlc_{scope}_message_build.generated.json')
    assert build['roundtrip_verified']
    replacements={r['file']:r['sha256'] for r in build['files']}
    payload=ROOT/'full_work/dlc_messages'/scope/'payload'
    work=ROOT/'full_work/dlc_cpk_raw'/scope
    staging=work/'staging'
    expected={}
    for path in sorted(original.rglob('*')):
        if not path.is_file():
            continue
        rel=path.relative_to(original).as_posix()
        source=payload/rel if rel in replacements else path
        digest=sha(source)
        if rel in replacements:
            assert digest==replacements[rel]
        expected[rel]=digest
        target=staging/rel
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
    assert set(replacements)<=set(expected)
    assert {p.relative_to(staging).as_posix():sha(p) for p in staging.rglob('*') if p.is_file()}==expected
    tool=ROOT.parent/'references/PersonaQ2ChsLocalization/bin/CRI_File_System_Tools_v2.40.13.0/cpkmakec.exe'
    packed=work/(scope+'.cpk')
    run_logged([tool,staging,packed,'-mode=FILENAME','-forcecompress'],work,'pack.log')
    # Fresh extraction directory avoids accepting leftovers from older builds.
    verify=Path(tempfile.mkdtemp(prefix='verify_',dir=work))
    run_logged([tool,packed,'-extract='+str(verify)],work,'extract.log')
    actual={p.relative_to(verify).as_posix():sha(p) for p in verify.rglob('*') if p.is_file()}
    assert actual==expected, 'CPK content/inventory mismatch'
    write(ROOT/'translation'/f'dlc_{scope}_cpk.generated.json',{
        'status':'INCOMPLETE_INTERNAL_DRAFT','content':scope,'files':len(expected),
        'modified':sorted(replacements),'unmodified':len(expected)-len(replacements),
        'resource_sha256':expected,
        'cpk':str(packed),'sha256':sha(packed),'reextract_verified':True,
        'cia_rebuilt':False,'runtime_tested':False})
    print(f'DLC {scope}: verified {len(expected)} packed files; original CIA untouched.')

if __name__=='__main__':
    main(sys.argv[1])
