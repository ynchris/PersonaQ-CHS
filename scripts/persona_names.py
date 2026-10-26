"""PQ1 cumulative-u16 Persona name bank, isolated from gameplay parameter tables."""
import hashlib
import re
import struct
from compile_translation import ROOT, read, write
from raw_text_codec import encode_display, decode_display

SOURCE = 'battle/table/personanametable.tbl'
EXPECTED_SHA = 'b2d20fe23676bba8fd6ec12126ec3a287bcb3360b2e10b87f6c51b9648d5ed7a'
DRAFT = ROOT/'translation/persona_names.review.json'


def parse(data):
    if len(data) < 2:
        raise ValueError('Truncated count')
    count = struct.unpack_from('<H', data)[0]
    start = 2 + count * 2
    if count != 288 or len(data) < start:
        raise ValueError('Unexpected Persona name count/header')
    offsets = [0] + list(struct.unpack_from('<288H', data, 2))
    if start + offsets[-1] != len(data):
        raise ValueError('Unexpected name bank end')
    rows = []
    for a, b in zip(offsets, offsets[1:]):
        row = data[start+a:start+b]
        if b <= a or not row.endswith(b'\0') or b'\0' in row[:-1]:
            raise ValueError('Invalid name span or terminator')
        rows.append(row)
    return rows


def is_placeholder(name):
    return name in {'ＢＬＡＮＫ', 'リザーブ'} or re.fullmatch(r'0x[0-9A-Fa-f]+', name)


def load_drafts():
    data = (ROOT/'data'/SOURCE).read_bytes()
    if hashlib.sha256(data).hexdigest() != EXPECTED_SHA:
        raise ValueError('Source Persona name table changed')
    names = [r[:-1].decode('cp932') for r in parse(data)]
    draft = read(DRAFT)
    if draft['source'] != SOURCE or draft['source_sha256'] != EXPECTED_SHA:
        raise ValueError('Wrong Persona name source')
    rows = {}
    for r in draft['entries']:
        i, value = r['index'], r['translation']
        if not isinstance(i, int) or not 0 <= i < len(names) or i in rows:
            raise ValueError('Invalid/duplicate Persona name index')
        if names[i] != r['original'] or is_placeholder(names[i]):
            raise ValueError('Changed original or selected placeholder')
        if not value or re.search(r'[\x00\r\n{}\u3041-\u3096\u30a1-\u30fa]', value):
            raise ValueError('Invalid Persona name')
        rows[i] = value
    if set(rows) != {i for i, n in enumerate(names) if not is_placeholder(n)}:
        raise ValueError('Incomplete Persona name bank')
    return data, names, rows


def build(data, rows, mapping):
    original = parse(data)
    if any(not isinstance(i, int) or not 0 <= i < len(original) for i in rows):
        raise ValueError('Name index out of range')
    chunks = list(original)
    for i, value in rows.items():
        encoded = encode_display(value, mapping)
        if b'\0' in encoded or not encoded:
            raise ValueError('Embedded NUL or empty name')
        chunks[i] = encoded + b'\0'
    ends, total = [], 0
    for chunk in chunks:
        total += len(chunk)
        if total > 65535:
            raise ValueError('u16 name-bank overflow')
        ends.append(total)
    result = struct.pack('<H', len(chunks)) + struct.pack('<288H', *ends) + b''.join(chunks)
    decoded = parse(result)
    for i, chunk in enumerate(decoded):
        if i in rows:
            if decode_display(chunk[:-1], mapping) != rows[i]:
                raise ValueError('Name roundtrip failed')
        elif chunk != original[i]:
            raise ValueError('Unselected name changed')
    return result


def main():
    data, names, rows = load_drafts()
    encoding_path = ROOT/'translation/font_encoding.hex.json'
    result = build(data, rows, read(encoding_path))
    target = ROOT/'full_work/persona_payload'/SOURCE
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(result)
    write(ROOT/'translation/persona_names_build.generated.json', {
        'source': SOURCE, 'source_sha256': EXPECTED_SHA,
        'sha256': hashlib.sha256(result).hexdigest(),
        'encoding_sha256': hashlib.sha256(encoding_path.read_bytes()).hexdigest(),
        'draft_sha256': hashlib.sha256(DRAFT.read_bytes()).hexdigest(),
        'draft_rows': len(rows), 'changed_rows': sum(names[i] != t for i, t in rows.items()),
        'total_slots': len(names), 'placeholder_slots': len(names)-len(rows),
        'roundtrip_verified': True, 'unselected_names_preserved': True,
        'parameter_tables_touched': False, 'runtime_tested': False})
    print(f'Persona names: {len(rows)} non-placeholder slots; binary roundtrip verified; runtime not tested.')


if __name__ == '__main__':
    main()
