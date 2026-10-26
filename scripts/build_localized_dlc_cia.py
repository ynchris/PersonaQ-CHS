"""Build a separate internal DLC CIA; preserve original installers and contents."""
import shutil,tempfile
from pathlib import Path
from make_decrypted_cias import ROOT,CTR,TOOL,MAKER,run,sha
from compile_translation import read,write

def inventory(folder):
    return {p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file()}

def main():
    assembly=ROOT/'translation/integrated_build.generated.json'
    assembly_hash=sha(assembly)
    manifest=read(assembly)
    scopes={r['content'] for r in manifest['dlc_resources']}
    assert scopes=={'0005','0006','0007','0008','0009'}
    work=Path(tempfile.mkdtemp(prefix='localized_dlc_',dir=ROOT/'full_work'))
    output=work/'PQ1_JPN_DLC_CHS_INTERNAL.cia'
    args=[];contents=[]
    sources=sorted((ROOT/'dlc').glob('cia_contents.*'))
    assert len(sources)==10
    for source in sources:
        _,index,cid=source.name.split('.')
        original_hash=sha(source)
        baseline=ROOT/'cia_rebuild/dlc'/index/'decrypted.cfa'
        if index not in scopes:
            # Preserve the independently verified decrypted content byte-for-byte.
            checked=work/(index+'_baseline_romfs.bin')
            run([CTR,'-q',f'--romfs={checked}',baseline])
            assert sha(checked)==sha(ROOT/'cia_rebuild/dlc'/index/'romfs.bin')
            rebuilt=baseline
        else:
            report=read(ROOT/'translation'/f'dlc_{index}_cpk.generated.json')
            packed=Path(report['cpk'])
            assert report['reextract_verified'] and sha(packed)==report['sha256']
            for r in manifest['dlc_resources']:
                if r['content']==index:assert report['resource_sha256'][r['file']]==r['sha256']
            folder=work/index;folder.mkdir()
            romfs=folder/'romfs'
            shutil.copytree(ROOT/'dlc'/f'content_{index}'/'romfs',romfs)
            expected=inventory(romfs)
            assert f'{index}.cpk' in expected
            shutil.copy2(packed,romfs/f'{index}.cpk')
            expected[f'{index}.cpk']=report['sha256']
            assert inventory(romfs)==expected
            image=folder/'romfs.bin'
            run([TOOL,'-ctf','romfs',image,'--romfs-dir',romfs])
            rebuilt=folder/'localized.cfa'
            run([TOOL,'-ctf','cfa',rebuilt,'--header',ROOT/'cia_rebuild/dlc'/index/'header.bin','--romfs',image,'--not-encrypt'])
            checked=folder/'checked_romfs.bin'
            run([CTR,'-q',f'--romfs={checked}',rebuilt])
            assert sha(image)==sha(checked)
            extracted=folder/'reextracted'
            run([TOOL,'-xtf','romfs',checked,'--romfs-dir',extracted])
            assert inventory(extracted)==expected
        assert 'Crypto Key           None' in run([CTR,rebuilt])
        assert sha(source)==original_hash
        args+=['-content',f'{rebuilt}:{int(index,16)}:{int(cid,16)}']
        contents.append(dict(index=index,content_id=cid,file=str(rebuilt),sha256=sha(rebuilt),localized=index in scopes,original_sha256=original_hash))
        print(f'Content {index}: verified; localized={index in scopes}',flush=True)
    run([MAKER,'-f','cia','-o',output,'-ver','0','-ignoresign','-dlc']+args)
    info=run([CTR,output])
    assert '0004008c000c3600' in info.lower() and '(0)' in info
    assert 'Encrypted:   YES' not in info
    prefix=work/'cia_recheck'
    run([CTR,'-q',f'--contents={prefix}',output])
    for row in contents:
        p=Path(f'{prefix}.{row["index"]}.{row["content_id"]}')
        assert sha(p)==row['sha256']
    assert sha(assembly)==assembly_hash
    write(ROOT/'translation/localized_dlc_cia.generated.json',dict(status='INCOMPLETE_INTERNAL_DRAFT_NOT_A_RELEASE',file=str(output),sha256=sha(output),title_id='0004008c000c3600',version=0,contents=contents,integrated_manifest_sha256=assembly_hash,cia_content_roundtrip_verified=True,localized_romfs_inventory_verified=True,original_cias_modified=False,installed=False,runtime_tested=False))
    print('Verified internal DLC CIA:',output,flush=True)

if __name__=='__main__':main()
