"""Read-only source audit and isolated texture extraction for tester feedback."""
import json, struct, subprocess
from pathlib import Path
from compile_translation import ROOT,read,write,TOKEN
from q2_name_banks import load
from encode_images_540 import DOTNET,HELPER

OUT=ROOT/'translation/feedback_541'
def main():
    OUT.mkdir(exist_ok=True)
    names={}
    for g in load()['groups']:
        if g['source']!='battle/table/enemynametable.tbl':continue
        for r in g['rows']:
            assert r['original'] not in names or names[r['original']]==r['translation']
            names[r['original']]=r['translation']
    matches=[]
    for r in read(ROOT/'translation/catalog.working.json'):
        if 'datmaterialhelp' not in r['source']:continue
        plain=TOKEN.sub('',r['original'])
        candidates=[(n,c) for n,c in names.items() if n in plain]
        # Longer exact enemy names win over suffixes embedded in them.
        candidates=[(n,c) for n,c in candidates if not any(n!=m and n in m for m,_ in candidates)]
        if candidates:matches.append(dict(key=r['key'],original=r['original'],translation=r.get('translation'),enemies=candidates))
    write(OUT/'material_enemy_audit.json',matches)
    print('Material rows with enemy references:',len(matches))
    print(json.dumps(matches[:8],ensure_ascii=False,indent=2))
    src=OUT/'textures';src.mkdir(exist_ok=True)
    sources=['camp/c_main.spr3','battle/panel/adv.spr3','battle/panel/info.ctpk','battle/panel/btl.spr3']
    records=[]
    for rel in sources:
        raw=(ROOT/'data'/rel).read_bytes();pos=0;i=0
        while True:
            off=raw.find(b'CTPK',pos)
            if off<0:break
            section,size=struct.unpack_from('<II',raw,off+8)
            assert off+section+size<=len(raw)
            name=rel.replace('/','_')+f'.tex{i}.ctpk'
            (src/name).write_bytes(raw[off:off+section+size])
            records.append(dict(source=rel,offset=off,length=section+size,name=name))
            pos=off+section+size;i+=1
    write(OUT/'texture_sources.json',records)
    print(json.dumps(records,indent=2))
    subprocess.run([str(DOTNET),str(HELPER),'export','-i',str(src),'-o',str(OUT/'decoded')],check=True)

if __name__=='__main__':main()
