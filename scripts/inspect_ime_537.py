"""Read-only ARM/iWnn discovery. No executable patches."""
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / 'tools/ime_python_deps'))
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM

dis = Cs(CS_ARCH_ARM, CS_MODE_ARM)
dis.skipdata = True
for rel in ['exefs/code.bin', 'update/exefs/code.bin']:
    if len(sys.argv) > 1 and rel.startswith('update/'):
        continue
    raw = (ROOT / rel).read_bytes()
    print(rel)
    if len(sys.argv) > 1 and sys.argv[1] == 'keyboard':
        out = ROOT / 'translation/ime_537'
        out.mkdir(exist_ok=True)
        lines = [f'{i.address:08x} {i.mnemonic:8} {i.op_str}' for i in dis.disasm(raw[0x5e000:0x84000], 0x15e000)]
        (out / 'keyboard_base.disasm.txt').write_text('\n'.join(lines), encoding='utf-8')
        print('Saved keyboard-range disassembly.')
        continue
    for m in re.finditer(rb'[ -~]{5,}', raw):
        if any(t in m.group().lower() for t in [b'njub', b'iwnn', b'dic/', b'njps', b'njuser']):
            print(hex(m.start()+0x100000), m.group().decode('ascii'))
    if len(sys.argv) > 1:
        start = int(sys.argv[1], 16)
        length = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0x200
        for ins in dis.disasm(raw[start-0x100000:start-0x100000+length], start):
            print(f'{ins.address:08x} {ins.mnemonic:8} {ins.op_str}')
    else:
        hits = [m.start() for m in re.finditer(re.escape(bytes.fromhex('30209fe5')), raw) if m.start()%4 == 0]
        print('candidate prologue literal matches:', [hex(p+0x100000) for p in hits])
