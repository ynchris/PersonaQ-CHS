import hashlib
import re
import unittest
import unicodedata
from collections import Counter
from compile_translation import ROOT,read,TOKEN,LEADING,TRAILING
from raw_text_codec import encode_display,decode_display

class ElizabethAnalysisTests(unittest.TestCase):
    def test_block_integrity(self):
        batch=read(ROOT/'translation/batches/389_elizabeth_analysis_defeat.generated.json')
        mapping=read(ROOT/'translation/font_encoding.hex.json');count=0
        for source,rows in batch['sources'].items():
            old=read(ROOT/source);new=read(ROOT/'translation/compiled'/source)
            self.assertEqual(hashlib.sha256((ROOT/source).read_bytes()).hexdigest(),batch['source_hashes'][source])
            member=int(re.search(r'_\((\d+)\)',source)[1])
            for i,j,mid,body in rows:
                count+=1;original=old['texts'][i]['lines'][j]
                full=LEADING.match(original).group()+body+TRAILING.search(original).group()
                self.assertEqual(old['texts'][i]['id'],mid)
                self.assertEqual(full,new['texts'][i]['lines'][j])
                self.assertEqual(TOKEN.findall(original),TOKEN.findall(full))
                nums=lambda t:Counter(re.findall(r'\d+',unicodedata.normalize('NFKC',TOKEN.sub('',t))))
                self.assertEqual(nums(full),nums(original))
                self.assertLessEqual(max(map(len,body.splitlines())),max(map(len,TOKEN.sub('',original).splitlines())))
                self.assertEqual(decode_display(encode_display(body,mapping),mapping),body)
                if member in {67,68}:self.assertIn('下降',body)
                if 69<=member<=78:
                    self.assertIn(['斩击','突击','坏击','火焰','冰冻','电击','疾风','光','暗','万能'][member-69]+'属性',body)
        self.assertGreater(count,100)
        for r in read(ROOT/'translation/catalog.working.json'):
            if r['source'].startswith('export_dlc/0006/battle/support/'):
                m=int(re.search(r'_\((\d+)\)',r['source'])[1])
                if 67<=m<=122 and not r.get('translation'):self.assertIn('ダミー',r['original'])

if __name__=='__main__':unittest.main()
