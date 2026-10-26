"""Check that packaged base and DLC resources match the current assembly."""
from compile_translation import ROOT, read, write
from pack_dlc_draft import sha
from pathlib import Path
from message_snapshot import scope_snapshot

def main():
    manifest_path=ROOT/'translation/integrated_build.generated.json'
    manifest=read(manifest_path)
    snapshots=manifest.get('message_input_snapshots',{})
    assert set(snapshots)=={'base','0005','0006','0007','0008','0009'}, 'Rebuild legacy manifest with exact text snapshots'
    for scope,digest in snapshots.items():
        assert digest==scope_snapshot(scope), f'Stale {scope} text inputs'
    base=read(ROOT/'translation/base_cpk.generated.json')
    for code in manifest['executable_resources']:
        assert sha(ROOT/code['output'])==code['sha256']
        assert sha(ROOT/code['source'])==code['source_sha256']
    assert sha(ROOT/'translation/code_ui_450.review.json')==manifest['executable_review_sha256']
    assert base['reextract_verified']
    assert base['integrated_manifest_sha256']==sha(manifest_path)
    assert sha(Path(base['cpk']))==base['sha256']
    dlc=[]
    for scope in sorted({r['content'] for r in manifest['dlc_resources']}):
        report=read(ROOT/'translation'/f'dlc_{scope}_cpk.generated.json')
        assert report['reextract_verified']
        assert sha(Path(report['cpk']))==report['sha256']
        for resource in manifest['dlc_resources']:
            if resource['content']==scope:
                assert report['resource_sha256'][resource['file']]==resource['sha256']
        dlc.append({'content':scope,'sha256':report['sha256'],'files':report['files']})
    write(ROOT/'translation/packaged_set.generated.json',{
        'status':'INCOMPLETE_INTERNAL_DRAFT_NOT_A_RELEASE',
        'message_drafts':manifest['message_drafts']+manifest['dlc_message_drafts'],
        'base_messages':manifest['message_drafts'],'dlc_messages':manifest['dlc_message_drafts'],
        'executable_resources':manifest['executable_resources'],
        'executable_review_sha256':manifest['executable_review_sha256'],
        'table_reviewed_rows':manifest['table_reviewed_rows'],'fonts':manifest['fonts'],
        'encoding_sha256':manifest['encoding_sha256'],
        'integrated_manifest_sha256':sha(manifest_path),
        'base_cpk_sha256':base['sha256'],'base_files':base['files'],
        'dlc_cpks':dlc,'packaged_resource_hashes_match_current_assembly':True,
        'runtime_tested':False,'update_runtime_verified':False,'dlc_cia_rebuilt':False,
        'deployed':False})
    capacity=read(ROOT/'translation/font_capacity_status.generated.json')
    assert sha(ROOT/'translation/font_encoding.hex.json')==manifest['encoding_sha256']
    capacity['font_build_required']=False
    capacity['font_build_verified']=True
    capacity['encoding_sha256']=manifest['encoding_sha256']
    write(ROOT/'translation/font_capacity_status.generated.json',capacity)
    print(f'Verified integrated draft set: base {base["files"]} files, {len(dlc)} DLC CPKs. Runtime untested.')

if __name__=='__main__':
    main()
