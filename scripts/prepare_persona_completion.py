"""One-time authored Persona completion; retain exact Q2-name provenance."""
import hashlib
from compile_translation import ROOT, read, write, LEADING, TRAILING
from persona_names import SOURCE, EXPECTED_SHA, DRAFT, parse, is_placeholder


def main():
    reference = ROOT.parent/'references/PersonaQ2ChsLocalization-latest-20260928/texts/zh_Hans/battle/table/personanametable.tbl.json'
    refs = read(reference)
    digest = hashlib.sha256(reference.read_bytes()).hexdigest()
    # Deliberately retain alternate transliterations; only targeted project decisions.
    overrides = {'オオミツヌ': '八束水臣津野命', 'イザナギノオオカミ': '伊邪那岐大神'}
    local = {'ナタク': '哪吒', '善': '善', '玲': '玲', 'ぬいぐるみ': '布偶'}
    data = (ROOT/'data'/SOURCE).read_bytes()
    assert hashlib.sha256(data).hexdigest() == EXPECTED_SHA
    entries = []
    for i, chunk in enumerate(parse(data)):
        name = chunk[:-1].decode('cp932')
        if is_placeholder(name):
            continue
        matches = [r for r in refs if r['original'] == name and r.get('translation')]
        variants = {r['translation'] for r in matches}
        assert len(variants) <= 1, (name, variants)
        value = overrides.get(name, next(iter(variants), local.get(name)))
        assert value is not None, name
        entries.append({'index': i, 'original': name, 'translation': value,
                        'references': [{'key': r['key'], 'translation': r['translation'], 'stage': r.get('stage')} for r in matches],
                        'amended': bool(variants and value not in variants)})
    batch_path = ROOT/'translation/batches/378_red_rider_compendium.generated.json'
    assert not DRAFT.exists() and not batch_path.exists(), 'Refusing to overwrite drafts'
    source = 'export_base/facility/datmyth.bmd.json'
    doc = read(ROOT/source)
    msg = doc['texts'][176]
    original = TRAILING.sub('', LEADING.sub('', msg['lines'][0]))
    width = max(map(len, original.splitlines()))
    chinese = '《约翰启示录》中记载的、世界终末时现身的四骑士之一。骑着红马，手持巨剑。被赋予夺走地上和平、使人们相互残杀的力量。'
    body = '\n'.join(chinese[i:i+width] for i in range(0, len(chinese), width)) + '\n'
    write(batch_path, {'status': 'draft', 'sources': {source: [[176, 0, msg['id'], body]]},
                      'source_hashes': {source: hashlib.sha256((ROOT/source).read_bytes()).hexdigest()},
                      'review_notes': ['红骑士图鉴：未找到二代精确同原文，依据一代日文直译。非占位条目。']})
    write(DRAFT, {'status': 'draft', 'source': SOURCE, 'source_sha256': EXPECTED_SHA,
                  'reference': str(reference.relative_to(ROOT.parent)), 'reference_sha256': digest,
                  'reference_commit': '15ca3ffda260133bfb090fc8a5b5ea896553f37c', 'entries': entries,
                  'notes': ['同日文名称精确复用，不按二代索引套用。重复及可能未使用条目保持各自索引，不代表全部可获得。',
                            '八束水臣津野命与图鉴68一致；伊邪那岐大神采用项目译名，不使用狼。',
                            '善、玲原文已为汉字，保留；布偶及哪吒无同名参考时本地翻译。',
                            '仅改名称银行，不修改成长、合体、技能或战斗参数。未运行验证。']})
    print(f'Prepared {len(entries)} name slots, {sum(bool(r["references"]) for r in entries)} exact-source reuse slots, 1 compendium entry.')


if __name__ == '__main__':
    main()
