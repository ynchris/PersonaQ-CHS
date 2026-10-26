"""Verify and deliver three coherent test installers without deleting old ones."""
import hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DEST=ROOT/'PQ1_CHS_TEST_569'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    mp=ROOT/'translation/integrated_build.generated.json';manifest=read(mp);mh=sha(mp)
    assert manifest['test_revision']==569 and manifest['seneca_image_revision']==570
    assert manifest['encoding_sha256']==sha(ROOT/'translation/font_encoding.hex.json')
    entries=[('localized_base_cxi.generated.json','PQ1_CHS_TEST_569.cxi','00040000000c3600'),('localized_update_cia.generated.json','PQ1_UPDATE_CHS_TEST_569.cia','0004000e000c3600'),('localized_dlc_cia.generated.json','PQ1_DLC_CHS_TEST_569.cia','0004008c000c3600')]
    rows=[];DEST.mkdir(exist_ok=True)
    for report,name,title in entries:
        d=read(ROOT/'translation'/report);p=Path(d['file'])
        assert d['integrated_manifest_sha256']==mh and d['title_id']==title and sha(p)==d['sha256']
        if title.startswith('00040000'):
            assert d['exefs_roundtrip_verified'] and d['romfs_inventory_verified'] and d['cxi_sections_verified']
            assert d['code_sha256']==next(r['sha256'] for r in manifest['executable_resources'] if r['scope']=='base')
        else:
            assert d['cia_content_roundtrip_verified']
            if 'code_sha256' in d:assert d['code_sha256']==next(r['sha256'] for r in manifest['executable_resources'] if r['scope']=='update')
        target=DEST/name
        if target.exists():assert sha(target)==d['sha256'],'Refuse overwriting different deliverable'
        else:shutil.copy2(p,target)
        assert sha(target)==d['sha256']
        rows.append(dict(file=str(target),sha256=d['sha256'],bytes=target.stat().st_size,title_id=title))
    shutil.copy2(ROOT/'translation/font_encoding.hex.json',DEST/'font_encoding.hex.json')
    result=dict(revision=569,files=rows,integrated_manifest_sha256=mh,gameplay_tested=False,pinyin_previously_user_tested=True,
        includes=['Latest compiled text and unified names','74 approved CTPK textures and one TMX','Seneca model texture revision 570','Six baseline-calibrated fonts','Base/update UI strings','Unchanged tested pinyin dictionaries'],pending=manifest['pending'])
    (DEST/'build.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(rows,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
