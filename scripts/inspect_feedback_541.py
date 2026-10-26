import struct,json
from compile_translation import ROOT,read,write
from check_roundtrip import parse_members
from raw_text_codec import decode_display
terms=['カーソル位置記憶','リーダースキル','スキル','パーティ','表示切替','戻る']
hits=[]
for p in [ROOT/'exefs/code.bin',ROOT/'update/exefs/code.bin',*sorted((ROOT/'data').rglob('*'))]:
    if not p.is_file():continue
    if p.suffix in ('.usm',):continue
    raw=p.read_bytes()
    for term in terms:
        pos=0;n=term.encode('cp932')
        while True:
            off=raw.find(n,pos)
            if off<0:break
            hits.append(dict(file=p.relative_to(ROOT).as_posix(),term=term,offset=off))
            pos=off+len(n)
write(ROOT/'translation/feedback_541/string_hits.json',hits)
for h in hits:
    if h['term'] not in ('スキル','戻る') or h['file'].endswith('code.bin'):print(h)
mapping=read(ROOT/'translation/font_encoding.hex.json')
p=ROOT/'full_work/integrated_payload/init/cmptable.bin'
raw=dict(parse_members(p.read_bytes()))['cmpConfigItem.ctd']
print('Integrated config row:',decode_display(raw[400:464].rstrip(b'\0'),mapping))
