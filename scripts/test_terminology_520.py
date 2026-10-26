import unittest
from compile_translation import ROOT,read,TOKEN
from terminology_520 import apply
from raw_text_codec import encode_display
class ArcanaTermTests(unittest.TestCase):
    def test_exact_rows_controls_and_encoding(self):
        rows=read(ROOT/'translation/terminology_520.review.json')['rows']
        self.assertEqual(len(rows),2)
        mapping=read(ROOT/'translation/font_encoding.hex.json')
        for r in rows:
            self.assertEqual(apply(r['key'],r['original'],r['before']),r['after'])
            self.assertEqual(TOKEN.findall(r['before']),TOKEN.findall(r['after']))
            encode_display(TOKEN.sub('',r['after']),mapping)
        with self.assertRaises(AssertionError):apply(rows[0]['key'],rows[0]['original'],'stale')
    def test_compiled_consistency(self):
        for name in ['catalog.working.json','tables.catalog.working.json']:
            rows=read(ROOT/'translation'/name)
            self.assertFalse(any('阿尔卡纳' in (r.get('translation') or '') for r in rows))
        lookup={r['key']:r for r in read(ROOT/'translation/catalog.working.json')}
        for r in read(ROOT/'translation/terminology_520.review.json')['rows']:
            self.assertEqual(lookup[r['key']]['translation'],r['after'])
if __name__=='__main__':unittest.main()
