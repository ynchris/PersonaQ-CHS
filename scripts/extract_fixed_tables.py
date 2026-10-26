"""Audit fixed-width menu text directly from PQ1 BIN members, including duplicates.

Layouts follow the Q2 reference's documented 0x40 text rows and 0x38 help
rows, with strict PQ1 structural/content checks. Unknown layouts are reported.
"""
import hashlib
import re
import struct
from pathlib import Path
from check_roundtrip import members
from compile_translation import ROOT, write

def inspect(data,name):
    if len(data)<16:
        raise ValueError('short header')
    size,count=struct.unpack_from('<2I',data)
    if not count or count>10000 or size%count or size+16>len(data):
        raise ValueError('not a supported fixed-row header')
    width=size//count
    if width==32:
        left,right=0,0
    elif width==64:
        left,right=0,0
    elif width==44 and name.startswith('fclHelpTable_'):
        left,right=8,4
    elif width==56 and 'fclHelpTable_' in name:
        left,right=20,4
    elif width==56 and 'tutorialConditions' in name:
        left,right=4,4
    else:
        raise ValueError(f'unknown row layout {width}')
    # If a second bank exists, only accept the matching layout recognized by
    # the reference. Never interpret/modify the additional bank as text here.
    if len(data)>size+16:
        tail=data[size+16:]
        short_help_header=(width==44 and name.startswith('fclHelpTable_')
                           and len(tail) in (4,8,12) and tail==data[:len(tail)])
        if not short_help_header and (len(data)<size+32 or struct.unpack_from('<2I',data,size+16)!=(size,count)):
            raise ValueError('unrecognized trailing bank')
    result=[]
    for i in range(count):
        start=16+i*width+left
        capacity=width-left-right
        raw=data[start:start+capacity]
        textbytes=raw.rstrip(b'\0')
        if b'\0' in textbytes:
            raise ValueError('embedded NUL in text region')
        text=textbytes.decode('cp932',errors='strict')
        if any(ord(c)<32 and c not in '\n\r\t' for c in text):
            raise ValueError('binary control data in candidate text')
        result.append({'row':i,'offset':start,'capacity_bytes':capacity,'original':text})
    if not any(re.search(r'[\u3040-\u30ff\u4e00-\u9fff]',r['original']) for r in result):
        raise ValueError('no Japanese text detected')
    return result

def main():
    entries=[]
    tables=[]
    rejected=[]
    for path in sorted((ROOT/'data/init').glob('*.bin')):
        try:
            subs=members(path)
        except (AssertionError,UnicodeError,struct.error):
            continue
        for mi,(name,data) in enumerate(subs):
            if Path(name).suffix.lower() not in {'.ctd','.ftd','.qtd'}:
                continue
            source=path.relative_to(ROOT/'data').as_posix()
            key=f'{source}:{mi}:{name}'
            try:
                rows=inspect(data,name)
            except (ValueError,UnicodeError,struct.error) as exc:
                rejected.append({'key':key,'reason':str(exc),'bytes':len(data)})
                continue
            digest=hashlib.sha256(data).hexdigest()
            tables.append({'key':key,'rows':len(rows),'member_sha256':digest})
            for row in rows:
                entries.append({'key':key+':'+str(row['row']),'source':source,'member_index':mi,
                                'member_name':name,'member_sha256':digest,**row,
                                'translation':'','status':'untranslated'})
    write(ROOT/'translation/tables.catalog.generated.json',entries)
    write(ROOT/'translation/tables.audit.generated.json',{'tables':tables,'rejected':rejected,'text_rows':len(entries)})
    print(f'Validated {len(tables)} fixed text tables, {len(entries)} rows; {len(rejected)} other tables need format review.')
    for table in tables:
        print(table['key'],table['rows'])

if __name__=='__main__':
    main()
