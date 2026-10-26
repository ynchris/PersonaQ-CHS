"""Verify authored boss dialogue and intentional placeholder exclusions."""
import copy
import unittest
from compile_translation import ROOT, read, TOKEN
from compile_boss_drafts import compile_draft
from reuse_parallel_story import body


class BossDraftTests(unittest.TestCase):
    def drafts(self):
        return [read(p) for p in (ROOT/'translation/boss_drafts').glob('*.json')]

    def test_catalog_and_speakers(self):
        catalog = {r['key']: r for r in read(ROOT/'translation/catalog.working.json')}
        self.assertTrue(self.drafts())
        for draft in self.drafts():
            compile_draft(draft)
            source = draft['source']
            compiled = read(ROOT/'translation/compiled'/source)
            original = read(ROOT/source)
            self.assertEqual(compiled['speakers'], [draft['speaker_names'][jp] for jp in original['speakers']])
            for i, j, text in draft['pages']:
                row = catalog[f'{source}:{i}:{j}']
                self.assertEqual(row['batch'], draft['batch'])
                self.assertEqual(body(row['translation']), text)
                self.assertEqual(TOKEN.findall(row['original']), TOKEN.findall(row['translation']))
            for i, j, expected in draft['excluded_placeholders']:
                self.assertFalse(catalog[f'{source}:{i}:{j}']['translation'])
                self.assertEqual(compiled['texts'][i]['lines'][j], original['texts'][i]['lines'][j])

    def test_rejects_missing_duplicate_and_control_changes(self):
        original = self.drafts()[0]
        bad = copy.deepcopy(original)
        bad['pages'].pop()
        with self.assertRaises(AssertionError):
            compile_draft(bad)
        bad = copy.deepcopy(original)
        bad['pages'].append(bad['pages'][0])
        with self.assertRaises(AssertionError):
            compile_draft(bad)
        bad = copy.deepcopy(original)
        bad['pages'][0][2] += '{F1 21}'
        with self.assertRaises(AssertionError):
            compile_draft(bad)

    def test_rejects_wrong_hash_and_false_placeholder(self):
        bad = copy.deepcopy(self.drafts()[0])
        bad['sha256'] = '0' * 64
        with self.assertRaises(AssertionError):
            compile_draft(bad)
        bad = copy.deepcopy(self.drafts()[0])
        i, j, text = bad['pages'].pop(0)
        bad['excluded_placeholders'].append([i, j, text])
        with self.assertRaises(AssertionError):
            compile_draft(bad)


if __name__ == '__main__':
    unittest.main()
