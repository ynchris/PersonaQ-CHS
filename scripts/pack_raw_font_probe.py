"""Package an isolated full base CPK for the raw glyph runtime experiment."""
import hashlib
import shutil
from compile_translation import ROOT, read, write
from cpk_tools import run_logged


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    work=ROOT/'full_work/raw_font_trial'
    report=read(work/'probe_report.json')
    assert report['exact_byte_sequences_verified']
    payload=work/'probe_payload'
    replacements={p.relative_to(payload).as_posix():sha(p) for p in payload.rglob('*') if p.is_file()}
    assert len(replacements)==7
    staging=work/'cpk_staging'
    expected={}
    for path in sorted((ROOT/'data').rglob('*')):
        if not path.is_file():
            continue
        rel=path.relative_to(ROOT/'data').as_posix()
        source=payload/rel if rel in replacements else path
        expected[rel]=sha(source)
        target=staging/rel
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
    assert set(replacements)<=set(expected)
    assert {p.relative_to(staging).as_posix():sha(p) for p in staging.rglob('*') if p.is_file()}==expected
    tool=ROOT.parent/'references/PersonaQ2ChsLocalization/bin/CRI_File_System_Tools_v2.40.13.0/cpkmakec.exe'
    target=work/'mod/00040000000C3600/romfs/data.cpk'
    target.parent.mkdir(parents=True,exist_ok=True)
    run_logged([tool,staging,target,'-mode=FILENAME'],work,'probe_pack.log')
    verify=work/'cpk_verify'
    verify.mkdir(exist_ok=True)
    run_logged([tool,target,'-extract='+str(verify)],work,'probe_extract.log')
    assert {p.relative_to(verify).as_posix():sha(p) for p in verify.rglob('*') if p.is_file()}==expected
    write(work/'package_report.json',{'status':'RUNTIME_PROBE_NOT_TRANSLATION_RELEASE',
          'cpk':str(target),'sha256':sha(target),'files':len(expected),'modified':replacements,
          'reextract_verified':True,'runtime_tested':False,'deployed':False})
    print(f'Verified {len(expected)} files; seven probe replacements; not deployed.',flush=True)


if __name__=='__main__':
    main()
