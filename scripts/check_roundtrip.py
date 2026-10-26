"""Compare PQ new-style BIN members without normalizing their payloads."""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent
def members(path):
    return parse_members(path.read_bytes())

def parse_members(data, allow_padding=False):
    assert len(data) >= 4
    count = struct.unpack_from('<I', data)[0]
    assert 0 < count < 10000
    pos = 4
    result = []
    for _ in range(count):
        assert pos + 36 <= len(data)
        name = data[pos:pos+32].rstrip(b'\0').decode('ascii')
        size = struct.unpack_from('<I', data, pos+32)[0]
        payload = data[pos+36:pos+36+size]
        assert len(payload) == size
        result.append((name, payload))
        pos += 36 + size
    trailer = data[pos:]
    # Packed GSDs can carry short alignment tails copied from their own header.
    valid_tail = not any(trailer) or (len(trailer) < 32 and trailer == data[:len(trailer)])
    assert pos == len(data) or (allow_padding and pos < len(data) and valid_tail)
    return result

def main():
    old = members(ROOT/'test_input/difficultyselect.bin')
    new = members(ROOT/'test_text_roundtrip/difficultyselect.bin')
    assert [n for n,_ in old] == [n for n,_ in new]
    report = []
    for (name, a), (_, b) in zip(old,new):
        report.append(dict(name=name, original_size=len(a), rebuilt_size=len(b),
            identical=a==b, same_without_trailing_zeros=a.rstrip(b'\0')==b.rstrip(b'\0'),
            original_sha256=hashlib.sha256(a).hexdigest(), rebuilt_sha256=hashlib.sha256(b).hexdigest()))
    (ROOT/'roundtrip_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    for item in report:
        print(item['name'], item['original_size'], item['rebuilt_size'], 'identical:',item['identical'])

if __name__ == '__main__':
    main()
