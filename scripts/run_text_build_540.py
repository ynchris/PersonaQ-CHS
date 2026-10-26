"""Rebuild current text resources with local logs; no installation/deletion."""
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
LOG=ROOT/'translation/build_540/logs'
LOG.mkdir(parents=True,exist_ok=True)
commands=[['compile_translation.py'],['build_draft_messages.py','base']]
commands += [['build_draft_messages.py',s] for s in ['0005','0006','0007','0008','0009']]
commands += [['build_draft_tables.py'],['build_code_ui.py'],['assemble_draft_payload.py']]
for i,args in enumerate(commands):
    print('Starting',*args,flush=True)
    p=LOG/(str(i)+'_'+args[0]+'.log')
    with p.open('wb') as log:
        result=subprocess.run([sys.executable,'-X','utf8',*args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    if result.returncode:
        print(p.read_text(encoding='utf-8',errors='replace')[-2500:],flush=True)
        raise SystemExit(result.returncode)
    print('Passed',*args,flush=True)
