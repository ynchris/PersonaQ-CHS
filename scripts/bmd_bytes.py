"""Independent BMD byte reader, avoiding lossy CP932 decoding in verification."""
import struct
import re
from repack_bf_text import sections
from repack_bvp_text import entries
from nested_text_members import extract_nested


def read_document(path, member=None):
    data=path.read_bytes()
    if member is not None:
        if path.suffix.lower()=='.bvp':
            match=re.fullmatch(r'\((\d+)\)\.BMD',member)
            assert match
            _,offset,size=entries(data)[int(match[1])]
            data=data[offset:offset+size]
        else:
            data=extract_nested(data,member)
    if data[8:12]==b'FLW0':
        _,rows=sections(data)
        selected=[r for r in rows if r[0]==3]
        assert len(selected)==1
        _,unit,count,start=selected[0]
        data=data[start:start+unit*count]
    return parse(data)


def parse(data):
    assert data[:4]==b'\x07\0\0\0' and data[8:12] in (b'MSG1',b'1GSM')
    endian='<' if data[8:12]==b'MSG1' else '>'
    def num(fmt,pos):
        return struct.unpack_from(endian+fmt,data,pos)
    count=num('I',24)[0]
    assert count<100000
    pointers=[num('II',32+i*8) for i in range(count)]
    names_pos,names_count=num('II',32+count*8)
    names=[]
    for i in range(names_count):
        start=32+num('I',32+names_pos+i*4)[0]
        names.append(data[start:data.index(b'\0',start)])
    messages=[]
    for kind,offset in pointers:
        pos=32+offset
        ident=data[pos:pos+24].rstrip(b'\0').decode('ascii') or '<EMPTY>'
        if kind==0:
            n,speaker=num('HH',pos+24)
            ptr=pos+28
        else:
            assert kind==1
            zero,n=num('HH',pos+24)
            assert zero==0
            speaker=65535
            ptr=pos+32
        lines=[]
        if n:
            starts=[32+num('I',ptr+i*4)[0] for i in range(n)]
            total=num('I',ptr+n*4)[0]
            end=ptr+n*4+4+total
            assert starts[0]==ptr+n*4+4 and end<=len(data)
            assert starts==sorted(starts)
            lines=[data[a:b] for a,b in zip(starts,starts[1:]+[end])]
        messages.append({'id':ident,'kind':kind,'speaker_index':speaker,'lines':lines})
    return {'speakers':names,'texts':messages}
