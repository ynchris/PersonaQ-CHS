"""Verify partial floor translations leave deferred and development text intact."""
import hashlib
import re
import unittest
from compile_translation import ROOT, read, TOKEN
from reuse_parallel_story import body
from reviewed_test_expectations import authored_translation


class DungeonEventTests(unittest.TestCase):
    filename = '337_dungeon_rei_key_and_common_interactions.json'
    pairs = 3
    pages = 402

    def test_pairs_hashes_and_complete_accounting(self):
        batch = read(ROOT/'translation/batches'/self.filename)
        self.assertEqual(len(batch['provenance_pairs']), self.pairs)
        self.assertEqual(sum(map(len, batch['sources'].values())), self.pages)
        for left, right in batch['provenance_pairs']:
            self.assertEqual((ROOT/left).read_bytes(), (ROOT/right).read_bytes())
            self.assertEqual(batch['sources'][left], batch['sources'][right])
            self.assertEqual(batch['excluded_pages'][left], batch['excluded_pages'][right])
        for source, rows in batch['sources'].items():
            doc = read(ROOT/source)
            self.assertEqual(hashlib.sha256((ROOT/source).read_bytes()).hexdigest(), batch['source_hashes'][source])
            expected = {(i, j) for i, m in enumerate(doc['texts']) for j in range(len(m['lines']))}
            translated = {(i, j) for i, j, _, _ in rows}
            excluded = {(i, j) for i, j, _ in batch['excluded_pages'][source]}
            self.assertEqual(len(translated), len(rows))
            self.assertFalse(translated & excluded)
            self.assertEqual(expected, translated | excluded)

    def test_roundtrip_controls_speakers_and_untouched_exclusions(self):
        filename = self.filename
        batch = read(ROOT/'translation/batches'/filename)
        catalog = {r['key']: r for r in read(ROOT/'translation/catalog.working.json')}
        for source, rows in batch['sources'].items():
            original = read(ROOT/source)
            compiled = read(ROOT/'translation/compiled'/source)
            for i, j, mid, chinese in rows:
                row = catalog[f'{source}:{i}:{j}']
                self.assertEqual(mid, original['texts'][i]['id'])
                self.assertEqual(row['batch'], filename)
                self.assertEqual(body(row['translation']), chinese)
                self.assertEqual(row['translation'], compiled['texts'][i]['lines'][j])
                self.assertEqual(TOKEN.findall(row['original']), TOKEN.findall(row['translation']))
                self.assertEqual(chinese.count('\n'), body(row['original']).count('\n'))
                self.assertNotRegex(chinese, r'[\u3041-\u3096\u30a1-\u30fa]')
            for i, j, expected in batch['excluded_pages'][source]:
                self.assertEqual(body(original['texts'][i]['lines'][j]), expected)
                current_expected=authored_translation(source,i,j,original['texts'][i]['lines'][j])
                self.assertEqual(current_expected, compiled['texts'][i]['lines'][j])
                if current_expected==original['texts'][i]['lines'][j]:
                    self.assertFalse(catalog[f'{source}:{i}:{j}']['translation'])
                else:
                    self.assertNotEqual(catalog[f'{source}:{i}:{j}']['batch'],filename)
            expected_names = original['speakers'][:]
            for index, jp, cn in batch.get('speakers', {}).get(source, []):
                self.assertEqual(expected_names[index], jp)
                expected_names[index] = cn
            self.assertEqual(compiled['speakers'], expected_names)


class DungeonPuzzleTests(DungeonEventTests):
    filename = '338_dungeon_floor_puzzles_and_switches.json'
    pairs = 16
    pages = 268

    def test_four_guardian_order_and_elevator_numbers(self):
        batch = read(ROOT/'translation/batches'/self.filename)
        puzzles = 0
        for source, rows in batch['sources'].items():
            doc = read(ROOT/source)
            for i, j, _, chinese in rows:
                original = body(doc['texts'][i]['lines'][j])
                self.assertEqual(re.findall(r'[０-９]+', original), re.findall(r'[０-９]+', chinese))
                if '玄武' in original:
                    puzzles += 1
                    pattern = r'玄武|白虎|青龍|朱雀'
                    self.assertEqual(re.findall(pattern, original), re.findall(pattern, chinese.replace('青龙', '青龍')))
        self.assertEqual(puzzles, 32)


if __name__ == '__main__':
    unittest.main()
