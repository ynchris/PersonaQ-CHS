"""Pack the entire base CPK and verify every re-extracted file; internal only."""
import shutil
import tempfile
from pathlib import Path
from compile_translation import ROOT, read, write
from cpk_tools import run_logged
from pack_dlc_draft import sha

def main():
    manifest_path=ROOT/'translation/integrated_build.generated.json'
    manifest_hash=sha(manifest_path)
    manifest=read(manifest_path)
    assert manifest['status']=='INCOMPLETE_INTERNAL_DRAFT_NOT_A_RELEASE'
    replacements={r['file']:r['sha256'] for r in manifest['resources']}
    original=ROOT/'data'
    payload=ROOT/'full_work/integrated_payload'
    work=ROOT/'full_work/base_cpk_raw'
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
    actual={p.relative_to(staging).as_posix():sha(p) for p in staging.rglob('*') if p.is_file()}
    assert actual==expected, 'Staging mismatch'
    print(f'Staging checked: {len(expected)} resources.',flush=True)
    tool=ROOT.parent/'references/PersonaQ2ChsLocalization/bin/CRI_File_System_Tools_v2.40.13.0/cpkmakec.exe'
    packed=work/'data.cpk'
    run_logged([tool,staging,packed,'-mode=FILENAME','-forcecompress'],work,'pack.log')
    verify=Path(tempfile.mkdtemp(prefix='verify_',dir=work))
    run_logged([tool,packed,'-extract='+str(verify)],work,'extract.log')
    actual={p.relative_to(verify).as_posix():sha(p) for p in verify.rglob('*') if p.is_file()}
    assert actual==expected, 'CPK re-extraction mismatch'
    assert sha(manifest_path)==manifest_hash, 'Build manifest changed during packaging'
    write(ROOT/'translation/base_cpk.generated.json',{
        'status':'INCOMPLETE_INTERNAL_DRAFT','files':len(expected),
        'modified':sorted(replacements),'unmodified':len(expected)-len(replacements),
        'cpk':str(packed),'sha256':sha(packed),'reextract_verified':True,
        'integrated_manifest_sha256':manifest_hash,'runtime_tested':False,
        'update_runtime_verified':False,'deployed':False})
    print(f'Base CPK: verified {len(expected)} packed files, {len(replacements)} replacements. Not deployed.')

if __name__=='__main__':
    main()
