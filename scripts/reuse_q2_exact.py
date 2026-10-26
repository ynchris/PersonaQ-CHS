"""Inventory exact visible-body matches; card import uses conservative template gates."""
import hashlib
import re
import sys
import unicodedata
from collections import defaultdict, Counter
from compile_translation import ROOT, read, write, LEADING, TRAILING

REF = ROOT.parent / 'references/PersonaQ2ChsLocalization/texts/zh_Hans'

def body(text):
    return TRAILING.sub('', LEADING.sub('', text)).strip()

def main(reference_root=REF, output='translation/q2_exact_candidates.generated.json', min_length=4):
    index = defaultdict(list)
    for path in sorted(reference_root.rglob('*.json')):
        rows = read(path)
        if not isinstance(rows, list):
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get('original'), str):
                continue
            original = row['original'].strip()
            translation = row.get('translation', '').strip()
            if not translation or translation == original:
                continue
            index[original].append(dict(translation=translation, reference=path.relative_to(reference_root).as_posix(),
                                       reference_key=row.get('key'), stage=row.get('stage'),
                                       reference_sha256=digest))
    candidates = []
    for row in read(ROOT/'translation/catalog.working.json'):
        if row.get('translation'):
            continue
        original = body(row['original'])
        if len(original) < min_length or re.search(r'ID_|ブランク|ダミー|枠最後|[{}\[\]]', original):
            continue
        matches = index.get(original, [])
        if not matches:
            continue
        variants = sorted({r['translation'] for r in matches})
        reasons = []
        if len(variants) != 1:
            reasons.append('conflicting_translations')
        for value in variants:
            if re.search(r'[{}\[\]\u3041-\u3096\u30a1-\u30fa]', value):
                reasons.append('controls_or_kana')
        candidates.append(dict(key=row['key'], source=row['source'], original=original,
                               variants=variants, reasons=sorted(set(reasons)), references=matches))
    write(ROOT/output, candidates)
    print('Candidates:', len(candidates), 'unambiguous/plain:', sum(not r['reasons'] for r in candidates))
    print(Counter(r['source'] for r in candidates))

def import_cards():
    candidates = read(ROOT/'translation/q2_exact_candidates.generated.json')
    source = 'export_base/init/datskillcardhelp.bmd.json'
    doc = read(ROOT/source)
    current = {r['key']: r for r in read(ROOT/'translation/catalog.working.json')}
    selected, audit, rejected = [], [], []
    target = ROOT/'translation/batches/367_q2_exact_skill_cards.generated.json'
    if target.exists():
        raise ValueError('Batch already exists; do not overwrite reviewed work')
    def numbers(value):
        return Counter(re.findall(r'\d+', unicodedata.normalize('NFKC', value)))
    for candidate in candidates:
        if candidate['source'] != source:
            continue
        key = candidate['key']
        old = current[key]
        original = candidate['original']
        translated = candidate['variants'][0]
        reasons = list(candidate['reasons'])
        if old.get('translation') or body(old['original']) != original:
            reasons.append('already_translated_or_changed')
        if not re.fullmatch(r'[^\n“”]+スキル“[^\n“”]+”を\n習得できるスキルカード。', original):
            reasons.append('not_skill_card_template')
        if any(x in original for x in ('（', '）', '未使用', '未設定', 'テスト')):
            reasons.append('possible_internal_slot')
        if not all(x in translated for x in ('技能', '技能卡', '习得', '“', '”')):
            reasons.append('unexpected_translation_template')
        if numbers(original) != numbers(translated):
            reasons.append('numeric_mismatch')
        if len(translated.splitlines()) > len(original.splitlines()) or max(map(len, translated.splitlines())) > max(map(len, original.splitlines())):
            reasons.append('layout_review')
        if not any(r['reference'] == 'init/datskillcardhelp.bmd.json' for r in candidate['references']):
            reasons.append('different_reference_category')
        if reasons:
            rejected.append(dict(key=key, reasons=sorted(set(reasons))))
            continue
        for reference in candidate['references']:
            path = REF/reference['reference']
            assert hashlib.sha256(path.read_bytes()).hexdigest() == reference['reference_sha256']
        mi, li = old['message_index'], old['line_index']
        selected.append([mi, li, doc['texts'][mi]['id'], translated+'\n'])
        audit.append(candidate)
    batch = dict(status='draft', sources={source: selected},
                 source_hashes={source: hashlib.sha256((ROOT/source).read_bytes()).hexdigest()},
                 review_notes=['二代同原文技能卡说明复用；仅去除一代外层控制码及首尾空白后匹配，不做模糊匹配。',
                               '保留二代中文作为AI草稿；通过格式/数字/行宽筛选，不宣称技能译名已经人工定稿。',
                               '名称表尚需统一，参考来源及文件哈希见q2_skill_card_reuse.generated.json；不移植二代二进制。'])
    write(target, batch)
    write(ROOT/'translation/q2_skill_card_reuse.generated.json', dict(imported=len(selected), entries=audit, rejected=rejected,
          semantic_review_complete=False, runtime_tested=False))
    print(f'Imported {len(selected)} draft card descriptions; held {len(rejected)} exceptions.')

if __name__ == '__main__':
    import_cards() if '--import-cards' in sys.argv else main()
