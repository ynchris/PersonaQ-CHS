"""Merge fixed text rows into message payloads without altering other bytes."""
import hashlib
import shutil
import struct
from collections import defaultdict
from compile_translation import ROOT, read, write
from check_roundtrip import members
from raw_text_codec import validate, encode_display, decode_display


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    rows=[r for r in read(ROOT/'translation/tables.catalog.working.json')
          if r['status']=='draft_table_reviewed']
    encoding_path=ROOT/'translation/font_encoding.hex.json'
    encoding=read(encoding_path)
    validate(encoding)
    stage=ROOT/'full_work/integrated_payload'
    message_root=ROOT/'full_work/messages/payload'
    message_report=read(ROOT/'translation/message_build.generated.json')
    assert message_report['encoding_sha256']==digest(encoding_path.read_bytes())
    for item in message_report['files']:
        source=message_root/item['file']
        assert digest(source.read_bytes())==item['sha256']
        target=stage/item['file']
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
    groups=defaultdict(list)
    for row in rows:
        groups[row['source']].append(row)
    report=[]
    for source,items in groups.items():
        original=members(ROOT/'data'/source)
        baseline=message_root/source
        if not baseline.exists():
            baseline=ROOT/'data'/source
        before=members(baseline)
        raw=baseline.read_bytes()
        result=bytearray(raw)
        offsets=[]
        pos=4
        for name,data in before:
            offsets.append(pos+36)
            pos+=36+len(data)
        allowed=set()
        changed_rows=0
        for row in items:
            mi=row['member_index']
            name,old=original[mi]
            assert name==row['member_name']
            assert digest(old)==row['member_sha256'], row['key']
            assert before[mi]==original[mi], 'Table already modified: '+row['key']
            start=row['offset']
            cap=row['capacity_bytes']
            assert old[start:start+cap].rstrip(b'\0').decode('cp932')==row['original']
            encoded=encode_display(row['translation'],encoding)
            assert len(encoded)<cap, f'Text overflow {len(encoded)}/{cap}: {row["key"]}'
            replacement=encoded.ljust(cap,b'\0')
            absolute=offsets[mi]+start
            result[absolute:absolute+cap]=replacement
            allowed.update(range(absolute,absolute+cap))
            changed_rows+=replacement!=old[start:start+cap]
        assert len(result)==len(raw)
        assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,result)))
        output=stage/source
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_bytes(result)
        after=members(output)
        assert [n for n,_ in after]==[n for n,_ in before]
        for row in items:
            data=after[row['member_index']][1]
            encoded=data[row['offset']:row['offset']+row['capacity_bytes']].rstrip(b'\0')
            decoded=decode_display(encoded,encoding)
            assert decoded==row['translation'], row['key']
        report.append({'file':source,'reviewed_rows':len(items),'changed_rows':changed_rows,
                       'sha256':digest(result),'baseline_sha256':digest(raw),
                       'outside_text_bytes_preserved':True,'roundtrip_verified':True})
    write(ROOT/'translation/table_build.generated.json',{
        'reviewed_rows':len(rows),'files':report,'runtime_tested':False,
        'encoding_sha256':digest(encoding_path.read_bytes())})
    print(f'Verified {len(rows)} table rows merged with {len(message_report["files"])} message resources.')


if __name__=='__main__':
    main()
