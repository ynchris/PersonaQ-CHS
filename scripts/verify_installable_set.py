"""Bind the local base resource and both CIA copies; no installation occurs."""
from pathlib import Path
from compile_translation import ROOT, read, write
from pack_dlc_draft import sha
from message_snapshot import scope_snapshot


def main():
    manifest = ROOT/'translation/integrated_build.generated.json'
    manifest_hash = sha(manifest)
    snapshots=read(manifest).get('message_input_snapshots',{})
    assert set(snapshots)=={'base','0005','0006','0007','0008','0009'}, 'Legacy set has no exact text snapshots; rebuild before claiming current'
    for scope,digest in snapshots.items():
        assert digest==scope_snapshot(scope), f'Current {scope} translations differ from packaged snapshot'
    packaged = read(ROOT/'translation/packaged_set.generated.json')
    update = read(ROOT/'translation/localized_update_cia.generated.json')
    dlc = read(ROOT/'translation/localized_dlc_cia.generated.json')
    base = read(ROOT/'translation/base_cpk.generated.json')
    base_cxi=read(ROOT/'translation/localized_base_cxi.generated.json')
    assert base_cxi['title_id']=='00040000000c3600'
    assert base_cxi['base_cpk_sha256']==base['sha256']
    assert base_cxi['encoding_sha256']==packaged['encoding_sha256']
    assert base_cxi['exefs_roundtrip_verified'] and base_cxi['romfs_inventory_verified'] and base_cxi['cxi_sections_verified']
    for report in [packaged, update, dlc, base, base_cxi]:
        assert report['integrated_manifest_sha256'] == manifest_hash, 'Stale mixed build'
    assert sha(ROOT/'translation/font_encoding.hex.json') == packaged['encoding_sha256'] == update['encoding_sha256']
    assert update['title_id'] == '0004000e000c3600' and update['version'] == 2096
    assert dlc['title_id'] == '0004008c000c3600' and dlc['version'] == 0
    assert update['cia_content_roundtrip_verified'] and update['code_decompression_roundtrip_verified']
    assert update['non_code_exefs_preserved'] and update['other_sections_preserved']
    assert dlc['cia_content_roundtrip_verified'] and dlc['localized_romfs_inventory_verified']
    assert base['reextract_verified']
    resources = []
    for kind, report, field in [('base_cpk', base, 'cpk'), ('base_cxi',base_cxi,'file'), ('update_cia', update, 'file'), ('dlc_cia', dlc, 'file')]:
        path = Path(report[field])
        assert sha(path) == report['sha256']
        resources.append(dict(kind=kind, path=str(path), sha256=report['sha256'], bytes=path.stat().st_size))
    for code in packaged['executable_resources']:
        assert sha(ROOT/code['output']) == code['sha256']
        resources.append(dict(kind=code['scope']+'_code', path=str(ROOT/code['output']), sha256=code['sha256'], bytes=code['bytes']))
    assert next(c for c in packaged['executable_resources'] if c['scope']=='update')['sha256'] == update['code_sha256']
    write(ROOT/'translation/installable_set.generated.json', dict(
        status='INCOMPLETE_INTERNAL_DRAFT_NOT_A_RELEASE',
        integrated_manifest_sha256=manifest_hash, encoding_sha256=packaged['encoding_sha256'],
        message_drafts=packaged['message_drafts'], resources=resources,
        offline_pairing_verified=True, runtime_tested=False, installed=False,
        requirements=['Base CPK must be combined with matching fonts already inside it.',
                      'Use update code with the update; base code is only for the no-update configuration.',
                      'CIA copies are local internal artifacts, not a redistribution package.',
                      'Image text, layout and full-game compatibility remain unverified.']))
    print('Verified base/update/DLC local set; NOT installed or runtime tested.')


if __name__ == '__main__':
    main()
