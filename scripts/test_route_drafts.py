"""Audit authored route differences and deliberate developer-placeholder omissions."""
import hashlib
import unittest
from compile_translation import ROOT, read, LEADING, TRAILING, TOKEN
from reuse_parallel_story import body
from reviewed_test_expectations import before_review

class RouteDraftTests(unittest.TestCase):
    def test_authored_pages_match_compiled_catalog(self):
        catalog = {r['key']:r for r in read(ROOT/'translation/catalog.working.json')}
        used = set()
        for path in (ROOT/'translation/route_drafts').glob('*.json'):
            draft = read(path)
            for code, scene in draft['scenes'].items():
                source = f'export_base/event/e{code[1]}00/{code}.bf.json'
                self.assertEqual(hashlib.sha256((ROOT/source).read_bytes()).hexdigest(), scene['sha256'])
                for mi, li, zh in scene['pages']:
                    key = f'{source}:{mi}:{li}'
                    self.assertNotIn(key, used)
                    used.add(key)
                    row = catalog[key]
                    self.assertEqual(row['batch'], draft['batch'])
                    self.assertEqual(body(before_review(key,row['translation'])), zh)
                    self.assertEqual(TOKEN.findall(row['original']), TOKEN.findall(row['translation']))
                    self.assertEqual(LEADING.match(row['original']).group(), LEADING.match(row['translation']).group())
                    self.assertEqual(TRAILING.search(row['original']).group(), TRAILING.search(row['translation']).group())
        self.assertTrue(used)

    def test_omitted_placeholders_remain_untranslated(self):
        catalog = {r['key']:r for r in read(ROOT/'translation/catalog.working.json')}
        allowed = {'＞一枚絵イベントです。\n','＞一枚絵のイベントです。\n','＞特殊イベントです。\n','＞特別演出のイベントです。\n','＞アニメイベントです。\n'}
        for path in (ROOT/'translation/story').glob('*.json'):
            draft = read(path)
            for mi in draft.get('excluded_placeholder_indices', []):
                row = catalog[f'{draft["source"]}:{mi}:0']
                self.assertIn(body(row['original']), allowed)
                self.assertFalse(row['translation'])

    def test_route_speaker_inventory_complete(self):
        names = {jp:zh for p in (ROOT/'translation/story').glob('*.json') for jp,zh in read(p)['speaker_names'].items()}
        for p in (ROOT/'translation/route_drafts').glob('*.json'):
            names.update(read(p).get('speaker_names', {}))
        for path in (ROOT/'translation/route_drafts').glob('*.json'):
            draft = read(path)
            batch = read(ROOT/'translation/batches'/draft['batch'])
            for source in batch['sources']:
                doc = read(ROOT/source)
                translated = {i:zh for i,jp,zh in batch['speakers'][source]}
                for i, jp in enumerate(doc['speakers']):
                    self.assertIn(jp, names)
                    if names[jp] != jp:
                        self.assertIn(i, translated, (source, jp))
                        self.assertEqual(translated[i], names[jp])

if __name__ == '__main__':
    unittest.main()
