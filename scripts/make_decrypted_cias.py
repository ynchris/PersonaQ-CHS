"""Rebuild decrypted installable CIA copies from extracted NCCH contents."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parent
WORK=ROOT.parent
CTR=Path('C:/3ds/ctrtool-v1.3.0-win_x64/ctrtool.exe')
TOOL=WORK/'tools/3dstool-v1.2.6-win/3dstool.exe'
MAKER=WORK/'references/PersonaQ2ChsLocalization/bin/Project_CTR/makerom.exe'

def run(args):
    result=subprocess.run([str(a) for a in args],capture_output=True,text=True,errors='replace')
    if result.returncode:
        raise RuntimeError(f'{Path(args[0]).name} failed: {result.stderr[-2000:]}')
    return result.stdout

def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    out=ROOT/'decrypted_installers'
    out.mkdir(exist_ok=True)
    reports=[]
    for category,version in [('update',2096),('dlc',0)]:
        contentargs=[]
        for source in sorted((ROOT/category).glob('cia_contents.*')):
            _,index,cid=source.name.split('.')
            folder=ROOT/'cia_rebuild'/category/index
            folder.mkdir(parents=True,exist_ok=True)
            executable=category=='update' and index=='0000'
            kind='cxi' if executable else 'cfa'
            sections=['romfs']
            if executable:
                sections+=['exefs','exh','logo','plain']
            args=[TOOL,'-xtf',kind,source,'--header',folder/'header.bin']
            for section in sections:
                args += ['--'+section,folder/(section+'.bin')]
            run(args)
            decrypted=folder/('decrypted.'+kind)
            args=[TOOL,'-ctf',kind,decrypted,'--header',folder/'header.bin','--not-encrypt']
            for section in sections:
                path=folder/(section+'.bin')
                if path.exists() and path.stat().st_size:
                    args += ['--'+section,path]
            run(args)
            info=run([CTR,decrypted])
            assert 'Crypto Key           None' in info, f'NCCH still encrypted: {index}'
            # Check decrypted payloads against the independently extracted original.
            args=[CTR,'-q']
            verify_sections=['romfs']+(['exefs','exheader'] if executable else [])
            for section in verify_sections:
                args.append(f'--{section}={folder / ("checked_"+section+".bin")}')
            args.append(decrypted)
            run(args)
            for section in verify_sections:
                original=folder/(('exh' if section=='exheader' else section)+'.bin')
                checked=folder/('checked_'+section+'.bin')
                assert original.read_bytes()==checked.read_bytes(), f'Payload mismatch: {category} {index} {section}'
            contentargs+=['-content',f'{decrypted}:{int(index,16)}:{int(cid,16)}']
            print(f'{category} content {index}: decrypted and payload verified',flush=True)
        filename=out/f'PQ1_JPN_{category}_decrypted.cia'
        if filename.exists():
            raise FileExistsError(filename)
        args=[MAKER,'-f','cia','-o',filename,'-ver',str(version),'-ignoresign']
        if category=='dlc':
            args+=['-dlc']
        run(args+contentargs)
        info=run([CTR,filename])
        assert 'Encrypted:   YES' not in info, 'CIA wrapper encryption remains'
        expected='0004000e000c3600' if category=='update' else '0004008c000c3600'
        assert expected in info.lower(), 'Wrong title ID'
        assert f'({version})' in info, 'Wrong title version'
        # Extract newly packaged NCCH files and compare to the verified inputs.
        prefix=folder.parent/'recheck'
        run([CTR,'-q',f'--contents={prefix}',filename])
        for n in range(0,len(contentargs),2):
            path,index,cid=contentargs[n+1].rsplit(':',2)
            extracted=Path(f'{prefix}.{int(index):04x}.{int(cid):08x}')
            assert sha(Path(path))==sha(extracted), 'CIA content changed during packaging'
        reports.append(dict(file=str(filename),title_id=expected,version=version,
            contents=len(contentargs)//2,sha256=sha(filename),payload_verified=True,
            emulator_installation_tested=False))
        print(f'Created and verified: {filename}',flush=True)
    (out/'verification.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')

if __name__=='__main__':
    main()
