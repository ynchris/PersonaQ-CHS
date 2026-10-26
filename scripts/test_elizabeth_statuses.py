import hashlib
import re
import unicodedata
import unittest
from collections import Counter
from compile_translation import ROOT,read,TOKEN,LEADING,TRAILING
from raw_text_codec import encode_display,decode_display

class ElizabethStatusesTests(unittest.TestCase):
    def test_complete_seven_status_groups(self):
        batch=read(ROOT/'translation/batches/387_elizabeth_statuses.generated.json')
        self.assertEqual(len(batch['sources']),7)
        mapping=read(ROOT/'translation/font_encoding.hex.json')
        for source,rows in batch['sources'].items():
            old=read(ROOT/source);new=read(ROOT/'translation/compiled'/source)
            self.assertEqual(hashlib.sha256((ROOT/source).read_bytes()).hexdigest(),batch['source_hashes'][source])
            self.assertEqual({i for i,j,mid,b in rows},set(range(22))-{5,13})
            for i in [5,13]:self.assertEqual(old['texts'][i],new['texts'][i])
            for i,j,mid,body in rows:
                original=old['texts'][i]['lines'][j]
                full=LEADING.match(original).group()+body+TRAILING.search(original).group()
                self.assertEqual(new['texts'][i]['lines'][j],full)
                self.assertEqual(TOKEN.findall(original),TOKEN.findall(full))
                nums=lambda t:Counter(re.findall(r'\d+',unicodedata.normalize('NFKC',TOKEN.sub('',t))))
                self.assertEqual(nums(original),nums(full))
                self.assertLessEqual(max(map(len,body.splitlines())),max(map(len,TOKEN.sub('',original).splitlines())))
                self.assertEqual(decode_display(encode_display(body,mapping),mapping),body)
                if '_(060)' in source:
                    self.assertRegex(body,'攻击|对敌人出手')
                    self.assertNotIn('受到攻击',body)

if __name__=='__main__':unittest.main()
