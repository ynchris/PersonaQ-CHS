"""Read-only ARM analysis of opening. All outputs isolated from game payload."""
import json, struct, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'tools/ime_python_deps'))
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM
raw=(ROOT/'exefs/code.bin').read_bytes()
BASE=0x100000
out=ROOT/'translation/opening_trace_566';out.mkdir(exist_ok=True)
dis=Cs(CS_ARCH_ARM,CS_MODE_ARM);dis.skipdata=True
if len(sys.argv)>1 and sys.argv[1]=='table':
    a=0x4c014c
    while a>BASE:
        fn,n=struct.unpack_from('<II',raw,a-BASE-8)
        if not (fn==0 or BASE<=fn<0x450000) or n>32:break
        a-=8
    print('candidate start',hex(a),'fiction index',hex((0x4c014c-a)//8))
    for p in range(a-32,a+40,4):print(hex(p),hex(struct.unpack_from('<I',raw,p-BASE)[0]))
    for off in range(0,len(raw)-3,4):
        w=struct.unpack_from('<I',raw,off)[0]
        if a<=w<=0x4c014c and (w-a)%8==0:print('table base reference',hex(off+BASE),hex(w),'fiction index',hex((0x4c014c-w)//8))
elif len(sys.argv)>1 and sys.argv[1]=='words':
    start=int(sys.argv[2],16);size=int(sys.argv[3],16)
    for a in range(start,start+size,4):
        w=struct.unpack_from('<I',raw,a-BASE)[0]
        print(f'{a:08x} {w:08x}')
elif len(sys.argv)>1 and sys.argv[1]=='refs':
    targets={int(x,16) for x in sys.argv[2:]}
    rows=[]
    for off in range(0,len(raw)-3,4):
        w=struct.unpack_from('<I',raw,off)[0];a=BASE+off
        if w in targets: rows.append(f'{a:08x} pointer {w:08x}')
        if (w&0x0e000000)==0x0a000000:
            delta=(w&0xffffff)<<2
            if delta&0x2000000:delta-=0x4000000
            t=a+8+delta
            if t in targets: rows.append(f'{a:08x} branch {t:08x}')
    print('\n'.join(rows))
    (out/'last_refs.txt').write_text('\n'.join(rows),encoding='utf-8')
elif len(sys.argv)>1:
    start=int(sys.argv[1],16);size=int(sys.argv[2],16)
    lines=[f'{i.address:08x} {i.mnemonic:8} {i.op_str}' for i in dis.disasm(raw[start-BASE:start-BASE+size],start)]
    text='\n'.join(lines)
    (out/f'{start:x}.asm.txt').write_text(text,encoding='utf-8')
    print(text)
else:
    targets=[0x1adfc8,0x1b641c,0x1b6450,0x216da4,0x240934,0x240974]
    refs=[]
    for off in range(0,len(raw)-3,4):
        word=struct.unpack_from('<I',raw,off)[0];addr=BASE+off
        # ARM immediate ADD/SUB with PC operand (ADR pseudo-instruction).
        if (word & 0x0e0f0000)==0x020f0000:
            opcode=(word>>21)&15;rot=((word>>8)&15)*2;imm=word&255
            imm=((imm>>rot)|(imm<<(32-rot)))&0xffffffff if rot else imm
            target=addr+8+imm if opcode==4 else addr+8-imm if opcode==2 else -1
            if target in targets:refs.append(dict(address=hex(addr),kind='ADR',target=hex(target)))
        if word in targets:refs.append(dict(address=hex(addr),kind='pointer',target=hex(word)))
    (out/'refs.json').write_text(json.dumps(refs,indent=2),encoding='utf-8')
    print(json.dumps(refs,indent=2))
