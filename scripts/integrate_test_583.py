"""Merge current verified text/fonts, approved images, and user-tested IME."""
import hashlib,json
from pathlib import Path
from check_roundtrip import parse_members
from encode_images_540 import pack
from integrate_test_540 import codes
from stage_pinyin_539 import patch_archive,TARGETS
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    manifest_path=ROOT/'translation/integrated_build.generated.json';manifest=read(manifest_path)
    stage=ROOT/'full_work/integrated_payload';resources={r['file']:r['sha256'] for r in manifest['resources']}
    for rel,digest in resources.items():assert sha((stage/rel).read_bytes())==digest
    fonts=read(ROOT/'translation/font_build.generated.json')
    assert len(fonts)==6 and all(r.get('alignment_revision')==544 for r in fonts)
    for r in fonts:assert resources['font/'+r['font']+'.bcfnt']==r['sha256']
    exe=codes(['code_party_577.review.json','code_party_580.review.json','code_ui_582.review.json'],'full_work/code_583');images=read(ROOT/'translation/build_583/images.json')
    approved=read(ROOT/'translation/previews_570/review.json')
    assert approved['status']=='approved_by_user' and approved['sha256']==images['quote']['sha256']
    for row in images['files']:
        rel=row['file'];old=(ROOT/'data'/rel).read_bytes();image=(ROOT/row['output']).read_bytes()
        assert sha(old)==row['source_sha256'] and sha(image)==row['sha256']
        current=bytearray((stage/rel).read_bytes() if rel in resources else old)
        if rel.endswith(('.bin','.arc','.pac')):
            a=dict(parse_members(old));b=dict(parse_members(image));parts=parse_members(bytes(current))
            replacement={n:v for n,v in b.items() if v!=a[n]}
            for n,v in parts:
                if n in replacement:assert v==a[n] or v==replacement[n],(rel,n)
            current=bytearray(pack([(n,replacement.get(n,v)) for n,v in parts]))
        else:
            assert len(current)==len(old)==len(image)
            for i,(before,after) in enumerate(zip(old,image)):
                if before!=after:
                    assert current[i] in (before,after),(rel,i)
                    current[i]=after
        target=stage/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(current);resources[rel]=sha(current)
    ime=ROOT/'translation/ime_538';build=read(ime/'build.json');tests=read(ime/'native_test.json')
    assert build['font_map_sha256']==sha((ROOT/'translation/font_encoding.hex.json').read_bytes())
    for name,digest in build['dictionaries'].items():assert digest==tests['hashes'][name]==sha((ime/name).read_bytes())
    for filename,prefix in TARGETS.items():
        rel='init/'+filename;before=(stage/rel).read_bytes() if rel in resources else (ROOT/'data'/rel).read_bytes()
        after=patch_archive(before,prefix,(ime/'pinyin_idx.tbl').read_bytes(),(ime/'pinyin_dat.txt').read_bytes())
        target=stage/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after);resources[rel]=sha(after)
    manifest.update(executable_resources=exe,resources=[dict(file=n,sha256=h) for n,h in sorted(resources.items())],
       test_revision=583,ui_fix_revisions=[573,574,575,576,577,578,579,580,582],sprite_box_edits=images['sprite_box_edits'],image_ctpk_count=74,image_tmx_count=1,model_texture_count=1,seneca_image_revision=570,
       font_alignment_revision=544,pinyin_input_archives=4,pinyin_native_function_tests=838,
       pinyin_user_reported_test_passed=True,pinyin_dictionaries_unchanged=True,cpk_packaged=False,runtime_tested=False,
       pending=['Gameplay verification of latest font calibration and image layout','Opening quotation/animation verification in new package','Full-game coverage verification','Sprite 218 relocated box and 573-582 UI fixes in gameplay'])
    assert {p.relative_to(stage).as_posix():sha(p.read_bytes()) for p in stage.rglob('*') if p.is_file()}==resources
    text=json.dumps(manifest,ensure_ascii=False,indent=2)
    manifest_path.write_text(text,encoding='utf-8');(ROOT/'translation/build_583/integrated.json').write_text(text,encoding='utf-8')
    print('Integrated revision 583:',len(resources),'resources; calibrated fonts + 570 quote + unchanged tested IME.')
if __name__=='__main__':main()
