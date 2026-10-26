"""Select verified fonts for future builds, preserving previous payloads."""
import shutil,hashlib
from compile_translation import ROOT,read,write
def main():
    reports=read(ROOT/'translation/font_aligned_544.generated.json');assert len(reports)==6
    prior=read(ROOT/'translation/font_build.generated.json');backup=ROOT/'full_work/font_aligned_544/previous_payload';backup.mkdir(exist_ok=True)
    for r in reports:
        p=ROOT/r['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
        target=ROOT/'full_work/font_payload'/p.name
        if not (backup/p.name).exists():shutil.copy2(target,backup/p.name)
        shutil.copy2(p,target)
        row=next(v for v in prior if v['font']==r['font'])
        row.update(sha256=r['sha256'],bytes=p.stat().st_size,alignment_revision=544,
            calibrated_glyphs=r['changed_glyphs'],cwdh_end_index_corrected=True,roundtrip_verified=True,runtime_tested=False)
    write(ROOT/'translation/font_build.generated.json',prior)
    print('Selected six verified fonts for next build; current ROM unchanged.')
if __name__=='__main__':main()
