"""Audit exact-route reuse against its pinned sources and compiled catalog."""
import hashlib
import re
import unittest
from compile_translation import ROOT, read, TOKEN, LEADING, TRAILING
from reuse_parallel_story import body, name_safe
from reviewed_test_expectations import before_review


class ParallelReuseTests(unittest.TestCase):
    def test_outer_name_controls_excluded(self):
        for token in ('{F1 81}', '{F1 82}', '{F5 C1 0A 00}', '{F5 C1 0E 00}', '{F5 C1 10 00}'):
            self.assertFalse(name_safe(token+'text'))
            self.assertFalse(name_safe('text'+token))

    def test_internal_controls_preserved(self):
        self.assertEqual(body('{F1 00}abc{F1 81}xyz{F1 01}'), 'abc{F1 81}xyz')

    def test_reuse_evidence(self):
        report = read(ROOT/'translation/parallel_reuse_review.generated.json')
        rows = {r['key']:r for r in read(ROOT/'translation/catalog.working.json')}
        self.assertEqual(report['count'], len(report['matches']))
        self.assertEqual(len({m['target_key'] for m in report['matches']}), report['count'])
        for path, digest in report['source_hashes'].items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(), digest)
        for m in report['matches']:
            src, dst = rows[m['source_key']], rows[m['target_key']]
            self.assertEqual(re.sub(r'/e([1-6])10_', r'/e\g<1>00_', dst['source']), src['source'])
            self.assertEqual(src['speaker'], dst['speaker'])
            self.assertEqual(body(src['original']), body(dst['original']))
            self.assertEqual(body(before_review(src['key'],src['translation'])), m['translation'])
            self.assertEqual(body(before_review(dst['key'],dst['translation'])), m['translation'])
            self.assertTrue(name_safe(src['original']) and name_safe(dst['original']))
            self.assertGreaterEqual(len(TOKEN.sub('', m['original']).strip()), 12)
            self.assertEqual(TOKEN.findall(dst['translation']), TOKEN.findall(dst['original']))
            self.assertEqual(LEADING.match(dst['translation']).group(), LEADING.match(dst['original']).group())
            self.assertEqual(TRAILING.search(dst['translation']).group(), TRAILING.search(dst['original']).group())


if __name__ == '__main__':
    unittest.main()
