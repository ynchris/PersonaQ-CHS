"""Check paired navigation resources, page coverage and compiled controls."""
import hashlib
import unittest
from compile_translation import ROOT, read, TOKEN
from reuse_parallel_story import body


class DungeonSupportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batches = list((ROOT/'translation/batches').glob('33[23456]_dungeon_support_*.json'))
        cls.catalog = {r['key']: r for r in read(ROOT/'translation/catalog.working.json')}

    def test_complete_index_hashes_and_duplicate_resources(self):
        self.assertEqual(len(self.batches), 5)
        total = 0
        for path in self.batches:
            batch = read(path)
            self.assertEqual(len(batch['provenance_pairs']), {'332': 5, '333': 5, '334': 5, '335': 3, '336': 2}[path.name[:3]])
            targets = set()
            for left, right in batch['provenance_pairs']:
                self.assertEqual((ROOT/left).read_bytes(), (ROOT/right).read_bytes())
                self.assertEqual(batch['sources'][left], batch['sources'][right])
                targets.update([left, right])
            self.assertEqual(targets, set(batch['sources']))
            self.assertEqual(targets, set(batch['source_hashes']))
            for source, rows in batch['sources'].items():
                self.assertEqual(hashlib.sha256((ROOT/source).read_bytes()).hexdigest(), batch['source_hashes'][source])
                original = read(ROOT/source)
                self.assertEqual(original['speakers'], [])
                expected = {(i, j) for i, m in enumerate(original['texts']) for j in range(len(m['lines']))}
                self.assertEqual(len(rows), len(expected))
                self.assertEqual(len(rows), len({(i, j) for i, j, _, _ in rows}))
                self.assertEqual(expected, {(i, j) for i, j, _, _ in rows})
                total += len(rows)
        self.assertEqual(total, 2190)

    def test_compiled_catalog_ids_controls_and_line_breaks(self):
        for path in self.batches:
            for source, rows in read(path)['sources'].items():
                original = read(ROOT/source)
                compiled = read(ROOT/'translation/compiled'/source)
                for i, j, mid, chinese in rows:
                    row = self.catalog[f'{source}:{i}:{j}']
                    self.assertEqual(original['texts'][i]['id'], mid)
                    self.assertEqual(row['batch'], path.name)
                    self.assertEqual(row['status'], 'draft_control_checked')
                    self.assertEqual(body(row['translation']), chinese)
                    self.assertEqual(compiled['texts'][i]['lines'][j], row['translation'])
                    self.assertEqual(TOKEN.findall(row['original']), TOKEN.findall(row['translation']))
                    self.assertEqual(body(row['original']).count('\n'), chinese.count('\n'))
                    self.assertNotRegex(chinese, r'[\u3041-\u3096\u30a1-\u30fa]')

    def test_repeated_prompts_preserve_text_and_original_break_variants(self):
        normalize = lambda s: s.replace('\n', '').replace('　', '')
        for path in self.batches:
            for source, rows in read(path)['sources'].items():
                original = read(ROOT/source)
                seen = {}
                for i, j, _, chinese in rows:
                    key = normalize(body(original['texts'][i]['lines'][j]))
                    if key in seen:
                        self.assertEqual(normalize(chinese), seen[key])
                    seen[key] = normalize(chinese)


if __name__ == '__main__':
    unittest.main()
