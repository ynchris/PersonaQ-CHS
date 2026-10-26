"""Read-only verification of the approved image selection; never repack."""
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
selection = json.loads((ROOT / 'translation/image_selection_515.json').read_text(encoding='utf-8'))
for row in selection['files']:
    for path_key, hash_key in [('png', 'sha256'), ('source', 'original_sha256')]:
        path = ROOT / row[path_key]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row[hash_key], str(path)
    with Image.open(ROOT / row['png']) as im:
        assert list(im.size) == row['size'], row['png']
        assert im.mode == 'RGBA', row['png']
assert len(selection['files']) == selection['count']
print(f"Verified {selection['count']} approved PNGs: hashes, source hashes, dimensions, RGBA. No encoding or packaging.")
