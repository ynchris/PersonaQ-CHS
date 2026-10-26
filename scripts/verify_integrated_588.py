"""Final local provenance checks while CPK packaging runs."""
import hashlib,json
from pathlib import Path
from check_roundtrip import parse_members
from stage_pinyin_539 import TARGETS
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
stage=ROOT/'full_work/integrated_payload';old=ROOT/'full_work/integrated_payload_before_588'
manifest=read(ROOT/'translation/integrated_build.generated.json')
assert manifest['test_revision']==588
results=[]
for filename,prefix in TARGETS.items():
    a=dict(parse_members((old/'init'/filename).read_bytes()))
    b=dict(parse_members((stage/'init'/filename).read_bytes()))
    for suffix in ['_idx.tbl','_dat.txt']:
        name=prefix+suffix;assert a[name]==b[name]
    results.append(dict(archive=filename,unchanged_tested_dictionaries=True))
images=read(ROOT/'translation/build_588/images.json')
for r in images['files']:
    assert sha(ROOT/'data'/r['file'])==r['source_sha256']
    if not r['file'].endswith(('.bin','.arc')):
        assert sha(stage/r['file'])==r['sha256']
fonts=read(ROOT/'translation/font_build.generated.json')
for r in fonts:assert r['alignment_revision']==586 and sha(stage/'font'/(r['font']+'.bcfnt'))==r['sha256']
assert sha(ROOT/'translation/previews_570/seneca.png')==images['quote']['sha256']
assert read(ROOT/'translation/previews_568/review.json')['status']=='superseded_do_not_encode'
report=dict(pinyin=results,font_alignment_revision=586,verified_fonts=6,original_image_containers_unchanged=True,quote_revision=570,old_quote_excluded=True)
(ROOT/'translation/build_588/provenance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
