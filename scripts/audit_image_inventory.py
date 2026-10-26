"""Inventory exported textures without changing pixels or guessing translations."""
import hashlib
import struct
from collections import Counter, defaultdict
from compile_translation import ROOT, write


def main():
    rows = []
    duplicates = defaultdict(list)
    for folder in ['export_base', 'export_dlc']:
        for path in sorted((ROOT/folder).rglob('*.png')):
            data = path.read_bytes()
            assert data[:8] == b'\x89PNG\r\n\x1a\n' and data[12:16] == b'IHDR', path
            width, height = struct.unpack_from('>II', data, 16)
            digest = hashlib.sha256(data).hexdigest()
            rel = path.relative_to(ROOT).as_posix()
            duplicates[digest].append(rel)
            rows.append(dict(source=rel, sha256=digest, width=width, height=height,
                             status='unreviewed_texture_not_necessarily_text'))
    write(ROOT/'translation/image_inventory.generated.json', dict(
        exported_images=len(rows), unique_png_files=len(duplicates),
        groups=dict(Counter('/'.join(r['source'].split('/')[:2]) for r in rows)),
        rows=rows, exact_duplicate_groups=[dict(sha256=k, sources=v) for k,v in duplicates.items() if len(v)>1],
        notes=['Only already exported PNGs are inventoried; this does not prove all game textures were exported.',
               'No OCR, translation, texture replacement or runtime verification has been performed.',
               'Exact duplicates may share future reviewed edits; do not copy Q2 textures based only on filenames.']))
    print('Exported PNG inventory:', len(rows), 'files;', len(duplicates), 'unique hashes')
    print(dict(Counter('/'.join(r['source'].split('/')[:2]) for r in rows)))


if __name__ == '__main__':
    main()
