import unittest
from collections import Counter
from compile_translation import ROOT,read,TOKEN
from raw_text_codec import encode_display
from terminology_459 import apply

class Terminology459Tests(unittest.TestCase):
    def test_scoped_changes_and_controls(self):
        rows=read(ROOT/'translation/terminology_459.review.json')['rows']
        self.assertEqual(Counter(r['scope'] for r in rows),{'messages':181,'tables':2,'schoolwalk':4})
        for r in rows:
            self.assertEqual(r['after'],r['before'].replace('钟楼','时钟塔'))
            self.assertEqual(TOKEN.findall(r['before']),TOKEN.findall(r['after']))
            self.assertEqual(apply(r['scope'],r['key'],r['before']),r['after'])
        with self.assertRaises(AssertionError):apply(rows[0]['scope'],rows[0]['key'],'stale')

    def test_compiled_messages_tables_and_schoolwalk(self):
        from schoolwalk_names import load
        messages=read(ROOT/'translation/catalog.working.json')
        tables=read(ROOT/'translation/tables.catalog.working.json')
        school=load()['rows']
        self.assertFalse(any('钟楼' in (r.get('translation') or '') for r in messages+tables+school))
        mapping=read(ROOT/'translation/font_encoding.hex.json')
        encode_display('时钟塔',mapping)

    def test_executable_floors(self):
        d=read(ROOT/'translation/code_extra_458.review.json')
        for f in d['files']:
            revised=[r for r in f['rows'] if 'supersedes_translation' in r]
            self.assertEqual(len(revised),11)
            self.assertTrue(all('时钟塔' in r['translation'] for r in revised))

if __name__=='__main__':unittest.main()
