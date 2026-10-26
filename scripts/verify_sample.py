"""Audit sample staging and, optionally, the re-extracted CPK against sources."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def main():
    target = Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'sample_staging'
    original = ROOT/'data'
    payload = ROOT/'sample_payload_v3'
    names = {p.relative_to(original) for p in original.rglob('*') if p.is_file()}
    actual = {p.relative_to(target) for p in target.rglob('*') if p.is_file()}
    assert names == actual, 'File inventory mismatch'
    modified=[]
    for rel in sorted(names):
        expected = payload/rel if (payload/rel).is_file() else original/rel
        assert digest(expected) == digest(target/rel), f'Payload mismatch: {rel}'
        if (payload/rel).is_file():
            modified.append(rel.as_posix())
    report=dict(verified_directory=str(target.resolve()), files=len(names),
        modified=modified, unmodified=len(names)-len(modified), runtime_tested=False)
    report_path = ROOT/('cpk_verification.json' if len(sys.argv)>1 else 'staging_verification.json')
    report_path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    main()
