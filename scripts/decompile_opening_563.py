"""Read-only opening-script analysis with independent output/log directories."""
import hashlib,subprocess,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'translation/opening_flow_563';OUT.mkdir(exist_ok=True)
dotnet=ROOT.parent/'tools/dotnet8/dotnet.exe'
dll=ROOT.parent/'tools/Atlus-Script-Tools/Build/Release/net8.0/AtlusScriptCompiler.dll'
rows=[]
all_mode='--all' in sys.argv
for name in ([p.stem for p in sorted((ROOT/'data/event/e000').glob('*.bf'))] if all_mode else ['e000_010','e020_001']):
    src=ROOT/f'data/event/e000/{name}.bf';digest=hashlib.sha256(src.read_bytes()).hexdigest()
    for mode,ext in ([('Disassemble','asm')] if all_mode else [('Decompile','flow'),('Disassemble','asm')]):
        dest=OUT/f'{name}.{ext}'
        cmd=[str(dotnet),str(dll),'-In',str(src),'-'+mode,'-Encoding','SJ','-Out',str(dest)]
        p=subprocess.run(cmd,cwd=OUT,capture_output=True,timeout=90)
        rawlog=p.stdout+p.stderr
        decoded=rawlog.decode('utf-16-le' if b'\x00' in rawlog[:80] else 'utf-8',errors='replace')
        log=OUT/f'{name}.{mode}.log';log.write_text(decoded,encoding='utf-8')
        rows.append(dict(source=str(src),mode=mode,returncode=p.returncode,output=str(dest),exists=dest.exists(),source_unchanged=hashlib.sha256(src.read_bytes()).hexdigest()==digest))
        print(name,mode,p.returncode,dest.exists(),flush=True)
        if p.returncode:print(decoded[-1500:],flush=True)
(OUT/('all_runs.json' if all_mode else 'runs.json')).write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
