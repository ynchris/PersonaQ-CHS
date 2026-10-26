import re,unittest
from compile_translation import ROOT,read,TOKEN
from audit_layout_metrics import measure,font_width_functions
from raw_text_codec import encode_message
from prepare_layout_453 import restore_controls

class LayoutTests(unittest.TestCase):
    def test_all_453_changes(self):
        rows=read(ROOT/'translation/layout_453.review.json')['rows'];self.assertEqual(len(rows),152)
        widths=font_width_functions();mapping=read(ROOT/'translation/font_encoding.hex.json')
        catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')}
        for row in rows:
            self.assertEqual(catalog[row['key']]['translation'],row['after'])
            self.assertEqual(TOKEN.findall(row['before']),TOKEN.findall(row['after']))
            if row['newline_only']:self.assertEqual(row['before'].replace('\n',''),row['after'].replace('\n',''))
            else:self.assertEqual(re.findall(r'[０-９]+',row['before']),re.findall(r'[０-９]+',row['after']))
            self.assertLessEqual(len(TOKEN.sub('',row['after']).splitlines()),len(TOKEN.sub('',row['original']).splitlines()))
            for a,b in widths.values():self.assertLessEqual(measure(row['after'],b)['max_width'],measure(row['original'],a)['max_width'])
            encode_message(row['after'],mapping)

    def test_color_boundaries(self):
        self.assertEqual(restore_controls('甲，{F2 01 03 01}乙丙{F2 01 01 01}。\n','甲，\n乙丙。\n'),
                         '甲，\n{F2 01 03 01}乙丙{F2 01 01 01}。\n')

    def test_compact_454(self):
        rows=read(ROOT/'translation/layout_454.review.json')['rows'];self.assertEqual(len(rows),3)
        widths=font_width_functions();mapping=read(ROOT/'translation/font_encoding.hex.json')
        for row in rows:
            self.assertEqual(TOKEN.findall(row['before']),TOKEN.findall(row['after']))
            for a,b in widths.values():self.assertLess(measure(row['after'],b)['max_width'],measure(row['before'],b)['max_width'])
            encode_message(row['after'],mapping)

if __name__=='__main__':unittest.main()
