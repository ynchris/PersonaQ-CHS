"""Build an isolated update CIA; preserve its version, manual and non-code data."""
import shutil
import tempfile
from pathlib import Path
from make_decrypted_cias import ROOT, CTR, TOOL, MAKER, run, sha
from compile_translation import read, write


def inventory(folder):
    return {p.relative_to(folder).as_posix(): sha(p) for p in folder.rglob('*') if p.is_file()}


def main():
    assembly = ROOT/'translation/integrated_build.generated.json'
    assembly_hash = sha(assembly)
    manifest = read(assembly)
    assert manifest['encoding_sha256'] == sha(ROOT/'translation/font_encoding.hex.json')
    code = next(r for r in manifest['executable_resources'] if r['scope'] == 'update')
    assert sha(ROOT/code['output']) == code['sha256']
    assert sha(ROOT/code['source']) == code['source_sha256']
    work = Path(tempfile.mkdtemp(prefix='localized_update_', dir=ROOT/'full_work'))
    original = ROOT/'cia_rebuild/update/0000'
    # Let the existing ExeFS header govern order and compressed-code flags.
    header = work/'exefs_header.bin'
    unpacked = work/'exefs_original'
    run([TOOL, '-xtfu', 'exefs', original/'exefs.bin', '--header', header, '--exefs-dir', unpacked])
    expected = inventory(unpacked)
    assert expected['code.bin'] == code['source_sha256']
    patched = work/'exefs_patched'
    shutil.copytree(unpacked, patched)
    shutil.copy2(ROOT/code['output'], patched/'code.bin')
    expected['code.bin'] = code['sha256']
    assert inventory(patched) == expected
    exefs = work/'exefs.bin'
    run([TOOL, '-ctfz', 'exefs', exefs, '--header', header, '--exefs-dir', patched])
    run([TOOL, '-xtfu', 'exefs', exefs, '--exefs-dir', work/'exefs_checked'])
    assert inventory(work/'exefs_checked') == expected
    cxi = work/'localized.cxi'
    args = [TOOL, '-ctf', 'cxi', cxi, '--header', original/'header.bin', '--not-encrypt', '--exefs', exefs]
    sections = ['romfs', 'exh', 'logo', 'plain']
    for section in sections:
        args += ['--'+section, original/(section+'.bin')]
    run(args)
    assert 'Crypto Key           None' in run([CTR, cxi])
    checked = work/'sections_checked'
    checked.mkdir()
    args = [TOOL, '-xtf', 'cxi', cxi, '--exefs', checked/'exefs.bin']
    for section in sections:
        args += ['--'+section, checked/(section+'.bin')]
    run(args)
    assert sha(checked/'exefs.bin') == sha(exefs)
    for section in sections:
        assert sha(checked/(section+'.bin')) == sha(original/(section+'.bin'))
    contents = []
    content_args = []
    for source in sorted((ROOT/'update').glob('cia_contents.*')):
        _, index, cid = source.name.split('.')
        baseline = ROOT/'cia_rebuild/update'/index/('decrypted.cxi' if index == '0000' else 'decrypted.cfa')
        payload = cxi if index == '0000' else baseline
        contents.append(dict(index=index, content_id=cid, file=str(payload), sha256=sha(payload), original_sha256=sha(source), localized=index=='0000'))
        content_args += ['-content', f'{payload}:{int(index,16)}:{int(cid,16)}']
    assert [r['index'] for r in contents] == ['0000', '0001']
    output = work/'PQ1_JPN_UPDATE_CHS_INTERNAL.cia'
    run([MAKER, '-f', 'cia', '-o', output, '-ver', '2096', '-ignoresign']+content_args)
    info = run([CTR, output])
    assert '0004000e000c3600' in info.lower() and '(2096)' in info
    assert 'Encrypted:   YES' not in info
    prefix = work/'cia_recheck'
    run([CTR, '-q', f'--contents={prefix}', output])
    for row in contents:
        assert sha(Path(f'{prefix}.{row["index"]}.{row["content_id"]}')) == row['sha256']
        assert sha(ROOT/'update'/f'cia_contents.{row["index"]}.{row["content_id"]}') == row['original_sha256']
    assert sha(assembly) == assembly_hash
    write(ROOT/'translation/localized_update_cia.generated.json', dict(
        status='INCOMPLETE_INTERNAL_DRAFT_NOT_A_RELEASE', file=str(output), sha256=sha(output),
        title_id='0004000e000c3600', version=2096, contents=contents,
        integrated_manifest_sha256=assembly_hash, encoding_sha256=manifest['encoding_sha256'],
        code_sha256=code['sha256'], exefs_inventory=expected,
        cia_content_roundtrip_verified=True, code_decompression_roundtrip_verified=True,
        non_code_exefs_preserved=True, other_sections_preserved=True,
        original_cias_modified=False, installed=False, runtime_tested=False))
    print('Verified internal update CIA:', output)


if __name__ == '__main__':
    main()
