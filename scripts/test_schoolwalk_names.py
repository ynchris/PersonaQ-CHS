import unittest
import re
import unicodedata
from collections import Counter
from schoolwalk_names import ROOT,load,SOURCE
from q2_name_banks import parse,build_bank
from compile_translation import read

class SchoolwalkTests(unittest.TestCase):
    def test_complete_and_preserved(self):
        draft=load();self.assertEqual(len(draft['rows']),136)
        self.assertEqual(len(draft['retained']),81)
        self.assertTrue(all('バッファ' in r['original'] or 'ダミー' in r['original'] for r in draft['retained']))
        mapping=read(ROOT/'translation/font_encoding.hex.json')
        data=(ROOT/'data'/SOURCE).read_bytes()
        result=build_bank(data,217,draft['rows'],mapping)
        self.assertEqual(result,(ROOT/'full_work/schoolwalk_payload'/SOURCE).read_bytes())
        old=parse(data,217);new=parse(result,217)
        for r in draft['retained']:self.assertEqual(old[r['index']],new[r['index']])
        translations={}
        nums=lambda s:Counter(re.findall(r'\d+',unicodedata.normalize('NFKC',s)))
        for r in draft['rows']:
            self.assertEqual(nums(r['original']),nums(r['translation']))
            self.assertNotRegex(r['translation'],r'[\u3041-\u3096\u30a1-\u30fa]')
            if r['original'] in translations:self.assertEqual(translations[r['original']],r['translation'])
            translations[r['original']]=r['translation']

if __name__=='__main__':unittest.main()
