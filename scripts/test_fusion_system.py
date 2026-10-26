import hashlib
import json
import re
import unicodedata
import unittest
from collections import Counter
from pathlib import Path
from compile_translation import LEADING, TRAILING, TOKEN
from reviewed_test_expectations import authored_translation

ROOT = Path(__file__).resolve().parent

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

class FusionSystemTests(unittest.TestCase):
    def setUp(self):
        self.batch = read(ROOT/'translation/batches/344_fusion_compendium_and_streetpass.json')

    def test_full_partition_controls_and_compiled_output(self):
        self.assertEqual(sum(map(len, self.batch['sources'].values())), 370)
        for source, rows in self.batch['sources'].items():
            self.assertEqual(hashlib.sha256((ROOT/source).read_bytes()).hexdigest(), self.batch['source_hashes'][source])
            old = read(ROOT/source)
            new = read(ROOT/'translation/compiled'/source)
            selected = set()
            for mi, li, mid, body in rows:
                self.assertNotIn((mi, li), selected)
                selected.add((mi, li))
                self.assertEqual(old['texts'][mi]['id'], mid)
                original = old['texts'][mi]['lines'][li]
                value = new['texts'][mi]['lines'][li]
                self.assertEqual(value, LEADING.match(original).group()+body+TRAILING.search(original).group())
                self.assertEqual(TOKEN.findall(original), TOKEN.findall(value))
                self.assertEqual(original.count('\n'), value.count('\n'))
                numbers = lambda s: Counter(re.findall(r'\d+', unicodedata.normalize('NFKC', TOKEN.sub('', s))))
                self.assertEqual(numbers(original), numbers(value))
            deferred = set()
            followup = read(ROOT/'translation/batches/370_q2_persona_compendium.generated.json')
            additions = {(mi, li): body for mi, li, _, body in followup['sources'].get(source, [])}
            prompt_followup = read(ROOT/'translation/batches/379_party_persona_prompts.generated.json')
            additions.update({(mi, li): body for mi, li, _, body in prompt_followup['sources'].get(source, [])})
            for mi, li, body in self.batch['deferred_pages'][source]:
                deferred.add((mi, li))
                original = old['texts'][mi]['lines'][li]
                self.assertEqual(body, TRAILING.sub('', LEADING.sub('', original)))
                expected = original
                if (mi, li) in additions:
                    expected = LEADING.match(original).group()+additions[(mi, li)]+TRAILING.search(original).group()
                self.assertEqual(authored_translation(source,mi,li,original), new['texts'][mi]['lines'][li])
            self.assertFalse(selected & deferred)
            self.assertEqual(selected | deferred, {(i,j) for i,m in enumerate(old['texts']) for j in range(len(m['lines']))})
            for i, jp, zh in self.batch.get('speakers', {}).get(source, []):
                self.assertEqual(old['speakers'][i], jp)
                self.assertEqual(new['speakers'][i], zh)

    def test_discount_and_streetpass_rules(self):
        source = 'export_base/facility/msg_combine.bmd.json'
        rows = {(mi, li): body for mi, li, mid, body in self.batch['sources'][source]}
        for a,b,pct in [(69,220,'１０'),(70,221,'１５'),(71,222,'２０'),(72,223,'２５')]:
            for mi in (a,b):
                matches = [v for (i,j),v in rows.items() if i == mi and pct+'％' in v]
                self.assertEqual(len(matches), 1)
                self.assertIn('减免', matches[0])
        for mi in (214,215):
            self.assertTrue(any('保护' in v for (i,j),v in rows.items() if i == mi))
        self.assertIn('无法由你亲自登记', rows[239,0])
        self.assertIn('消失', rows[202,2])
        self.assertNotIn((187,0), rows)
        self.assertNotIn((236,0), rows)
        self.assertEqual(rows[0,0], '是')
        self.assertEqual(rows[0,1], '否')

if __name__ == '__main__':
    unittest.main()
