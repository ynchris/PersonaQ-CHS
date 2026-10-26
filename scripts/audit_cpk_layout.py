"""Read-only CPK UTF metadata comparison for the boot-crash investigation."""
import struct
from compile_translation import ROOT, write


def table(stream, offset):
    stream.seek(offset)
    head=stream.read(16)
    size=struct.unpack_from('<Q',head,8)[0]
    data=stream.read(size)
    assert data[:4]==b'@UTF', (offset, data[:4])
    rows,strings,blobs=struct.unpack_from('>III',data,8)
    name,cols,width,count=struct.unpack_from('>IHHI',data,20)
    def string(index):
        start=8+strings+index
        return data[start:data.index(b'\0',start)].decode('utf-8')
    def value(pos, typ):
        formats={0:'B',1:'b',2:'H',3:'h',4:'I',5:'i',6:'Q',7:'q',8:'f',10:'I',11:'II'}
        fmt='>'+formats[typ]
        val=struct.unpack_from(fmt,data,pos)
        return (string(val[0]) if typ==10 else val[0] if len(val)==1 else val), struct.calcsize(fmt)
    specs=[]
    pos=32
    for _ in range(cols):
        flag=data[pos]
        col=string(struct.unpack_from('>I',data,pos+1)[0])
        pos+=5
        fixed=None
        if flag&0xf0==0x30:
            fixed,n=value(pos,flag&15)
            pos+=n
        specs.append((col,flag,fixed))
    output=[]
    for i in range(count):
        pos=8+rows+i*width
        row={}
        for col,flag,fixed in specs:
            val=fixed
            if flag&0xf0==0x50:
                val,n=value(pos,flag&15)
                pos+=n
            row[col]=val
        output.append(row)
    return output


def inspect(path):
    with path.open('rb') as f:
        header=table(f,0)[0]
        toc=table(f,header['TocOffset'])
    return {'path':str(path),'bytes':path.stat().st_size,'header':header,
            'toc_columns':list(toc[0]),'first_entries':toc[:3],
            'compressed_files':sum((r.get('FileSize') or 0)<(r.get('ExtractSize') or 0) for r in toc),
            'fonts':[r for r in toc if r.get('DirName')=='font']}


if __name__=='__main__':
    trial=ROOT/'full_work/raw_font_trial'
    paths=[ROOT/'romfs/data.cpk',trial/'citra_backup_aa1e36ab612b4ee7bbf3d72559faa799/00040000000C3600/romfs/data.cpk',trial/'mod/00040000000C3600/romfs/data.cpk']
    reports=[inspect(p) for p in paths]
    write(trial/'cpk_layout_audit.json',reports)
    for r in reports:
        print(r['path'],r['bytes'],'compressed:',r['compressed_files'])
        print(r['header'])
        print(r['first_entries'])
