"""PQ1 itemtbl fixed name bank; never modify its numeric item records."""
import hashlib
import json
import re
import struct
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE='init/itemtbl.bin'
EXPECTED_SHA='00c9c1a43f35d527d3607d29724432c04300c7ac577d2bf51a4431d109d98b47'

def parse(data):
    count=struct.unpack_from('<I',data)[0]
    if count!=3328:
        raise ValueError('Unexpected item count')
    second=16+count*104
    if data[:16]!=data[second:second+16] or len(data)!=32+count*126:
        raise ValueError('Unexpected item bank layout')
    start=second+16
    names=[]
    for i in range(count):
        row=data[start+i*22:start+(i+1)*22]
        end=row.find(b'\0')
        if end<0 or any(row[end:]):
            raise ValueError(f'Invalid name padding: {i}')
        names.append(row[:end].decode('cp932',errors='strict'))
    return start,names

def load_drafts():
    data=(ROOT/'data'/SOURCE).read_bytes()
    if hashlib.sha256(data).hexdigest()!=EXPECTED_SHA:
        raise ValueError('Source item table changed')
    start,names=parse(data)
    rows={}
    for path in sorted((ROOT/'translation/equipment_names').glob('*.json')):
        batch=json.loads(path.read_text(encoding='utf-8'))
        if batch['source']!=SOURCE or batch['source_sha256']!=EXPECTED_SHA:
            raise ValueError('Wrong equipment source')
        for index,text in batch['rows']:
            if index in rows or not 0<=index<1280:
                raise ValueError(f'Duplicate/out of scope index: {index}')
            if not text or any(c in text for c in '\0\r\n{}'):
                raise ValueError('Invalid equipment name')
            if re.fullmatch(r'0x[0-9A-Fa-f]+',names[index]) or 'ダミー' in names[index] or names[index]=='リザーブ':
                raise ValueError(f'Placeholder selected: {index}')
            rows[index]=text
    return data,start,names,rows

def build(data,start,rows,mapping):
    from raw_text_codec import encode_display,decode_display
    result=bytearray(data)
    allowed=set()
    for index,text in rows.items():
        encoded=encode_display(text,mapping)
        if len(encoded)>=22:
            raise ValueError(f'Equipment name overflow: {index}: {len(encoded)}')
        pos=start+index*22
        result[pos:pos+22]=encoded.ljust(22,b'\0')
        allowed.update(range(pos,pos+22))
        if decode_display(bytes(result[pos:pos+22]).rstrip(b'\0'),mapping)!=text:
            raise ValueError('Equipment name roundtrip failed')
    if len(data)!=len(result) or any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(data,result))):
        raise ValueError('Non-name data changed')
    return bytes(result)

def main():
    data,start,names,rows=load_drafts()
    from q2_item_names import load as load_extra
    extra=load_extra()
    equipment_count=len(rows)
    rows={**rows,**extra}
    encoding_path=ROOT/'translation/font_encoding.hex.json'
    mapping=json.loads(encoding_path.read_text(encoding='utf-8'))
    result=build(data,start,rows,mapping)
    target=ROOT/'full_work/equipment_payload'/SOURCE
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(result)
    report=dict(source=SOURCE,source_sha256=EXPECTED_SHA,sha256=hashlib.sha256(result).hexdigest(),encoding_sha256=hashlib.sha256(encoding_path.read_bytes()).hexdigest(),draft_rows=len(rows),name_bank_offset=start,capacity_bytes=22,numeric_records_preserved=True,outside_text_bytes_preserved=True,roundtrip_verified=True,runtime_tested=False,draft_sha256=hashlib.sha256(json.dumps(rows,sort_keys=True,ensure_ascii=False).encode('utf-8')).hexdigest())
    report.update(equipment_rows=equipment_count,extra_item_rows=len(extra))
    (ROOT/'translation/equipment_build.generated.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Equipment names: {len(rows)} rows roundtrip verified; numeric records unchanged; runtime not tested.')

if __name__=='__main__':
    main()
