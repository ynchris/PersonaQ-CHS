"""Find exact Japanese matches in the user-specified Q2 reference; no auto-approval."""
import re
import sys
from collections import defaultdict, Counter
from pathlib import Path
from compile_translation import ROOT, read, write, LEADING, TRAILING, TOKEN

REF=ROOT.parent/'references/PersonaQ2ChsLocalization/texts/zh_Hans'

def normalize(text):
    return re.sub(r'\s+','',text.strip().removeprefix('＞'))

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    memory=defaultdict(list)
    for path in sorted(REF.rglob('*.json')):
        data=read(path)
        if not isinstance(data,list):
            continue
        for r in data:
            jp,zh=r.get('original',''),r.get('translation','')
            if not jp or not zh or jp==zh or any(c in jp+zh for c in '{}[]'):
                continue
            if re.search(r'[\u3041-\u3096\u30a1-\u30fa]',zh):
                continue
            if not re.search(r'[\u3041-\u3096\u30a1-\u30fa]',jp):
                continue
            memory[normalize(jp)].append({'translation':zh,'reference':path.relative_to(REF).as_posix(),'reference_key':r['key'],'stage':r.get('stage')})
    candidates=[]
    for r in read(ROOT/'translation/catalog.working.json'):
        if r['status']!='untranslated':
            continue
        body=TRAILING.sub('',LEADING.sub('',r['original']))
        if TOKEN.search(body):
            continue
        matches=memory.get(normalize(body),[])
        choices={normalize(m['translation']) for m in matches}
        if len(choices)!=1:
            continue
        candidates.append({**r,'reference_matches':matches,'candidate_translation':matches[0]['translation'],
                           'status':'reference_candidate_not_approved'})
    write(ROOT/'translation/reference_candidates.generated.json',candidates)
    print('Candidates (not counted as translated):',len(candidates))
    print(Counter('/'.join(r['source'].split('/')[:2]) for r in candidates))
    for r in candidates[:35]:
        print(r['key'],repr(TRAILING.sub('',LEADING.sub('',r['original']))),'=>',repr(r['candidate_translation']))

if __name__=='__main__':
    main()
