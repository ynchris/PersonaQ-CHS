"""Hash exact per-scope text inputs; equal row counts do not imply equal text."""
import hashlib
import json
from compile_translation import ROOT, read


def scope_snapshot(scope):
    assert scope=='base' or scope in {'0005','0006','0007','0008','0009'}
    prefix='export_base/' if scope=='base' else f'export_dlc/{scope}/'
    rows=[r for r in read(ROOT/'translation/catalog.working.json')
          if r['status']=='draft_control_checked' and r['source'].startswith(prefix)]
    inputs=dict(rows=sorted((r['key'],r['translation']) for r in rows),
                documents=[(s,hashlib.sha256((ROOT/'translation/compiled'/s).read_bytes()).hexdigest())
                           for s in sorted({r['source'] for r in rows})])
    return hashlib.sha256(json.dumps(inputs,ensure_ascii=False,sort_keys=True).encode('utf-8')).hexdigest()
