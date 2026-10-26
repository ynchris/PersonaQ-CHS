"""Build a separate emulator-loadable CXI from the user's local decrypted ROM."""
import shutil,tempfile
from pathlib import Path
from make_decrypted_cias import ROOT,CTR,TOOL,run,sha
from compile_translation import read,write
from build_localized_update_cia import inventory

SOURCE=Path('C:/3ds/Games/PQ-SOTL-JPN-DecrTD-Ziperto/Persona Q - Shadow of the Labyrinth (Japan) Decrypted.3ds')

def main():
    manifest_path=ROOT/'translation/integrated_build.generated.json';manifest_hash=sha(manifest_path)
    manifest=read(manifest_path);cpk=read(ROOT/'translation/base_cpk.generated.json')
    assert cpk['integrated_manifest_sha256']==manifest_hash and cpk['reextract_verified']
    assert sha(Path(cpk['cpk']))==cpk['sha256']
    code=next(r for r in manifest['executable_resources'] if r['scope']=='base')
    assert sha(ROOT/code['output'])==code['sha256']
    assert shutil.disk_usage(ROOT).free>12*1024**3, 'Need at least 12 GiB for isolated build and verification'
    original_sha=sha(SOURCE)
    work=Path(tempfile.mkdtemp(prefix='localized_base_',dir=ROOT/'full_work'))
    partition=work/'original.cxi'
    run([TOOL,'-xtf','cci',SOURCE,'--partition0',partition])
    original=work/'original_sections';original.mkdir()
    sections=['exh','logo','plain','exefs']
    args=[TOOL,'-xtf','cxi',partition,'--header',original/'header.bin']
    for section in sections:args+=['--'+section,original/(section+'.bin')]
    run(args)
    assert sha(original/'exefs.bin')==sha(ROOT/'exefs.bin'), 'Different base ROM revision'
    header=work/'exefs_header.bin';extracted=work/'exefs_original'
    run([TOOL,'-xtfu','exefs',original/'exefs.bin','--header',header,'--exefs-dir',extracted])
    expected=inventory(extracted)
    assert expected['code.bin']==code['source_sha256']
    patched=work/'exefs_patched';shutil.copytree(extracted,patched)
    shutil.copy2(ROOT/code['output'],patched/'code.bin');expected['code.bin']=code['sha256']
    exefs=work/'exefs.bin'
    run([TOOL,'-ctfz','exefs',exefs,'--header',header,'--exefs-dir',patched])
    run([TOOL,'-xtfu','exefs',exefs,'--exefs-dir',work/'exefs_checked'])
    assert inventory(work/'exefs_checked')==expected
    romfs_dir=work/'romfs';shutil.copytree(ROOT/'romfs',romfs_dir)
    romfs_expected=inventory(romfs_dir)
    shutil.copy2(Path(cpk['cpk']),romfs_dir/'data.cpk');romfs_expected['data.cpk']=cpk['sha256']
    assert inventory(romfs_dir)==romfs_expected
    romfs=work/'romfs.bin';run([TOOL,'-ctf','romfs',romfs,'--romfs-dir',romfs_dir])
    run([TOOL,'-xtf','romfs',romfs,'--romfs-dir',work/'romfs_checked'])
    assert inventory(work/'romfs_checked')==romfs_expected
    output=work/'PQ1_JPN_CHS_LAYOUT_TEST.cxi'
    args=[TOOL,'-ctf','cxi',output,'--header',original/'header.bin','--not-encrypt','--exefs',exefs,'--romfs',romfs]
    for section in ['exh','logo','plain']:
        p=original/(section+'.bin')
        if p.exists() and p.stat().st_size:args+=['--'+section,p]
    run(args)
    info=run([CTR,output])
    assert '00040000000c3600' in info.lower() and 'Crypto Key           None' in info
    checked=work/'checked';checked.mkdir()
    args=[TOOL,'-xtf','cxi',output]
    for section in ['exh','logo','plain','exefs','romfs']:args+=['--'+section,checked/(section+'.bin')]
    run(args)
    for section in ['exh','logo','plain']:
        p=original/(section+'.bin')
        if p.exists() and p.stat().st_size:assert sha(p)==sha(checked/(section+'.bin'))
    assert sha(checked/'exefs.bin')==sha(exefs)
    assert sha(checked/'romfs.bin')==sha(romfs)
    assert sha(SOURCE)==original_sha and sha(manifest_path)==manifest_hash
    write(ROOT/'translation/localized_base_cxi.generated.json',dict(
        file=str(output),sha256=sha(output),bytes=output.stat().st_size,title_id='00040000000c3600',
        integrated_manifest_sha256=manifest_hash,encoding_sha256=manifest['encoding_sha256'],
        code_sha256=code['sha256'],base_cpk_sha256=cpk['sha256'],
        original_rom=str(SOURCE),original_rom_sha256=original_sha,original_rom_modified=False,
        exefs_roundtrip_verified=True,romfs_inventory_verified=True,cxi_sections_verified=True,
        runtime_tested=False,installed=False,status='INCOMPLETE_INTERNAL_DRAFT_NOT_A_RELEASE'))
    print('Verified emulator-test CXI:',output,flush=True)

if __name__=='__main__':main()
