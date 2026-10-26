"""Extract original demo font only, into a diagnostic directory."""
import sys,os,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parent
out=ROOT/'translation/inspection_530/demo_font';out.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT.parent/'tools/pq_python_deps'))
sys.path.insert(0,str(ROOT.parent/'references/PersonaQ2ChsLocalization/bin/3dstools'))
os.chdir(out)
sys.argv=['bcfnt.py','-x','-y','-f',str(ROOT/'data/font/demo_font.bcfnt')]
runpy.run_path(str(ROOT.parent/'references/PersonaQ2ChsLocalization/bin/3dstools/bcfnt.py'),run_name='__main__')
