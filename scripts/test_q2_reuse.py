import hashlib
import unittest
from compile_translation import ROOT, read
from reuse_q2_exact import REF, body


class Q2ReuseTests(unittest.TestCase):
    def test_short_choices_381(self):
        from compile_translation import LEADING, TRAILING, TOKEN
        p=ROOT/'translation/q2_reuse_381.review.json'
        plan=read(p)
        audit=read(ROOT/'translation/381_q2_short_choices_and_prompts.audit.generated.json')
        self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),audit['plan_sha256'])
        self.assertEqual(len(audit['entries']),23)
        batch=read(ROOT/'translation/batches'/plan['batch'])
        rows={f'{s}:{i}:{j}':v for s,rs in batch['sources'].items() for i,j,_,v in rs}
        cache={}
        for e in audit['entries']:
            i,j=e['key'].rsplit(':',2)[1:]
            slot=i+':'+j if j!='0' else i
            value=plan['overrides'].get(e['source'],{}).get(slot,e['variants'][0])
            self.assertEqual(value,e['final_body'].strip())
            self.assertEqual(rows[e['key']],e['final_body'])
            old=read(ROOT/e['source'])['texts'][int(i)]['lines'][int(j)]
            actual=read(ROOT/'translation/compiled'/e['source'])['texts'][int(i)]['lines'][int(j)]
            self.assertEqual(actual,LEADING.match(old).group()+e['final_body']+TRAILING.search(old).group())
            self.assertEqual(TOKEN.findall(old),TOKEN.findall(actual))
            self.assertLessEqual(max(map(len,TOKEN.sub('',actual).splitlines())),max(map(len,TOKEN.sub('',old).splitlines())))
            for ref in e['references']:
                path=ROOT/plan['reference_root']/ref['reference']
                if path not in cache:
                    cache[path]=(hashlib.sha256(path.read_bytes()).hexdigest(),read(path))
                digest,items=cache[path]
                self.assertEqual(digest,ref['reference_sha256'])
                self.assertTrue(any(r['key']==ref['reference_key'] and r['original'].strip()==e['original'] and r['translation'].strip()==ref['translation'] for r in items))

    def test_latest_return_items_skills_380(self):
        from compile_translation import TOKEN
        plan_path=ROOT/'translation/q2_reuse_380.review.json'
        plan=read(plan_path)
        audit=read(ROOT/'translation/380_q2_return_items_skills.audit.generated.json')
        self.assertEqual(audit['plan_sha256'],hashlib.sha256(plan_path.read_bytes()).hexdigest())
        self.assertEqual(len(audit['entries']),15)
        compiled={r['key']:r for r in read(ROOT/'translation/catalog.working.json')}
        for entry in audit['entries']:
            value=entry['variants'][0]
            for a,b in plan['replacements'].items():
                value=value.replace(a,b)
            mi,li=entry['key'].rsplit(':',2)[1:]
            slot=mi+':'+li if li!='0' else mi
            value=plan['overrides'].get(entry['source'],{}).get(slot,value)
            self.assertEqual(value,entry['final_body'].strip())
            self.assertEqual(body(compiled[entry['key']]['translation']),value)
            for ref in entry['references']:
                path=ROOT/plan['reference_root']/ref['reference']
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),ref['reference_sha256'])
                self.assertTrue(any(r['key']==ref['reference_key'] and r['original'].strip()==entry['original'] and r['translation'].strip()==ref['translation'] for r in read(path)))
            self.assertLessEqual(max(map(len,value.splitlines())),max(map(len,entry['original'].splitlines())))
        keys={e['key'] for e in audit['entries']}
        self.assertFalse(any('datquestdetail' in k for k in keys))

    def test_provenance_and_exact_source(self):
        audit = read(ROOT/'translation/q2_skill_card_reuse.generated.json')
        batch = read(ROOT/'translation/batches/367_q2_exact_skill_cards.generated.json')
        rows = {f'{s}:{mi}:{li}': text for s, values in batch['sources'].items() for mi, li, _, text in values}
        catalog = {r['key']: r for r in read(ROOT/'translation/catalog.generated.json')}
        self.assertEqual(len(rows), 482)
        self.assertEqual(set(rows), {r['key'] for r in audit['entries']})
        cache = {}
        for entry in audit['entries']:
            self.assertEqual(entry['reasons'], [])
            self.assertEqual(body(catalog[entry['key']]['original']), entry['original'])
            self.assertEqual(rows[entry['key']].strip(), entry['variants'][0])
            for ref in entry['references']:
                path = REF/ref['reference']
                if path not in cache:
                    cache[path] = (hashlib.sha256(path.read_bytes()).hexdigest(), read(path))
                digest, items = cache[path]
                self.assertEqual(digest, ref['reference_sha256'])
                matched = [r for r in items if r['key'] == ref['reference_key']]
                self.assertTrue(any(r['original'].strip() == entry['original'] and r['translation'].strip() == entry['variants'][0] for r in matched))
        self.assertFalse(set(rows) & {r['key'] for r in audit['rejected']})

    def test_only_outer_controls_are_removed(self):
        self.assertEqual(body('{F1 41}日文\n{00}'), '日文')
        self.assertEqual(body('{F1 41}日{F1 81}文{00}'), '日{F1 81}文')

    def check_compendium_phrase_fixes(self, number, count):
        plan_path = ROOT/f'translation/q2_reuse_{number}.review.json'
        plan = read(plan_path)
        audit = read(ROOT/'translation'/plan['batch'].replace('.generated.json', '.audit.generated.json'))
        self.assertEqual(audit['plan_sha256'], hashlib.sha256(plan_path.read_bytes()).hexdigest())
        self.assertEqual(len(audit['entries']), count)
        path = (ROOT/plan['reference_root'])/'facility/datmyth.bmd.json'
        digest, reference = hashlib.sha256(path.read_bytes()).hexdigest(), read(path)
        for entry in audit['entries']:
            mi = entry['key'].rsplit(':', 2)[1]
            value = entry['variants'][0].replace('\n','')
            for old, new in plan['phrase_fixes'].get(entry['source'], {}).get(mi, []):
                self.assertIn(old, value)
                value = value.replace(old, new)
            value = plan['overrides'].get(entry['source'], {}).get(mi, value)
            self.assertEqual(value, entry['final_body'].replace('\n',''))
            for ref in entry['references']:
                self.assertEqual(ref['reference_sha256'], digest)
                self.assertTrue(any(r['key'] == ref['reference_key'] and r['original'].strip() == entry['original'] and r['translation'].strip() == ref['translation'] for r in reference))
        return plan, audit

    def test_latest_compendium_phrase_fixes(self):
        plan, audit = self.check_compendium_phrase_fixes(373, 45)
        selected = set(plan['selections']['export_base/facility/datmyth.bmd.json'])
        self.assertFalse(selected & {54, 66, 68})
        fix = next(e for e in audit['entries'] if e['key'].endswith(':52:0'))
        self.assertIn('始终不会腐败', fix['final_body'].replace('\n',''))

    def test_compendium_97_120(self):
        plan, audit = self.check_compendium_phrase_fixes(374, 24)
        self.assertEqual(plan['selections']['export_base/facility/datmyth.bmd.json'], list(range(97, 121)))
        values = {e['key'].rsplit(':', 2)[1]: e['final_body'].replace('\n','') for e in audit['entries']}
        self.assertIn('只有以魔术之力才能治愈', values['98'])
        self.assertIn('伊邪那美派去追赶伊邪那岐', values['110'])
        self.assertIn('黄泉丑女', values['110'])

    def test_compendium_121_144(self):
        plan, audit = self.check_compendium_phrase_fixes(375, 24)
        self.assertEqual(plan['selections']['export_base/facility/datmyth.bmd.json'], list(range(121, 145)))
        values = {e['key'].rsplit(':', 2)[1]: e['final_body'].replace('\n','') for e in audit['entries']}
        self.assertIn('含义相互矛盾', values['121'])
        self.assertIn('像羊', values['127'])
        self.assertIn('被希伯来的神贬低', values['140'])

    def test_compendium_377_preserves_kronos_translation(self):
        plan, audit = self.check_compendium_phrase_fixes(377, 26)
        value = next(e['final_body'].replace('\n', '') for e in audit['entries'] if e['key'].endswith(':186:0'))
        self.assertIn('克洛诺斯', value)
        self.assertNotIn('柯罗诺斯', value)
        batch = read(ROOT/'translation/batches'/plan['batch'])
        text = next(r[3] for r in batch['sources']['export_base/facility/datmyth.bmd.json'] if r[0] == 186)
        self.assertEqual(text.replace('\n', ''), value)

    def test_compendium_145_168(self):
        plan, audit = self.check_compendium_phrase_fixes(376, 24)
        self.assertEqual(plan['selections']['export_base/facility/datmyth.bmd.json'], list(range(145, 169)))
        values = {e['key'].rsplit(':', 2)[1]: e['final_body'].replace('\n','') for e in audit['entries']}
        self.assertIn('为防止', values['153'])
        self.assertIn('以祭品换取', values['156'])
        self.assertIn('若是喜欢召唤者', values['158'])
        self.assertIn('儿子荷鲁斯', values['165'])

    def test_latest_compendium_reference(self):
        plan_path = ROOT/'translation/q2_reuse_372.review.json'
        plan = read(plan_path)
        audit = read(ROOT/'translation/372_q2_latest_compendium.audit.generated.json')
        self.assertEqual(audit['plan_sha256'], hashlib.sha256(plan_path.read_bytes()).hexdigest())
        self.assertEqual(plan['reference_commit'], '15ca3ffda260133bfb090fc8a5b5ea896553f37c')
        self.assertEqual(len(audit['entries']), 24)
        path = (ROOT/plan['reference_root'])/'facility/datmyth.bmd.json'
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        reference = read(path)
        for entry in audit['entries']:
            mi = entry['key'].rsplit(':', 2)[1]
            value = entry['variants'][0]
            for old, new in plan['replacements'].items():
                value = value.replace(old, new)
            value = plan['overrides'][entry['source']].get(mi, value)
            self.assertEqual(value.replace('\n',''), entry['final_body'].replace('\n',''))
            for ref in entry['references']:
                self.assertEqual(ref['reference_sha256'], digest)
                self.assertTrue(any(r['key'] == ref['reference_key'] and r['original'].strip() == entry['original'] and r['translation'].strip() == ref['translation'] for r in reference))
        self.assertIn('儿子兼第２任丈夫', plan['overrides']['export_base/facility/datmyth.bmd.json']['44'])

    def test_compendium_review(self):
        plan_path = ROOT/'translation/q2_reuse_370.review.json'
        plan = read(plan_path)
        audit = read(ROOT/'translation/370_q2_persona_compendium.audit.generated.json')
        self.assertEqual(audit['plan_sha256'], hashlib.sha256(plan_path.read_bytes()).hexdigest())
        self.assertEqual(len(audit['entries']), 27)
        cache = {}
        for entry in audit['entries']:
            mi, li = entry['key'].rsplit(':', 2)[1:]
            slot = mi+':'+li if li != '0' else mi
            value = plan['overrides'].get(entry['source'], {}).get(slot, entry['variants'][0])
            if entry['source'] in plan['reflow_sources']:
                width = max(map(len, entry['original'].splitlines()))
                compact = value.replace('\n', '')
                value = '\n'.join(compact[i:i+width] for i in range(0, len(compact), width))
            self.assertEqual(value.strip(), entry['final_body'].strip())
            for ref in entry['references']:
                path = REF/ref['reference']
                if path not in cache:
                    cache[path] = (hashlib.sha256(path.read_bytes()).hexdigest(), read(path))
                digest, items = cache[path]
                self.assertEqual(digest, ref['reference_sha256'])
                self.assertTrue(any(r['key'] == ref['reference_key'] and r['original'].strip() == entry['original'] and r['translation'].strip() == ref['translation'] for r in items))
        fixes = plan['overrides']['export_base/facility/datmyth.bmd.json']
        self.assertIn('猿田彦', fixes['3'])
        self.assertIn('5000', fixes['4'])
        self.assertIn('６４', fixes['21'])

    def test_battle_party_review(self):
        plan_path = ROOT/'translation/q2_reuse_369.review.json'
        plan = read(plan_path)
        audit = read(ROOT/'translation/369_q2_battle_party_reuse.audit.generated.json')
        self.assertEqual(audit['plan_sha256'], hashlib.sha256(plan_path.read_bytes()).hexdigest())
        batch = read(ROOT/'translation/batches'/plan['batch'])
        rows = {f'{s}:{mi}:{li}': text for s, values in batch['sources'].items() for mi, li, _, text in values}
        self.assertEqual(len(rows), 43)
        self.assertEqual(set(rows), {r['key'] for r in audit['entries']})
        cache = {}
        for entry in audit['entries']:
            self.assertEqual(rows[entry['key']], entry['final_body'])
            mi, li = entry['key'].rsplit(':', 2)[1:]
            slot = mi+':'+li if li != '0' else mi
            value = entry['variants'][0]
            for old, new in plan['replacements'].items():
                value = value.replace(old, new)
            value = plan['overrides'].get(entry['source'], {}).get(slot, value)
            self.assertEqual(value.strip(), entry['final_body'].strip())
            for ref in entry['references']:
                path = REF/ref['reference']
                if path not in cache:
                    cache[path] = (hashlib.sha256(path.read_bytes()).hexdigest(), read(path))
                digest, items = cache[path]
                self.assertEqual(digest, ref['reference_sha256'])
                self.assertTrue(any(r['key'] == ref['reference_key'] and r['original'].strip() == entry['original'] and r['translation'].strip() == ref['translation'] for r in items))
        for mi in plan['selections']['export_base/battle/message/battlemessage.bmd.json']:
            self.assertEqual(rows[f'export_base/battle/message/battlemessage.bmd.json:{mi}:0'], rows[f'export_base/battle/pack/btl_com.arc_battlemessage.bmd.json:{mi}:0'])
        self.assertIn('人数越多', rows['export_base/battle/result/persona_get.bin_persona_get.bmd.json:3:1'])
        self.assertIn('不保存', rows['export_base/facility/party_edit_msg.bmd.json:5:0'])

    def test_quest_material_review(self):
        plan_path = ROOT/'translation/q2_reuse_368.review.json'
        plan = read(plan_path)
        audit = read(ROOT/'translation/368_q2_quest_material_reuse.audit.generated.json')
        self.assertEqual(audit['plan_sha256'], hashlib.sha256(plan_path.read_bytes()).hexdigest())
        batch = read(ROOT/'translation/batches'/plan['batch'])
        rows = {f'{s}:{mi}:{li}': text for s, values in batch['sources'].items() for mi, li, _, text in values}
        self.assertEqual(len(rows), 50)
        self.assertEqual(set(rows), {r['key'] for r in audit['entries']})
        cache = {}
        for entry in audit['entries']:
            self.assertEqual(rows[entry['key']], entry['final_body'])
            value = entry['variants'][0]
            for old, new in plan['replacements'].items():
                value = value.replace(old, new)
            mi = entry['key'].rsplit(':', 2)[1]
            value = plan['overrides'].get(entry['source'], {}).get(mi, value)
            self.assertEqual(value.strip(), entry['final_body'].strip())
            for ref in entry['references']:
                path = REF/ref['reference']
                if path not in cache:
                    cache[path] = (hashlib.sha256(path.read_bytes()).hexdigest(), read(path))
                digest, items = cache[path]
                self.assertEqual(digest, ref['reference_sha256'])
                self.assertTrue(any(r['key'] == ref['reference_key'] and r['original'].strip() == entry['original'] and r['translation'].strip() == entry['variants'][0] for r in items))
        source = 'export_base/init/dateventitemhelp.bmd.json'
        self.assertIn('性质', rows[source+':153:0'])
        self.assertIn('终点', rows[source+':190:0'])
        self.assertIn('减免１０％', rows[source+':201:0'])
        self.assertIn('仅能为主角', rows[source+':208:0'])
        self.assertNotIn(source+':193:0', rows)


if __name__ == '__main__':
    unittest.main()
