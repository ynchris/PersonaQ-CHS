"""Replace one new-style little-endian BIN member, preserving all other bytes."""
import argparse
import struct
from pathlib import Path
from check_roundtrip import members

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('original', type=Path)
    parser.add_argument('rebuilt', type=Path)
    parser.add_argument('member')
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.output.resolve() in (args.original.resolve(), args.rebuilt.resolve()):
        raise ValueError('Output must be separate from the source files')
    before = members(args.original)
    replacements = [payload for name,payload in members(args.rebuilt) if name == args.member]
    if len(replacements) != 1 or sum(n == args.member for n,_ in before) != 1:
        raise ValueError('Member must exist exactly once in each container')
    source = args.original.read_bytes()
    result = bytearray(source[:4])
    pos = 4
    for name, payload in before:
        header = source[pos:pos+36]
        if name == args.member:
            payload = replacements[0]
            result += header[:32] + struct.pack('<I', len(payload)) + payload
        else:
            result += source[pos:pos+36+len(payload)]
        pos += 36 + len(dict(before)[name])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('xb') as f:
        f.write(result)
    after = members(args.output)
    assert all(a == b for a,b in zip(before,after) if a[0] != args.member)
    print('Verified: all unedited members are byte-identical')

if __name__ == '__main__':
    main()
