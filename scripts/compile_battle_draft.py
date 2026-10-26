"""Compile reviewed whole BMD members; retain message identity and control checks."""
from compile_translation import ROOT, read, write

def main():
    draft=read(ROOT/'translation/theodor_battle_opening.zh-Hans.json')
    sources={}
    for number,values in draft['members'].items():
        source=f'{draft["directory"]}/{draft["container"]}_({number}).BMD.json'
        doc=read(ROOT/source)
        assert len(values)==len(doc['texts'])
        rows=[]
        for index,(msg,text) in enumerate(zip(doc['texts'],values)):
            assert len(msg['lines'])==1
            rows.append([index,0,msg['id'],text])
        sources[source]=rows
    write(ROOT/'translation/batches'/draft['batch'],{'status':'draft','sources':sources})
    print(f'{sum(map(len,sources.values()))} battle navigation drafts in {len(sources)} members.')

if __name__=='__main__':
    main()
