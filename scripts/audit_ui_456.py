"""Read-only resource discovery. Writes inventories, never game payloads."""
import hashlib
import re
from collections import Counter
from compile_translation import ROOT, read, write
from prepare_system_455 import PREFIX

CONTROLS = {bytes.fromhex(s) for s in ['f2010301','f2010201','f2010101','f2440101']}

def text_with_controls(data):
    parts=[]; literal=bytearray(); i=0
    def flush():
        if literal:
            parts.append(bytes(literal).decode('cp932')); literal.clear()
    while i<len(data):
        if data[i:i+4] in CONTROLS:
            flush(); parts.append('{'+data[i:i+4].hex(' ').upper()+'}'); i+=4
        else:
            n=2 if 0x81<=data[i]<=0x9f or 0xe0<=data[i]<=0xfc else 1
            literal.extend(data[i:i+n]); i+=n
    flush()
    result=''.join(parts)
    assert not any(ord(c)<32 and c not in '\n\r\t' for c in result)
    return result

def main():
    review=read(ROOT/'translation/system_455.review.json')
    files=[]
    for f in review['files']:
        raw=(ROOT/f['source']).read_bytes(); done={r['offset']:r for r in f['rows']}
        rows=[]
        for m in re.finditer(re.escape(PREFIX),raw):
            start=m.end(); end=raw.index(0,start); data=raw[start:end]
            text=text_with_controls(data)
            rows.append(dict(offset=start,capacity_bytes=len(data),original=text,original_hex=data.hex(),
                             translation=done.get(start,{}).get('translation'),
                             status='reviewed_455' if start in done else 'pending_translation'))
        files.append(dict(source=f['source'],sha256=hashlib.sha256(raw).hexdigest(),rows=rows))
    write(ROOT/'translation/system_inventory_456.generated.json',dict(files=files,
          scope='Every exact F2 05 FF FF F1 41 prefixed NUL-terminated dialog in both executables, not every possible game string.'))
    inv=read(ROOT/'translation/image_inventory.generated.json')
    groups={'title','init','memcard','camp','tutorial','mapdat','facility','gamecoin','photo'}
    images=[r for r in inv['rows'] if r['source'].split('/')[1] in groups or '.spr3.' in r['source']]
    # Include every exported table, not only tables accepted by the old parser.
    tables=[p.relative_to(ROOT).as_posix() for p in (ROOT/'export_base').rglob('*') if p.suffix.lower() in {'.ctd','.ftd','.qtd'}]
    anchors=['どちらの物語を体験しますか？','カーソル位置記憶','時間','セーブ','戻る','再生','キャラ切替','キーアイテム','権利者','ご注意','追加コンテンツを確認しています。']
    hits=[]
    targets=[ROOT/'exefs/code.bin',ROOT/'update/exefs/code.bin']
    for group in groups|{'event'}:
        targets.extend(p for p in (ROOT/'data'/group).rglob('*') if p.is_file() and p.suffix.lower() in {'.spr3','.ctpk','.bin','.ctd'})
    for p in sorted(set(targets)):
        raw=p.read_bytes()
        for term in anchors:
            for enc in ['cp932','utf-16-le','utf-8']:
                needle=term.encode(enc); pos=raw.find(needle)
                if pos>=0:
                    hits.append(dict(source=p.relative_to(ROOT).as_posix(),term=term,encoding=enc,offset=pos,
                                     caveat='May be sprite metadata, not displayed text; first occurrence only.'))
    write(ROOT/'translation/ui_inventory_456.generated.json',dict(images=images,tables=sorted(tables),anchor_hits=hits,
        image_groups=dict(Counter(r['source'].split('/')[1] for r in images)),
        coverage_complete=False,notes=['Candidate inventory, NOT translated or visually reviewed coverage.',
        'Includes all exported tutorials and selected UI groups/sprite sheets. Unexported/embedded/system resources may remain.',
        'No ROM, executable or texture modifications. Pinyin input remains pending after core localization.']))
    print('Dialog counts:',[(f['source'],len(f['rows'])) for f in files])
    print('UI candidate textures:',len(images),'tables:',len(tables),'anchor hits:',len(hits))

if __name__=='__main__':main()
