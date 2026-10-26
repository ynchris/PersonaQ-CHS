"""Compile indexed, human-authored drafts; preserve and validate control streams.

Batch bodies exclude only the leading/trailing control runs. Internal controls
must be supplied unchanged, including order. Source exports are never modified.
"""
import copy
import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOKEN = re.compile(r'\{[0-9A-F ]+\}')
LEADING = re.compile(r'^(?:\{[0-9A-F ]+\})*')
TRAILING = re.compile(r'(?:\{[0-9A-F ]+\})*$')

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

def main():
    catalog = read(ROOT/'translation/catalog.generated.json')
    lookup = {row['key']: row for row in catalog}
    documents, translated, warnings = {}, {}, []
    correction_path=ROOT/'translation/text_corrections.review.json'
    corrections=read(correction_path)['rows'] if correction_path.exists() else []
    corrections_by_key={r['key']:r for r in corrections}
    assert len(corrections_by_key)==len(corrections), 'Duplicate reviewed correction'
    applied_corrections=set()
    translated_speakers={}
    def add(source, mi, li, value, author):
        key = f'{source}:{mi}:{li}'
        old = lookup[key]['original']
        if key in corrections_by_key:
            correction=corrections_by_key[key]
            if value != correction['before'] or old != correction['original']:
                raise ValueError(f'Stale reviewed correction: {key}')
            value=correction['after']
            applied_corrections.add(key)
        from terminology_459 import apply as apply_terminology
        value=apply_terminology('messages',key,value)
        from terminology_473 import apply as apply_attribute_terminology
        value=apply_attribute_terminology(key,old,value)
        from terminology_520 import apply as apply_arcana_terminology
        value=apply_arcana_terminology(key,old,value)
        from terminology_541 import apply as apply_enemy_terminology
        value=apply_enemy_terminology(key,old,value)
        from terminology_543 import apply as apply_other_enemy_terminology
        value=apply_other_enemy_terminology(key,old,value)
        from terminology_554 import apply as apply_storage_terminology
        value=apply_storage_terminology(key,old,value)
        from terminology_555 import apply as apply_npc_terminology
        value=apply_npc_terminology(key,old,value)
        from terminology_556 import apply as apply_sharing_terminology
        value=apply_sharing_terminology(key,old,value)
        if key in translated:
            raise ValueError(f'Duplicate translation: {key}')
        if TOKEN.findall(old) != TOKEN.findall(value):
            raise ValueError(f'Control mismatch: {key}')
        if '{' in TOKEN.sub('', value) or '}' in TOKEN.sub('', value):
            raise ValueError(f'Invalid control syntax: {key}')
        if not TOKEN.sub('', value).strip():
            raise ValueError(f'Empty translation: {key}')
        if re.search(r'[\u3041-\u3096\u30a1-\u30fa]', TOKEN.sub('', value)):
            warnings.append({'key': key, 'kind': 'remaining_kana'})
        def numbers(text):
            text=unicodedata.normalize('NFKC',TOKEN.sub('',text))
            return Counter(re.findall(r'\d+(?:\.\d+)?',text))
        if numbers(old)!=numbers(value):
            warnings.append({'key':key,'kind':'numeric_review','original':old,'translation':value})
        old_rows = TOKEN.sub('', old).splitlines()
        new_rows = TOKEN.sub('', value).splitlines()
        if len(new_rows) > len(old_rows) or max(map(len,new_rows),default=0) > max(map(len,old_rows),default=0):
            warnings.append({'key': key, 'kind': 'layout_review', 'original': old, 'translation': value})
        translated[key] = dict(translation=value, status='draft_control_checked', batch=author)
        if source not in documents:
            documents[source] = copy.deepcopy(read(ROOT/source))
        documents[source]['texts'][mi]['lines'][li] = value

    for batch_path in sorted((ROOT/'translation/batches').glob('*.json')):
        batch = read(batch_path)
        for source, expected_hash in batch.get('source_hashes', {}).items():
            if hashlib.sha256((ROOT/source).read_bytes()).hexdigest() != expected_hash:
                raise ValueError(f'Batch source hash changed: {batch_path.name}: {source}')
        for source, names in batch.get('speakers',{}).items():
            original=read(ROOT/source)
            if source not in documents:
                documents[source]=copy.deepcopy(original)
            for index, expected, chinese in names:
                key=f'{source}:speaker:{index}'
                if key in translated_speakers or original['speakers'][index]!=expected:
                    raise ValueError(f'Duplicate or changed speaker: {key}')
                if TOKEN.findall(expected)!=TOKEN.findall(chinese):
                    raise ValueError(f'Speaker control mismatch: {key}')
                documents[source]['speakers'][index]=chinese
                for msg in documents[source]['texts']:
                    if msg['speaker']==expected:
                        msg['speaker']=chinese
                translated_speakers[key]=chinese
        for source, rows in batch['sources'].items():
            doc = read(ROOT/source)
            for mi, li, expected_id, body in rows:
                msg = doc['texts'][mi]
                if msg['id'] != expected_id:
                    raise ValueError(f'Message ID changed: {source}:{mi}')
                old = msg['lines'][li]
                prefix, suffix = LEADING.match(old).group(), TRAILING.search(old).group()
                add(source, mi, li, prefix+body+suffix, batch_path.name)
    difficulty = read(ROOT/'translation/difficultyselect.zh-Hans.json')
    for mi, lines in enumerate(difficulty['messages']):
        for li, value in enumerate(lines):
            add('export_base/'+difficulty['source'], mi, li, value, 'difficultyselect.zh-Hans.json')
    # All validation completes before writing generated artifacts.
    assert applied_corrections==set(corrections_by_key), 'Unused reviewed correction'
    output = ROOT/'translation/compiled'
    for source, doc in documents.items():
        write(output/source, doc)
    for row in catalog:
        if row['key'] in translated:
            row.update(translated[row['key']])
    groups = Counter('/'.join(row['source'].split('/')[:2]) for row in catalog if row['key'] in translated)
    report = dict(catalog_lines=len(catalog), translated_draft_lines=len(translated), translated_speaker_entries=len(translated_speakers),
                  remaining_catalog_lines=len(catalog)-len(translated), changed_documents=len(documents),
                  by_group=dict(groups), warnings=warnings, binary_built=False, runtime_tested=False,
                  excludes='Images, raw tables and executable strings are not included in catalog totals.')
    report['reviewed_text_corrections']=len(applied_corrections)
    table_file=ROOT/'translation/tables.catalog.working.json'
    table_rows=[r for r in read(table_file) if r['status']=='draft_table_reviewed'] if table_file.exists() else []
    report['translated_table_draft_rows']=len(table_rows)
    from equipment_names import load_drafts
    equipment_names=load_drafts()[3]
    report['equipment_name_draft_rows']=len(equipment_names)
    from persona_names import load_drafts as load_persona_names
    persona_names=load_persona_names()[2]
    report['persona_name_draft_rows']=len(persona_names)
    from q2_name_banks import load as load_q2_names
    q2_names=[r['translation'] for g in load_q2_names()['groups'] for r in g['rows']]
    report['q2_name_bank_draft_slots']=len(q2_names)
    completion=ROOT/'translation/enemy_names_completion.review.json'
    report['local_enemy_name_completion_slots']=len(read(completion)['rows']) if completion.exists() else 0
    skill_completion=ROOT/'translation/skill_names_completion.review.json'
    report['local_skill_name_completion_slots']=len(read(skill_completion)['rows']) if skill_completion.exists() else 0
    report['q2_name_bank_count_note']='Combined name-bank total; local enemy/skill completion slots are local additions, not Q2 reuse.'
    from q2_item_names import load as load_extra_items
    extra_items=load_extra_items()
    report['q2_extra_item_name_slots']=len(extra_items)
    consumables=ROOT/'translation/consumable_names_completion.review.json'
    report['local_consumable_completion_slots']=len(read(consumables)['rows']) if consumables.exists() else 0
    item_completion=ROOT/'translation/item_names_completion.review.json'
    report['local_other_item_completion_slots']=len(read(item_completion)['rows']) if item_completion.exists() else 0
    from schoolwalk_names import load as load_schoolwalk
    schoolwalk=[r['translation'] for r in load_schoolwalk()['rows']]
    report['schoolwalk_title_slots']=len(schoolwalk)
    code_review=ROOT/'translation/code_ui_450.review.json'
    code_texts=[r['translation'] for f in read(code_review)['files'] for r in f['rows']] if code_review.exists() else []
    report['executable_ui_draft_slots']=len(code_texts)
    report['executable_ui_note']='Separate base/update in-place string drafts; outside message coverage. Not proof of full executable text coverage or runtime compatibility.'
    write(ROOT/'translation/catalog.working.json', catalog)
    write(ROOT/'translation/progress.generated.json', report)
    characters = ''.join(sorted(set(''.join(TOKEN.sub('',x['translation']) for x in translated.values())+''.join(TOKEN.sub('',x) for x in translated_speakers.values())+''.join(r['translation'] for r in table_rows))))
    characters=''.join(sorted(set(characters+''.join(equipment_names.values())+''.join(persona_names.values())+''.join(q2_names)+''.join(extra_items.values()))))
    characters=''.join(sorted(set(characters+''.join(schoolwalk)+''.join(code_texts))))
    write(ROOT/'translation/required_characters.generated.json', {'characters': characters, 'count': len(characters)})
    print(json.dumps({k:v for k,v in report.items() if k!='warnings'},ensure_ascii=False,indent=2))
    print(f'Layout/kana warnings: {len(warnings)}')

if __name__ == '__main__':
    main()
