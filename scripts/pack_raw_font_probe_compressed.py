"""Compression-only control against the failed raw-font probe. Never deploys."""
from compile_translation import ROOT, read, write
from pack_raw_font_probe import sha
from cpk_tools import run_logged
from audit_cpk_layout import inspect


def inventory(directory):
    return {p.relative_to(directory).as_posix():sha(p) for p in directory.rglob('*') if p.is_file()}


def main():
    trial=ROOT/'full_work/raw_font_trial'
    failed=read(trial/'package_report.json')
    assert failed['reextract_verified']
    assert sha(trial/'mod/00040000000C3600/romfs/data.cpk')==failed['sha256']
    expected=inventory(trial/'cpk_verify')
    assert len(expected)==failed['files']==7722
    assert inventory(trial/'cpk_staging')==expected
    work=trial/'compressed_control'
    target=work/'mod/00040000000C3600/romfs/data.cpk'
    target.parent.mkdir(parents=True,exist_ok=True)
    tool=ROOT.parent/'references/PersonaQ2ChsLocalization/bin/CRI_File_System_Tools_v2.40.13.0/cpkmakec.exe'
    print('Verified staging equals failed probe content; changing compression only.',flush=True)
    run_logged([tool,trial/'cpk_staging',target,'-mode=FILENAME','-forcecompress'],work,'pack.log')
    verify=work/'verify'
    verify.mkdir(exist_ok=True)
    run_logged([tool,target,'-extract='+str(verify)],work,'extract.log')
    assert inventory(verify)==expected, 'Compression control content changed'
    layout=inspect(target)
    assert layout['compressed_files']>0
    write(work/'package_report.json',{'status':'COMPRESSION_ONLY_CONTROL_RUNTIME_PENDING',
          'cpk':str(target),'sha256':sha(target),'bytes':target.stat().st_size,
          'failed_probe_sha256':failed['sha256'],'files':len(expected),
          'all_extracted_files_identical_to_failed_probe':True,
          'compressed_files':layout['compressed_files'],'reextract_verified':True,
          'runtime_tested':False,'deployed':False})
    write(work/'layout.json',layout)
    print(f'Compression control verified: {target.stat().st_size} bytes; {layout["compressed_files"]} compressed files.',flush=True)


if __name__=='__main__':
    main()
