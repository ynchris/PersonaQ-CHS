"""Append translated BVP members, preserving original bytes and entry flags."""
import re
import struct

def entries(data):
    result=[]
    pos=0
    while True:
        assert pos+12<=len(data), 'Missing BVP terminator'
        flags,offset,size=struct.unpack_from('<3I',data,pos)
        pos+=12
        if offset==0:
            assert flags==size==0, 'Nonzero BVP terminator'
            break
        assert len(result)<10000 and size>0 and offset+size<=len(data)
        result.append((flags,offset,size))
    assert result and all(o>=pos for _,o,_ in result)
    spans=sorted((o,o+s) for _,o,s in result)
    assert all(a[1]<=b[0] for a,b in zip(spans,spans[1:]))
    return result

def replace_members(original,rebuilt,names):
    before=entries(original)
    compiled=entries(rebuilt)
    assert len(before)==len(compiled)
    assert [e[0] for e in before]==[e[0] for e in compiled], 'BVP flags changed'
    changed=set()
    for name in names:
        match=re.fullmatch(r'\((\d+)\)\.BMD',name)
        assert match, 'Unexpected BVP member name'
        index=int(match[1])
        assert index<len(before) and index not in changed
        changed.add(index)
    result=bytearray(original)
    permitted=set()
    for index in sorted(changed):
        _,offset,size=compiled[index]
        new=rebuilt[offset:offset+size]
        result.extend(b'\0'*((-len(result))%16))
        position=len(result)
        result.extend(new)
        struct.pack_into('<2I',result,index*12+4,position,len(new))
        permitted.update(range(index*12+4,index*12+12))
    assert all(a==b or i in permitted for i,(a,b) in enumerate(zip(original,result)))
    after=entries(result)
    for i,(_,offset,size) in enumerate(after):
        source=rebuilt if i in changed else original
        _,expected_offset,expected_size=(compiled if i in changed else before)[i]
        assert result[offset:offset+size]==source[expected_offset:expected_offset+expected_size]
    return bytes(result),len(before)-len(changed)
