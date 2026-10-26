import unittest
import re
from compile_translation import ROOT, read, TOKEN
from terminology_473 import apply, RULES
from raw_text_codec import encode_display

class AttributeTerminologyTests(unittest.TestCase):
    def test_exact_source_controls_and_font(self):
        rows=read(ROOT/'translation/terminology_473.review.json')['rows']
        self.assertEqual(len(rows),61)
        self.assertEqual(sum(r['key'].startswith('export_dlc/') for r in rows),4)
        mapping=read(ROOT/'translation/font_encoding.hex.json')
        for r in rows:
            self.assertRegex(TOKEN.sub('',r['original']),'壊属性|壊耐性')
            self.assertEqual(TOKEN.findall(r['before']),TOKEN.findall(r['after']))
            self.assertEqual(apply(r['key'],r['original'],r['before']),r['after'])
            encode_display(TOKEN.sub('',r['after']),mapping)
        r=rows[0]
        with self.assertRaises(AssertionError):apply(r['key'],r['original'],'stale')
        self.assertEqual(apply('unrelated','精神的な打撃','受到打击'),'受到打击')

    def test_compiled_and_residual_terms(self):
        rows=read(ROOT/'translation/catalog.working.json')
        lookup={r['key']:r for r in rows}
        for r in read(ROOT/'translation/terminology_473.review.json')['rows']:
            self.assertEqual(lookup[r['key']]['translation'],r['after'])
        for r in rows:
            if re.search('壊属性|壊耐性',TOKEN.sub('',r['original'])) and r.get('translation'):
                self.assertIn('破坏属性',r['translation'])
                self.assertNotRegex(r['translation'],r'打击属性|坏击属性|(?<!破)坏属性|打击伤害|打击耐性|（打击）')

    def test_related_names_and_tables(self):
        from q2_name_banks import load
        banks=load()
        for group in banks['groups']:
            for r in group['rows']:
                if r['original'] in ('壊撃の鬼','壊撃の神'):
                    self.assertIn(r['translation'],('破坏之鬼','破坏之神'))
        for r in read(ROOT/'translation/tables.catalog.working.json'):
            if re.search('壊属性|壊耐性',r['original']):
                self.assertFalse(any(old in (r.get('translation') or '') for old,_ in RULES))

if __name__=='__main__':unittest.main()
