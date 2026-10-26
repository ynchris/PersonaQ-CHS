"""Compile whole-scene drafts pinned to exact original exports."""
import hashlib
from compile_translation import ROOT, read, write

def main():
    total=0
    for path in sorted((ROOT/'translation/story').glob('*.json')):
        draft=read(path)
        source=draft['source']
        assert hashlib.sha256((ROOT/source).read_bytes()).hexdigest()==draft['source_sha256'].lower(), 'Story source changed: '+source
        doc=read(ROOT/source)
        selected={int(k):v for k,v in draft['messages'].items()}
        omitted=set(draft.get('excluded_placeholder_indices',[]))
        assert not set(selected)&omitted
        assert set(selected)|omitted==set(range(len(doc['texts']))), 'Incomplete scene: '+source
        rows=[]
        for mi,lines in sorted(selected.items()):
            msg=doc['texts'][mi]
            assert len(lines)==len(msg['lines']), f'Page count mismatch: {source}:{mi}'
            rows.extend([mi,li,msg['id'],line] for li,line in enumerate(lines))
        names=draft['speaker_names']
        assert set(names)==set(doc['speakers']), 'Speaker inventory mismatch'
        speakers=[[i,jp,names[jp]] for i,jp in enumerate(doc['speakers']) if names[jp]!=jp]
        write(ROOT/'translation/batches'/draft['batch'],{
            'status':'draft','sources':{source:rows},'speakers':{source:speakers},
            'source_sha256':draft['source_sha256'],'excluded_placeholder_indices':sorted(omitted)})
        total+=len(rows)
    print(f'Compiled {total} pinned story draft lines.')

if __name__=='__main__':
    main()
