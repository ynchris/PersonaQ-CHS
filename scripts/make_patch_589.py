"""Build the player patch kit for revision 589: per-content xdelta patches + one-click PowerShell patcher.
Base: decrypted .3ds partition0 -> localized CXI; update/DLC: decrypted NCCH content -> localized content."""
import hashlib,json,shutil,subprocess,sys
from pathlib import Path
from make_decrypted_cias import ROOT,CTR,TOOL,MAKER,run,sha
from compile_translation import read
OUT=ROOT/'PQ1_CHS_PATCH_589'
XD=ROOT.parent/'tools/xdelta3/xdelta3-3.1.0-x86_64.exe'
KIT=ROOT/'patch_kit'
BASE_3DS_SHA='568eb1dda845432557ce290abf5e5082fa13d3a21954794235f8e92344e5327a'
def xdelta(src,dst,patch):
    run([XD,'-e','-f','-9','-B','2147483648','-s',src,dst,patch])
    check=patch.with_suffix('.check')
    run([XD,'-d','-f','-s',src,patch,check]);assert sha(check)==sha(dst),patch;check.unlink()
def main():
    assert not OUT.exists(),f'{OUT} exists; remove it first'
    (OUT/'patches').mkdir(parents=True);(OUT/'tools').mkdir()
    base=read(ROOT/'translation/localized_base_cxi.generated.json')
    assert base['original_rom_sha256']==BASE_3DS_SHA
    work=Path(base['file']).parent;orig=work/'original.cxi';loc=Path(base['file'])
    assert sha(loc)==base['sha256']
    # manual partition, needed to build the base CIA
    manual=OUT/'patches/_manual_probe.cfa';run([TOOL,'-xtf','cci',base['original_rom'],'--partition1',manual])
    manual_sha=sha(manual);manual.unlink()
    xdelta(orig,loc,OUT/'patches/base.xdelta')
    m=dict(revision=589,
        base=dict(rom_sha256=BASE_3DS_SHA,partition0_sha256=sha(orig),manual_sha256=manual_sha,localized_sha256=base['sha256'],
                  patch='base.xdelta',version=16),
        update=dict(title_id='0004000e000c3600',version=2096,contents=[]),
        dlc=dict(title_id='0004008c000c3600',version=0,contents=[]))
    for scope,report in [('update','localized_update_cia'),('dlc','localized_dlc_cia')]:
        r=read(ROOT/f'translation/{report}.generated.json')
        for c in r['contents']:
            kind='cxi' if scope=='update' and c['index']=='0000' else 'cfa'
            dec=ROOT/'cia_rebuild'/scope/c['index']/('decrypted.'+kind)
            row=dict(index=c['index'],content_id=c['content_id'],kind=kind,encrypted_sha256=c['original_sha256'],decrypted_sha256=sha(dec),final_sha256=c['sha256'],patch=None)
            if c['localized']:
                row['patch']=f'{scope}_{c["index"]}.xdelta';xdelta(dec,Path(c['file']),OUT/'patches'/row['patch'])
            else:assert row['decrypted_sha256']==c['sha256']
            m[scope]['contents'].append(row)
    (OUT/'patches/manifest.json').write_text(json.dumps(m,indent=1),encoding='utf-8')
    for exe in [CTR,TOOL,MAKER,XD]:shutil.copy2(exe,OUT/'tools'/Path(exe).name)
    shutil.copy2(KIT/'patch.ps1',OUT/'tools/patch.ps1')
    for f in KIT.iterdir():
        if f.name!='patch.ps1':shutil.copy2(f,OUT/f.name)
    total=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
    print('Patch kit',OUT,'size MB',round(total/2**20,1))
    for p in sorted((OUT/'patches').iterdir()):print(' ',p.name,p.stat().st_size)
if __name__=='__main__':main()
