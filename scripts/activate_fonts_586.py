"""Select the 586 unified-CJK fonts for future builds; keep the 544 payloads as a backup."""
import hashlib,shutil
from compile_translation import ROOT,read,write
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    reports=read(ROOT/'translation/font_unified_586.generated.json');assert len(reports)==6
    enc=sha(ROOT/'translation/font_encoding.hex.json')
    prior=read(ROOT/'translation/font_build.generated.json')
    backup=ROOT/'full_work/font_unified_586/previous_payload_544';backup.mkdir(parents=True,exist_ok=True)
    for r in reports:
        p=ROOT/r['path'];assert sha(p)==r['sha256'] and r['encoding_sha256']==enc,(r['font'],'stale font or encoding')
        target=ROOT/'full_work/font_payload'/p.name
        if not (backup/p.name).exists():shutil.copy2(target,backup/p.name)
        shutil.copy2(p,target);assert sha(target)==r['sha256']
        row=next(v for v in prior if v['font']==r['font'])
        row.update(sha256=r['sha256'],bytes=p.stat().st_size,alignment_revision=586,unified_cjk_glyphs=r['redrawn_glyphs'],
                   unified_face='FZFWQingYinTiJWB',fallback_face_glyphs=r['fallback_face_glyphs'],roundtrip_verified=True,runtime_tested=False)
    write(ROOT/'translation/font_build.generated.json',prior)
    print('Selected six 586 unified fonts; 544 payloads backed up in',backup.relative_to(ROOT))
if __name__=='__main__':main()
