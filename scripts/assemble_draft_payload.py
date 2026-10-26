"""Assemble an internal, explicitly incomplete payload from verified resources."""
import hashlib
import shutil
from compile_translation import ROOT, read, write
from message_snapshot import scope_snapshot


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    progress=read(ROOT/'translation/progress.generated.json')
    messages=read(ROOT/'translation/message_build.generated.json')
    assert messages.get('translation_input_sha256')==scope_snapshot('base'), 'Base messages need rebuilding after text changes'
    message_snapshots={'base':messages['translation_input_sha256']}
    tables=read(ROOT/'translation/table_build.generated.json')
    fonts=read(ROOT/'translation/font_build.generated.json')
    encoding_path=ROOT/'translation/font_encoding.hex.json'
    encoding=read(encoding_path)
    # Code belongs to ExeFS, not data.cpk. Bind both separate versions to the
    # same font mapping without accidentally inserting them in the CPK payload.
    code_report=read(ROOT/'translation/code_ui_build.generated.json')
    code_review=read(ROOT/'translation/code_ui_450.review.json')
    assert code_report['encoding_sha256']==sha(encoding_path)
    assert code_report['review_sha256']==sha(ROOT/'translation/code_ui_450.review.json')
    assert [f['scope'] for f in code_report['files']]==['base','update']
    for built,reviewed in zip(code_report['files'],code_review['files']):
        assert built['source']==reviewed['source']
        assert built['source_sha256']==reviewed['sha256']==sha(ROOT/built['source'])
        assert built['sha256']==sha(ROOT/built['output'])
        assert built['reviewed_strings']==len(reviewed['rows'])
        assert built['outside_string_bytes_preserved'] and built['terminators_preserved'] and built['roundtrip_verified']
    assert sum(f['reviewed_strings'] for f in code_report['files'])==progress['executable_ui_draft_slots']
    assert messages['encoding_sha256']==sha(encoding_path)
    assert messages['roundtrip_verified']
    catalog=read(ROOT/'translation/catalog.working.json')
    base_rows=[r for r in catalog if r['status']=='draft_control_checked' and r['source'].startswith('export_base/')]
    assert messages['draft_lines']==len(base_rows)
    assert messages['documents']==len({r['source'] for r in base_rows})
    dlc_resources=[]
    dlc_count=0
    for scope in sorted({r['source'].split('/')[1] for r in catalog if r['status']=='draft_control_checked' and r['source'].startswith('export_dlc/')}):
        build=read(ROOT/'translation'/f'dlc_{scope}_message_build.generated.json')
        assert build.get('translation_input_sha256')==scope_snapshot(scope), f'DLC {scope} message snapshot stale'
        message_snapshots[scope]=build['translation_input_sha256']
        assert build['encoding_sha256']==sha(encoding_path)
        selected=[r for r in catalog if r['status']=='draft_control_checked' and r['source'].startswith('export_dlc/'+scope+'/')]
        assert build['roundtrip_verified'] and build['draft_lines']==len(selected)
        assert build['documents']==len({r['source'] for r in selected})
        for resource in build['files']:
            path=ROOT/'full_work/dlc_messages'/scope/'payload'/resource['file']
            assert sha(path)==resource['sha256']
            dlc_resources.append({'content':scope,**resource})
        dlc_count+=build['draft_lines']
    assert messages['draft_lines']+dlc_count==progress['translated_draft_lines']
    assert tables['reviewed_rows']==progress['translated_table_draft_rows']
    assert tables['encoding_sha256']==sha(encoding_path)
    expected={r['file']:r['sha256'] for r in messages['files']}
    for row in tables['files']:
        assert row['outside_text_bytes_preserved'] and row['roundtrip_verified']
        assert row['baseline_sha256']==expected.get(row['file'],sha(ROOT/'data'/row['file']))
        expected[row['file']]=row['sha256']
    stage=ROOT/'full_work/integrated_payload'
    # Equipment names live in a separate fixed bank, not the generic menu tables.
    from equipment_names import load_drafts, SOURCE as equipment_source
    import json
    equipment=read(ROOT/'translation/equipment_build.generated.json')
    equipment_rows=load_drafts()[3]
    assert equipment['equipment_rows']==len(equipment_rows)==progress['equipment_name_draft_rows']
    from q2_item_names import load as load_extra_items
    extra_items=load_extra_items()
    assert equipment['extra_item_rows']==len(extra_items)==progress['q2_extra_item_name_slots']
    equipment_rows={**equipment_rows,**extra_items}
    assert equipment['draft_rows']==len(equipment_rows)
    assert equipment['draft_sha256']==hashlib.sha256(json.dumps(equipment_rows,sort_keys=True,ensure_ascii=False).encode('utf-8')).hexdigest()
    assert equipment['encoding_sha256']==sha(encoding_path)
    assert equipment['numeric_records_preserved'] and equipment['outside_text_bytes_preserved'] and equipment['roundtrip_verified']
    assert equipment['source_sha256']==sha(ROOT/'data'/equipment_source)
    source=ROOT/'full_work/equipment_payload'/equipment_source
    assert sha(source)==equipment['sha256']
    assert equipment_source not in expected
    target=stage/equipment_source
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,target)
    expected[equipment_source]=equipment['sha256']
    from persona_names import load_drafts as load_persona_names, SOURCE as persona_source, DRAFT as persona_draft
    persona=read(ROOT/'translation/persona_names_build.generated.json')
    assert persona['draft_rows']==len(load_persona_names()[2])==progress['persona_name_draft_rows']
    assert persona['draft_sha256']==sha(persona_draft)
    assert persona['encoding_sha256']==sha(encoding_path)
    assert persona['source_sha256']==sha(ROOT/'data'/persona_source)
    assert persona['roundtrip_verified'] and persona['unselected_names_preserved']
    assert not persona['parameter_tables_touched']
    source=ROOT/'full_work/persona_payload'/persona_source
    assert sha(source)==persona['sha256'] and persona_source not in expected
    target=stage/persona_source
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,target)
    expected[persona_source]=persona['sha256']
    from q2_name_banks import load as load_name_banks, DRAFT as names_draft
    banks=load_name_banks()
    bank_build=read(ROOT/'translation/q2_name_banks_build.generated.json')
    assert bank_build['draft_sha256']==sha(names_draft)
    assert bank_build.get('local_completion_sha256')==banks.get('local_completion_sha256')
    assert bank_build.get('skill_completion_sha256')==banks.get('skill_completion_sha256')
    assert bank_build['encoding_sha256']==sha(encoding_path)
    assert bank_build['roundtrip_verified'] and bank_build['unselected_bytes_preserved']
    assert {f['source'] for f in bank_build['files']}=={g['source'] for g in banks['groups']}
    assert sum(f['rows'] for f in bank_build['files'])==progress['q2_name_bank_draft_slots']
    for resource in bank_build['files']:
        name=resource['source']
        assert name not in expected and sha(ROOT/'data'/name)==resource['source_sha256']
        source=ROOT/'full_work/q2_name_payload'/name
        assert sha(source)==resource['sha256']
        target=stage/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
        expected[name]=resource['sha256']
    assert len(fonts)==6
    from schoolwalk_names import load as load_schoolwalk, DRAFT as schoolwalk_draft, SOURCE as schoolwalk_source
    schoolwalk=read(ROOT/'translation/schoolwalk_build.generated.json')
    assert schoolwalk['draft_sha256']==sha(schoolwalk_draft)
    assert schoolwalk['source_sha256']==sha(ROOT/'data'/schoolwalk_source)
    assert schoolwalk['encoding_sha256']==sha(encoding_path)
    assert schoolwalk['rows']==len(load_schoolwalk()['rows'])==progress['schoolwalk_title_slots']
    assert schoolwalk['roundtrip_verified'] and schoolwalk['unselected_bytes_preserved']
    source=ROOT/'full_work/schoolwalk_payload'/schoolwalk_source
    assert sha(source)==schoolwalk['sha256'] and schoolwalk_source not in expected
    target=stage/schoolwalk_source
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,target)
    expected[schoolwalk_source]=schoolwalk['sha256']
    for row in fonts:
        assert row['encoding_sha256']==sha(encoding_path)
        assert row['roundtrip_verified'] and row['original_pixels_preserved'] and not row['missing']
        name=row['font']
        manifest=read(ROOT/'full_work/font_verify'/name/f'{name}_manifest.json')
        for char,encoded in encoding.items():
            code=chr(int.from_bytes(bytes.fromhex(encoded),'big'))
            assert code in manifest['glyphMap'], f'Missing font code: {name}:{char!r}'
        source=ROOT/'full_work/font_payload'/f'{name}.bcfnt'
        assert sha(source)==row['sha256']
        assert source.stat().st_size==row['bytes']
        target=stage/'font'/source.name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
        expected['font/'+source.name]=sha(source)
    actual={p.relative_to(stage).as_posix():sha(p) for p in stage.rglob('*') if p.is_file()}
    assert actual==expected, 'Unexpected or stale resource in integrated payload'
    write(ROOT/'translation/integrated_build.generated.json',{
        'status':'INCOMPLETE_INTERNAL_DRAFT_NOT_A_RELEASE',
        'message_input_snapshots':message_snapshots,
        'executable_resources':code_report['files'],
        'executable_review_sha256':code_report['review_sha256'],
        'base_title_id':'00040000000C3600',
        'message_drafts':messages['draft_lines'],
        'dlc_message_drafts':dlc_count,'dlc_resources':dlc_resources,
        'speaker_entries':progress['translated_speaker_entries'],
        'table_reviewed_rows':tables['reviewed_rows'],
        'equipment_name_rows':equipment['equipment_rows'],
        'extra_item_name_rows':equipment['extra_item_rows'],
        'q2_name_bank_slots':progress['q2_name_bank_draft_slots'],
        'persona_name_rows':persona['draft_rows'],
        'schoolwalk_title_slots':schoolwalk['rows'],
        'table_changed_rows':sum(r['changed_rows'] for r in tables['files']),
        'fonts':len(fonts),'encoding_sha256':tables['encoding_sha256'],
        'resources':[{'file':k,'sha256':v} for k,v in sorted(actual.items())],
        'cpk_packaged':False,'runtime_tested':False,
        'update_runtime_verified':False,'dlc_localization_complete':False,
        'pending':['Resource coverage audit and remaining executable strings',
                   'Image text translation','Final full-game character encoding strategy',
                   'Layout and terminology review','Update and DLC integration',
                   'CPK rebuild and complete inventory verification',
                   'Emulator and hardware validation']})
    print(f'Assembled and hash-verified {len(actual)} internal draft resources. Not a complete patch.')


if __name__=='__main__':
    main()
