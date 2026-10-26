"""Revision 583 build orchestration; preserve previous deliverables and staging."""
import hashlib,json,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'translation/build_583';OUT.mkdir(exist_ok=True)
LOG=OUT/'logs';LOG.mkdir(exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args):
    print('Starting',*args,flush=True)
    p=LOG/('_'.join(args).replace('/','_')+'.log')
    with p.open('wb') as f:r=subprocess.run([sys.executable,'-X','utf8',*args],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    if r.returncode:
        print(p.read_text(encoding='utf-8',errors='replace')[-3500:],flush=True)
        raise SystemExit(r.returncode)
    print('Passed',*args,flush=True)
mode=sys.argv[1]
if mode=='prepare':
    marker=OUT/'prepared.json'
    if marker.exists():print('Already prepared; previous stage preserved.');raise SystemExit(0)
    for name in ['integrated_build.generated.json','localized_base_cxi.generated.json','localized_update_cia.generated.json','localized_dlc_cia.generated.json','font_build.generated.json','q2_name_banks_build.generated.json']:
        shutil.copy2(ROOT/'translation'/name,OUT/('previous_'+name))
    stage=(ROOT/'full_work/integrated_payload').resolve()
    backup=(ROOT/'full_work/integrated_payload_before_583').resolve()
    assert stage.parent==backup.parent==(ROOT/'full_work').resolve()
    assert stage.name=='integrated_payload' and backup.name=='integrated_payload_before_583'
    assert stage.is_dir() and not backup.exists()
    # Exact checked derived staging directory only; no ROM or save is moved.
    shutil.move(str(stage),str(backup));stage.mkdir()
    review=ROOT/'translation/previews_576/review.json';d=read(review)
    for o in d['outputs']:assert sha(ROOT/o['path'])==o['sha256']
    d.update(status='approved_by_user',approval_note='用户确认576箭头修订；A键裁切仅为预览模拟问题，按钮间距与573光标字体随576一并回封。')
    write(review,d)
    write(marker,dict(previous_stage=str(backup),pinyin_user_reported_test_passed=True,ui_fix_revisions=[573,574,575,576,577,578,579,580,582],
         pinyin_scope='用户确认之前测试拼音输入无问题；不推定其他未报告测试通过。',previous_roms_unchanged=True))
    print('Prepared; free GiB:',round(shutil.disk_usage(ROOT).free/1024**3,1))
elif mode=='text':
    assert (OUT/'prepared.json').exists()
    for args in [['compile_translation.py'],['q2_name_banks.py'],['build_draft_messages.py','base']]+[['build_draft_messages.py',s] for s in ['0005','0006','0007','0008','0009']]+[['build_draft_tables.py'],['build_code_ui.py'],['assemble_draft_payload.py'],['verify_enemy_543.py'],['verify_storage_554.py'],['audit_names_555.py']]:run(args)
elif mode=='base':
    for args in [['pack_base_draft.py'],['build_localized_base_cxi.py']]:run(args)
elif mode=='addons':
    for args in [['pack_dlc_draft.py',s] for s in ['0005','0006','0007','0008','0009']]+[['build_localized_update_cia.py'],['build_localized_dlc_cia.py']]:run(args)
else:raise ValueError(mode)
