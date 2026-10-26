"""Execute original PQ1 ARM candidate routine with generated dictionary.

This is a function-level emulator test, not an emulator/gameplay/save test.
"""
import json
import struct
import sys
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent/'tools/ime_python_deps'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_ARM
from unicorn.arm_const import UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC


def query(spelling, executable='exefs/code.bin'):
    uc = Uc(UC_ARCH_ARM, UC_MODE_ARM)
    uc.mem_map(0x100000, 0x1800000)
    code=(ROOT/executable).read_bytes()
    uc.mem_write(0x100000, code)
    def word(p,v):
        uc.mem_write(p,struct.pack('<I',v))
    signature=bytes.fromhex('f05f2de9f6de4de20070a0e30740a0e1')
    assert code.count(signature)==1
    function=code.index(signature)
    state, slots=struct.unpack_from('<II',code,function+0x278)
    inp=''.join(chr(ord(c)+0xfee0) for c in spelling).encode('cp932')
    uc.mem_write(0x900000,inp+b'\0')
    for off,val in [(0x14,0x901000),(0x18,0x902000),(0x2c,0x900000),(0x30,len(inp)),(0x3c,0x903000),(0x40,0x904000)]:
        word(state+off,val)
    uc.mem_write(state,b'\0\0\0\0')
    uc.mem_write(0x903000,(ROOT/'translation/ime_538/pinyin_idx.tbl').read_bytes())
    data=(ROOT/'translation/ime_538/pinyin_dat.txt').read_bytes()
    uc.mem_write(0xa00000,data)
    uc.mem_write(0x904000,struct.pack('<III',0xa00000,0,len(data)))
    for n in range(80):
        word(slots+n*4,0x910000+n*0x40)
    uc.reg_write(UC_ARM_REG_SP,0x1700000)
    uc.reg_write(UC_ARM_REG_LR,0x1800000)
    try:
        uc.emu_start(function+0x100000,0x1800000,count=2000000)
    except Exception:
        print('Failure PC:',hex(uc.reg_read(UC_ARM_REG_PC)))
        raise
    assert uc.reg_read(UC_ARM_REG_PC)==0x1800000, 'instruction budget exceeded'
    count=struct.unpack('<I',uc.mem_read(state+0x38,4))[0]
    assert count <= 80
    return [bytes(uc.mem_read(0x910000+n*0x40,0x30)).split(b'\0')[0] for n in range(count)]


if __name__ == '__main__':
    mapping=json.loads((ROOT/'translation/font_encoding.hex.json').read_text(encoding='utf-8'))
    reverse={bytes.fromhex(v):k for k,v in mapping.items()}
    expected=json.loads((ROOT/'translation/ime_538/candidates.json').read_text(encoding='utf-8'))
    cases=['ni','NI','nI','hao','zhong','ZhOnG','lv','nv','han','zzzz','']
    if '--all' in sys.argv:
        cases += list(expected)
    tested=[]
    for executable in ['exefs/code.bin','update/exefs/code.bin']:
        for spelling in cases:
            results=query(spelling,executable)
            chinese=[reverse.get(c,c.decode('cp932',errors='replace')) for c in results[2:]]
            assert chinese==expected.get(spelling.lower(),[]),(executable,spelling,chinese)
        tested.append(dict(executable=executable,sha256=hashlib.sha256((ROOT/executable).read_bytes()).hexdigest(),cases=len(cases)))
        print(executable, len(cases), 'passed')
    hashes={n:hashlib.sha256((ROOT/'translation/ime_538'/n).read_bytes()).hexdigest() for n in ['pinyin_idx.tbl','pinyin_dat.txt','candidates.json']}
    (ROOT/'translation/ime_538/native_test.json').write_text(json.dumps(dict(results=tested,hashes=hashes,gameplay_verified=False,save_roundtrip_verified=False),indent=2),encoding='utf-8')
    print('Native ARM query tests passed. Not a gameplay validation.')
