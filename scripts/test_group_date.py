"""Check complete effective group-date dialogue and ordered choices."""
import hashlib
import re
import unittest
from compile_translation import ROOT, read, TOKEN
from reuse_parallel_story import body


class GroupDateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batches = [read(ROOT/'translation/batches'/name) for name in [
            '339_group_date_reactions_part1.json', '340_group_date_questions_and_choices.json',
            '341_group_date_reactions_part2.json', '342_group_date_final_preferences.json']]
        cls.catalog = {r['key']: r for r in read(ROOT/'translation/catalog.working.json')}

    def test_hashes_ids_controls_lines_and_compiled_text(self):
        counts = []
        for batch in self.batches:
            count = 0
            for source, rows in batch['sources'].items():
                original = read(ROOT/source)
                compiled = read(ROOT/'translation/compiled'/source)
                self.assertEqual(hashlib.sha256((ROOT/source).read_bytes()).hexdigest(), batch['source_hashes'][source])
                self.assertEqual(len(rows), len({(i, j) for i, j, _, _ in rows}))
                for i, j, mid, chinese in rows:
                    row = self.catalog[f'{source}:{i}:{j}']
                    self.assertEqual(mid, original['texts'][i]['id'])
                    self.assertEqual(body(row['translation']), chinese)
                    self.assertEqual(compiled['texts'][i]['lines'][j], row['translation'])
                    self.assertEqual(TOKEN.findall(row['original']), TOKEN.findall(row['translation']))
                    self.assertEqual(body(row['original']).count('\n'), chinese.count('\n'))
                    self.assertNotRegex(chinese, r'[\u3041-\u3096\u30a1-\u30fa]')
                    prefix = re.match(r'^(　\n(?:\{[0-9A-F ]+\})*)', body(row['original']))
                    if prefix:
                        self.assertTrue(chinese.startswith(prefix.group()))
                    count += 1
            counts.append(count)
        self.assertEqual(counts, [254, 77, 273, 17])

    def test_all_effective_reactions_and_questions_covered(self):
        for suffix, expected, omitted in [('bf', 527, 21), ('bmd', 94, 129)]:
            source = 'export_base/event/gcs.bin_gconSelectQuestion' + ('Message' if suffix == 'bmd' else '') + '.' + suffix + '.json'
            original = read(ROOT/source)
            compiled = read(ROOT/'translation/compiled'/source)
            done = pending = 0
            for i, message in enumerate(original['texts']):
                for j, text in enumerate(message['lines']):
                    row = self.catalog[f'{source}:{i}:{j}']
                    if row['translation']:
                        done += 1
                    else:
                        pending += 1
                        self.assertEqual(text, compiled['texts'][i]['lines'][j])
                        if suffix == 'bf':
                            self.assertNotRegex(TOKEN.sub('', body(text)), r'[\u3040-\u30ff\u4e00-\u9fff]')
                        else:
                            self.assertTrue(i in {2, 3, 5} or body(text).startswith('ダミー'))
            self.assertEqual((done, pending), (expected, omitted))

    def test_speakers_and_question_choice_order(self):
        batch = self.batches[0]
        source = next(iter(batch['sources']))
        original = read(ROOT/source)
        compiled = read(ROOT/'translation/compiled'/source)
        names = original['speakers'][:]
        for i, jp, cn in batch['speakers'][source]:
            self.assertEqual(names[i], jp)
            names[i] = cn
        self.assertEqual(compiled['speakers'], names)
        question_source = next(iter(self.batches[1]['sources']))
        expected = {11: ['性别有关系', '完全没关系！'],
                    25: ['红姜丝', '蛋白粉', '葱花'],
                    43: ['米饭', '面包', '甜甜圈'],
                    51: ['书道', '花道', '弓道']}
        for i, choices in expected.items():
            self.assertEqual(body(self.catalog[f'{question_source}:{i}:0']['translation']).splitlines(), choices)


if __name__ == '__main__':
    unittest.main()
