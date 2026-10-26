"""Regression checks for reviewed skill descriptions, not runtime validation."""
import hashlib
import json
import re
import unicodedata
from pathlib import Path
import unittest
from compile_translation import LEADING, TRAILING, TOKEN
from reviewed_test_expectations import authored_translation

ROOT = Path(__file__).resolve().parent
SOURCE = 'export_base/init/datskillhelp.bmd.json'

class SkillPassiveTests(unittest.TestCase):
    def test_physical_and_recovery(self):
        batch = json.loads((ROOT/'translation/batches/352_skill_physical_and_recovery.json').read_text(encoding='utf-8'))
        original = json.loads((ROOT/SOURCE).read_text(encoding='utf-8-sig'))
        compiled = json.loads((ROOT/'translation/compiled'/SOURCE).read_text(encoding='utf-8-sig'))
        self.assertEqual(hashlib.sha256((ROOT/SOURCE).read_bytes()).hexdigest(), batch['source_hashes'][SOURCE])
        rows = batch['sources'][SOURCE]
        self.assertEqual(len(rows), 83)
        self.assertEqual(len({r[0] for r in rows}), 83)
        numbers = lambda s: re.findall(r'\d+', unicodedata.normalize('NFKC', TOKEN.sub('',s)))
        for mi, li, mid, body in rows:
            old = original['texts'][mi]['lines'][li]
            self.assertEqual(original['texts'][mi]['id'], mid)
            value = LEADING.match(old).group()+body+TRAILING.search(old).group()
            self.assertEqual(compiled['texts'][mi]['lines'][li], value)
            self.assertEqual(TOKEN.findall(old), TOKEN.findall(value))
            self.assertEqual(numbers(old), numbers(value))
            self.assertLessEqual(max(map(len,body.splitlines())), max(map(len,TOKEN.sub('',old).splitlines())))
        text = lambda i: compiled['texts'][i]['lines'][0]
        for i in [935,998]:
            self.assertEqual(text(i),authored_translation(SOURCE,i,0,original['texts'][i]['lines'][0]))
        for i, phrase in [(851,'敌我全体'),(918,'无视目标的抗性与强化'),(921,'６～１０次'),(924,'仅在本回合'),(985,'５０％'),(999,'仅一次'),(1004,'５０％以下')]:
            self.assertIn(phrase,text(i))

    def test_targets_and_statuses(self):
        batch = json.loads((ROOT/'translation/batches/351_skill_targets_and_statuses.json').read_text(encoding='utf-8'))
        original = json.loads((ROOT/SOURCE).read_text(encoding='utf-8-sig'))
        compiled = json.loads((ROOT/'translation/compiled'/SOURCE).read_text(encoding='utf-8-sig'))
        self.assertEqual(hashlib.sha256((ROOT/SOURCE).read_bytes()).hexdigest(), batch['source_hashes'][SOURCE])
        rows = batch['sources'][SOURCE]
        self.assertEqual(len(rows), 65)
        self.assertEqual(len({r[0] for r in rows}), 65)
        numbers = lambda s: re.findall(r'\d+', unicodedata.normalize('NFKC', TOKEN.sub('',s)))
        for mi, li, mid, body in rows:
            old = original['texts'][mi]['lines'][li]
            self.assertEqual(original['texts'][mi]['id'], mid)
            value = LEADING.match(old).group()+body+TRAILING.search(old).group()
            self.assertEqual(compiled['texts'][mi]['lines'][li], value)
            self.assertEqual(TOKEN.findall(old), TOKEN.findall(value))
            self.assertEqual(numbers(old), numbers(value))
            self.assertLessEqual(max(map(len,body.splitlines())), max(map(len,TOKEN.sub('',old).splitlines())))
        text = lambda i: compiled['texts'][i]['lines'][0]
        self.assertIn('３０％以下',text(715))
        self.assertIn('击中弱点并打倒',text(719))
        self.assertIn('强化越多',text(723))
        self.assertIn('１列目标',text(785))
        self.assertIn('２～４次',text(795))
        self.assertIn('６次',text(806))
        self.assertIn('所有目标',text(820))
        self.assertIn('１列目标',text(834))

    def test_resistances_and_followups(self):
        batch = json.loads((ROOT/'translation/batches/350_skill_resistances_and_followups.json').read_text(encoding='utf-8'))
        original = json.loads((ROOT/SOURCE).read_text(encoding='utf-8-sig'))
        compiled = json.loads((ROOT/'translation/compiled'/SOURCE).read_text(encoding='utf-8-sig'))
        self.assertEqual(hashlib.sha256((ROOT/SOURCE).read_bytes()).hexdigest(), batch['source_hashes'][SOURCE])
        rows = batch['sources'][SOURCE]
        self.assertEqual(len(rows), 104)
        self.assertEqual(len({r[0] for r in rows}), 104)
        for mi, li, mid, body in rows:
            old = original['texts'][mi]['lines'][li]
            self.assertEqual(original['texts'][mi]['id'], mid)
            self.assertNotRegex(old, 'ブランク|スキルID_|ダミー|文章不要|仕様カット')
            value = LEADING.match(old).group()+body+TRAILING.search(old).group()
            self.assertEqual(compiled['texts'][mi]['lines'][li], value)
            self.assertEqual(TOKEN.findall(old), TOKEN.findall(value))
            self.assertLessEqual(max(map(len,body.splitlines())), max(map(len,TOKEN.sub('',old).splitlines())))
        text = lambda i: compiled['texts'][i]['lines'][0]
        for i in [614,622]:
            self.assertEqual(text(i), original['texts'][i]['lines'][0])
        for i,pct in [(568,'１０％'),(569,'２０％'),(570,'３０％')]:
            self.assertIn(pct,text(i))
        for i in [659,660,*range(664,672)]:
            self.assertIn('３回合',text(i))
        for i in [616,618,620,624]:
            self.assertIn('后排',text(i))
        for a,b in [(564,565),(571,572),(573,574)]:
            self.assertEqual(text(a),text(b))

    def test_reviewed_batch_and_compiled_controls(self):
        batch = json.loads((ROOT/'translation/batches/349_skill_triggers_and_passives.json').read_text(encoding='utf-8'))
        original = json.loads((ROOT/SOURCE).read_text(encoding='utf-8-sig'))
        compiled = json.loads((ROOT/'translation/compiled'/SOURCE).read_text(encoding='utf-8-sig'))
        self.assertEqual(hashlib.sha256((ROOT/SOURCE).read_bytes()).hexdigest(), batch['source_hashes'][SOURCE])
        rows = batch['sources'][SOURCE]
        self.assertEqual(len(rows), 60)
        self.assertEqual(len({r[0] for r in rows}), 60)
        for mi, li, mid, body in rows:
            old = original['texts'][mi]['lines'][li]
            self.assertEqual(original['texts'][mi]['id'], mid)
            self.assertNotRegex(old, 'ブランク|スキルID_|文章不要|仕様カット')
            expected = LEADING.match(old).group()+body+TRAILING.search(old).group()
            self.assertEqual(compiled['texts'][mi]['lines'][li], expected)
            self.assertEqual(TOKEN.findall(old), TOKEN.findall(expected))
            self.assertLessEqual(max(map(len,body.splitlines())), max(map(len,TOKEN.sub('',old).splitlines())))

    def test_variants_and_conditions(self):
        doc = json.loads((ROOT/'translation/compiled'/SOURCE).read_text(encoding='utf-8-sig'))
        text = lambda i: doc['texts'][i]['lines'][0]
        for a,b in [(466,467),(482,483),(484,485),(494,495)]:
            self.assertEqual(text(a),text(b))
        self.assertIn('低概率',text(498))
        self.assertIn('中等概率',text(499))
        self.assertIn('高概率',text(501))
        self.assertIn('同一回合',text(472))
        self.assertIn('１次',text(516))
        self.assertIn('ＨＰ１',text(520))
        self.assertIn('仍然存活',text(521))

if __name__ == '__main__':
    unittest.main()
