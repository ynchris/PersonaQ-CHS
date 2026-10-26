"""Expand reviewed DLC navigation rows; aliases require identical source bodies."""
from compile_translation import ROOT, read, write, LEADING, TRAILING

def body(line):
    return TRAILING.sub('',LEADING.sub('',line))

def compile_one(path):
    draft=read(path)
    source=draft['source']
    doc=read(ROOT/source)
    values={int(k):v for k,v in draft['reviewed_bodies'].items()}
    for key,other in draft['identical_body_aliases'].items():
        index=int(key)
        assert index not in values
        assert body(doc['texts'][index]['lines'][0])==body(doc['texts'][other]['lines'][0])
        values[index]=values[other]
    assert set(values).isdisjoint(draft['excluded_placeholder_indices'])
    assert set(values)|set(draft['excluded_placeholder_indices'])==set(range(len(doc['texts'])))
    rows=[]
    for index,value in sorted(values.items()):
        msg=doc['texts'][index]
        assert len(msg['lines'])==1
        rows.append([index,0,msg['id'],value])
    batch=draft.get('batch','013_dlc_theodor_navigation.generated.json')
    write(ROOT/'translation/batches'/batch,{
        'status':'draft','sources':{source:rows},'excluded_placeholder_indices':draft['excluded_placeholder_indices']})
    print(f'{len(rows)} DLC navigation draft rows; placeholders excluded.')

def main():
    for path in sorted((ROOT/'translation').glob('*_navigation.zh-Hans.json')):
        compile_one(path)

if __name__=='__main__':
    main()
