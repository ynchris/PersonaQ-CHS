import unittest
from compile_translation import ROOT,read,TOKEN,LEADING,TRAILING
from audit_layout_metrics import measure,font_width_functions
from raw_text_codec import encode_message
from prepare_reflow_452 import valid_break


class ReflowTests(unittest.TestCase):
    def test_all_reflows_preserve_content_and_font_bounds(self):
        rows=read(ROOT/'translation/reflow_452.review.json')['rows']
        widths=font_width_functions();mapping=read(ROOT/'translation/font_encoding.hex.json')
        catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')}
        self.assertEqual(len(rows),146)
        for r in rows:
            self.assertEqual(r['before'].replace('\n',''),r['after'].replace('\n',''))
            self.assertEqual(TOKEN.findall(r['before']),TOKEN.findall(r['after']))
            self.assertEqual(catalog[r['key']]['translation'],r['after'])
            self.assertLessEqual(len(TOKEN.sub('',r['after']).splitlines()),len(TOKEN.sub('',r['original']).splitlines()))
            pre=LEADING.match(r['before']).group();suf=TRAILING.search(r['before']).group()
            self.assertFalse(TOKEN.search(r['before'][len(pre):len(r['before'])-len(suf)]))
            for old_width,new_width in widths.values():
                old=measure(r['original'],old_width);new=measure(r['after'],new_width)
                self.assertFalse(old['missing']);self.assertFalse(new['missing'])
                self.assertLessEqual(new['max_width'],old['max_width'])
            encode_message(r['after'],mapping)

    def test_break_boundaries(self):
        self.assertFalse(valid_break('人格面具',3))
        self.assertFalse(valid_break('Thank you',2))
        self.assertFalse(valid_break('好了，……',3))
        self.assertTrue(valid_break('好了，出发吧',3))


if __name__=='__main__':unittest.main()
