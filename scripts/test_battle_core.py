import hashlib
import json
import unittest
from pathlib import Path
from compile_translation import LEADING, TRAILING, TOKEN
from reviewed_test_expectations import authored_translation

ROOT = Path(__file__).resolve().parent

class BattleCoreTests(unittest.TestCase):
    def test_authored_pages_and_preservation(self):
        batch = json.loads((ROOT/'translation/batches/343_battle_core_and_party_calls.json').read_text(encoding='utf-8'))
        self.assertEqual(sum(map(len, batch['sources'].values())), 668)
        a, b = batch['provenance_pairs'][0]
        self.assertEqual((ROOT/a).read_bytes(), (ROOT/b).read_bytes())
        self.assertEqual(batch['sources'][a], batch['sources'][b])
        for source, rows in batch['sources'].items():
            self.assertEqual(hashlib.sha256((ROOT/source).read_bytes()).hexdigest(), batch['source_hashes'][source])
            original = json.loads((ROOT/source).read_text(encoding='utf-8-sig'))
            compiled = json.loads((ROOT/'translation/compiled'/source).read_text(encoding='utf-8'))
            seen = set()
            for mi, li, mid, body in rows:
                self.assertNotIn(mi, seen)
                seen.add(mi)
                old = original['texts'][mi]['lines'][li]
                new = compiled['texts'][mi]['lines'][li]
                self.assertEqual(original['texts'][mi]['id'], mid)
                self.assertEqual(new, LEADING.match(old).group()+body+TRAILING.search(old).group())
                self.assertEqual(TOKEN.findall(old), TOKEN.findall(new))
                self.assertEqual(old.count('\n'), new.count('\n'))
            deferred = set()
            followup = json.loads((ROOT/'translation/batches/369_q2_battle_party_reuse.generated.json').read_text(encoding='utf-8'))
            additions = {(mi, li): body for mi, li, _, body in followup['sources'].get(source, [])}
            sweep=json.loads((ROOT/'translation/batches/384_q2_normalized_sweep.generated.json').read_text(encoding='utf-8'))
            additions.update({(i,j):v for i,j,_,v in sweep['sources'].get(source,[])})
            for mi, li, body in batch['deferred_pages'][source]:
                deferred.add(mi)
                old = original['texts'][mi]['lines'][li]
                self.assertEqual(TRAILING.sub('', LEADING.sub('', old)), body)
                expected = old
                if (mi, li) in additions:
                    expected = LEADING.match(old).group()+additions[(mi, li)]+TRAILING.search(old).group()
                self.assertEqual(authored_translation(source,mi,li,old), compiled['texts'][mi]['lines'][li])
            self.assertFalse(seen & deferred)
            self.assertEqual(seen | deferred, set(range(458)))
            self.assertEqual(compiled['speakers'], ['慈悲的圣职者'])

    def test_dynamic_subjects_and_party_calls(self):
        batch = json.loads((ROOT/'translation/batches/343_battle_core_and_party_calls.json').read_text(encoding='utf-8'))
        rows = {mi: body for mi, li, mid, body in next(iter(batch['sources'].values()))}
        self.assertEqual(rows[27], '受到{F2 44 03 01}点伤害！\n')
        self.assertEqual(rows[28], '点伤害！\n')
        self.assertEqual(rows[40], '呼唤了同伴！\n')
        self.assertTrue(set(range(348, 368)) <= rows.keys())
        self.assertTrue(set(range(379, 399)) <= rows.keys())
        self.assertIn('３', rows[421])
        self.assertIn('１', rows[406])

if __name__ == '__main__':
    unittest.main()
