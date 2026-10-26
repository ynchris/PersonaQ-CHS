"""Replace only section 3 (BMD) in an Atlus FLW0 script."""
import struct

def sections(data):
    if data[8:12]!=b'FLW0':
        raise ValueError('Not FLW0')
    endian='<' if data[16] else '>'
    n=struct.unpack_from(endian+'I',data,16)[0]
    if not 0<n<64:
        raise ValueError('Invalid section count')
    rows=[struct.unpack_from(endian+'4I',data,32+i*16) for i in range(n)]
    for kind,size,count,offset in rows:
        if offset+size*count>len(data):
            raise ValueError('Section exceeds file')
    return endian,rows

def replace_text(original,rebuilt):
    endian,rows=sections(original)
    other_endian,newrows=sections(rebuilt)
    assert endian==other_endian
    oldtext=[r for r in rows if r[0]==3]
    newtext=[r for r in newrows if r[0]==3]
    assert len(oldtext)==len(newtext)==1
    _,unit,count,start=oldtext[0]
    _,newunit,newcount,newstart=newtext[0]
    end=start+unit*count
    text=rebuilt[newstart:newstart+newunit*newcount]
    assert len(text)%unit==0
    delta=len(text)-(end-start)
    result=bytearray(original[:start]+text+original[end:])
    for i,(kind,size,count,offset) in enumerate(rows):
        if kind==3:
            count=len(text)//size
        elif start<=offset<end and size*count:
            raise ValueError('Sections overlap BMD')
        if kind!=3 and offset>=end:
            offset+=delta
        struct.pack_into(endian+'4I',result,32+i*16,kind,size,count,offset)
    limit=struct.unpack_from(endian+'I',original,4)[0]
    if limit>=end:
        struct.pack_into(endian+'I',result,4,limit+delta)
    elif limit>start:
        raise ValueError('File limit inside BMD')
    _,after=sections(result)
    for a,b in zip(rows,after):
        if a[0]!=3:
            assert a[:3]==b[:3]
            assert original[a[3]:a[3]+a[1]*a[2]]==result[b[3]:b[3]+b[1]*b[2]]
    # All bytes outside header offsets and the BMD itself are preserved.
    assert original[32+len(rows)*16:start]==result[32+len(rows)*16:start]
    assert original[end:]==result[end+delta:]
    return bytes(result),len(rows)-1
