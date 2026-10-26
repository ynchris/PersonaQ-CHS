"""Export read-only resource path inventories for source-location handoff."""
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parent
base=ROOT/'data'
out=ROOT/'translation/handoff_533'
out.mkdir(parents=True,exist_ok=True)
files=sorted((p for p in base.rglob('*') if p.is_file()),key=lambda p:p.relative_to(base).as_posix())
header=f'Resource root: {base}\nPaths below are relative to this root.\nRead-only inventory; no game resources modified.\n\n'
all_lines=[f'{p.relative_to(base).as_posix()}\t{p.stat().st_size}' for p in files]
(out/'data_all_files.txt').write_text(header+'Relative path\tBytes\n'+'\n'.join(all_lines)+'\n',encoding='utf-8-sig')
scripts=[p for p in files if p.suffix.lower() in {'.bf','.bmd'}]
(out/'data_bf_bmd_paths.txt').write_text(header+'Only standalone .bf/.bmd files; nested archive members are not included.\n\n'+'\n'.join(p.relative_to(base).as_posix() for p in scripts)+'\n',encoding='utf-8-sig')
dirs=sorted({p.parent.relative_to(base).as_posix() for p in files})
(out/'data_directories.txt').write_text(header+'\n'.join(dirs)+'\n',encoding='utf-8-sig')
print('All files:',len(files),'Standalone scripts:',len(scripts),'types:',dict(Counter(p.suffix.lower() for p in scripts)))
print('Output:',out)
