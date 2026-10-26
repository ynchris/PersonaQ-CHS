"""Build verified test installers. Never install or delete existing files."""
import json
import shutil
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'translation/build_540'
LOG=OUT/'logs'
LOG.mkdir(parents=True,exist_ok=True)
mode=sys.argv[1]
if mode=='snapshot':
    rows=[]
    for name in ['localized_base_cxi.generated.json','localized_update_cia.generated.json','localized_dlc_cia.generated.json']:
        p=ROOT/'translation'/name
        d=json.loads(p.read_text(encoding='utf-8'));rows.append(dict(report=name,file=d['file'],sha256=d['sha256']))
        shutil.copy2(p,OUT/('previous_'+name))
    (OUT/'previous_outputs.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    print('Previous installer identities saved; no files removed.')
    raise SystemExit(0)
commands=([['pack_base_draft.py'],['build_localized_base_cxi.py']] if mode=='base' else
          [['pack_dlc_draft.py',s] for s in ['0005','0006','0007','0008','0009']]+[['build_localized_update_cia.py'],['build_localized_dlc_cia.py']])
assert mode in ['base','addons']
for i,args in enumerate(commands):
    print('Starting',*args,flush=True)
    path=LOG/(mode+'_'+str(i)+'_'+args[0]+'.log')
    with path.open('wb') as log:
        result=subprocess.run([sys.executable,'-X','utf8',*args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    if result.returncode:
        print(path.read_text(encoding='utf-8',errors='replace')[-2200:],flush=True)
        raise SystemExit(result.returncode)
    print('Passed',*args,flush=True)
