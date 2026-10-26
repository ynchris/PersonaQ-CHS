"""Selective native-dictionary overlay. No CPK/CXI/CIA creation or deployment.

patch_archive can also consume a later translated archive: it replaces only
the two dictionary members, preserving all other members byte-for-byte.
"""
import hashlib
import json
import struct
from pathlib import Path
from check_roundtrip import parse_members

ROOT=Path(__file__).resolve().parent
IME=ROOT/'translation/ime_538'
TARGETS={'nameentry.arc':'namedict', 'mapmemo.arc':'mapdict',
         'notebookname.arc':'noteNamedict', 'notebookword.arc':'noteWorddict'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def patch_archive(raw, prefix, index, data):
    members=parse_members(raw)
    replacement={prefix+'_idx.tbl':index,prefix+'_dat.txt':data}
    assert set(replacement).issubset(dict(members))
    output=bytearray(struct.pack('<I',len(members)))
    for name, original in members:
        blob=replacement.get(name,original)
        output += name.encode('ascii').ljust(32,b'\0')+struct.pack('<I',len(blob))+blob
    reread=parse_members(bytes(output))
    assert [n for n,_ in members]==[n for n,_ in reread]
    for (name, before),(_,after) in zip(members,reread):
        assert after == replacement.get(name,before)
    return bytes(output)


def main():
    build=json.loads((IME/'build.json').read_text(encoding='utf-8'))
    tests=json.loads((IME/'native_test.json').read_text(encoding='utf-8'))
    assert build['font_map_sha256']==sha((ROOT/'translation/font_encoding.hex.json').read_bytes())
    for name, expected in build['dictionaries'].items():
        assert expected==tests['hashes'][name]==sha((IME/name).read_bytes())
    for entry in tests['results']:
        assert entry['cases']>=build['readings']
        assert entry['sha256']==sha((ROOT/entry['executable']).read_bytes())
    index=(IME/'pinyin_idx.tbl').read_bytes()
    data=(IME/'pinyin_dat.txt').read_bytes()
    dest=ROOT/'translation/ime_539'
    rows=[]
    for filename,prefix in TARGETS.items():
        source=ROOT/'data/init'/filename
        original=source.read_bytes()
        result=patch_archive(original,prefix,index,data)
        target=dest/'resources/init'/filename
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(result)
        # Idempotent overlay, including when other members were translated.
        assert patch_archive(result,prefix,index,data)==result
        assert source.read_bytes()==original
        rows.append(dict(source=str(source.relative_to(ROOT)),source_sha256=sha(original),
                         staged=str(target.relative_to(ROOT)),staged_sha256=sha(result),
                         changed_members=[prefix+'_idx.tbl',prefix+'_dat.txt'],other_members_preserved=True))
    report=dict(status='staged_not_deployed',files=rows,encoding_sha256=build['font_map_sha256'],
                native_tests=tests,images_modified=False,code_modified=False,
                final_package_generated=False,gameplay_verified=False,
                integration_rule='Apply patch_archive to latest translated archives; do not overwrite them with these original-based test archives.')
    (dest/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Staged four input archives; only eight dictionary members changed. No image, code, CPK, CXI or CIA changes.')


if __name__=='__main__':
    main()
