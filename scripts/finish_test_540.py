"""Verify one coherent test build and copy three installers to a clear folder."""
import hashlib
import json
import shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DEST=ROOT/'PQ1_CHS_TEST_540'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    manifest_path=ROOT/'translation/integrated_build.generated.json'
    manifest=read(manifest_path);mh=sha(manifest_path)
    assert manifest['test_revision']==540 and manifest['pinyin_input_archives']==4
    assert manifest['encoding_sha256']==sha(ROOT/'translation/font_encoding.hex.json')
    entries=[('localized_base_cxi.generated.json','PQ1_CHS_TEST_540.cxi','00040000000c3600'),
             ('localized_update_cia.generated.json','PQ1_UPDATE_CHS_TEST_540.cia','0004000e000c3600'),
             ('localized_dlc_cia.generated.json','PQ1_DLC_CHS_TEST_540.cia','0004008c000c3600')]
    rows=[]
    DEST.mkdir(exist_ok=True)
    for report,name,title in entries:
        d=read(ROOT/'translation'/report);p=Path(d['file'])
        assert d['integrated_manifest_sha256']==mh
        assert d['title_id']==title and sha(p)==d['sha256']
        if title.startswith('00040000'):
            assert d['exefs_roundtrip_verified'] and d['romfs_inventory_verified'] and d['cxi_sections_verified']
            assert d['code_sha256']==next(x['sha256'] for x in manifest['executable_resources'] if x['scope']=='base')
        else:
            assert d['cia_content_roundtrip_verified']
            if 'code_sha256' in d:assert d['code_sha256']==next(x['sha256'] for x in manifest['executable_resources'] if x['scope']=='update')
        target=DEST/name
        if target.exists():assert sha(target)==d['sha256'],'Refuse overwriting unrelated test package'
        else:shutil.copy2(p,target)
        assert sha(target)==d['sha256']
        rows.append(dict(file=str(target),sha256=d['sha256'],bytes=target.stat().st_size,title_id=title))
    shutil.copy2(ROOT/'translation/font_encoding.hex.json',DEST/'font_encoding.hex.json')
    result=dict(revision=540,files=rows,integrated_manifest_sha256=mh,gameplay_tested=False,
                includes=['Current compiled text','68 approved CTPK textures and one TMX','Base/update system and menu strings','Native pinyin dictionaries in four input archives'],
                pending=['Seneca opening quotation','Gameplay pinyin, save roundtrip and layout tests'])
    (DEST/'build.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(rows,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
