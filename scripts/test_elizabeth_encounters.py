import hashlib
import re
import unicodedata
import unittest
from collections import Counter
from compile_translation import ROOT,read,TOKEN,LEADING,TRAILING
from raw_text_codec import encode_display,decode_display

class ElizabethEncountersTests(unittest.TestCase):
    def test_encounter_block(self):
        batch=read(ROOT/'translation/batches/386_elizabeth_encounters.generated.json')
        mapping=read(ROOT/'translation/font_encoding.hex.json')
        total=0
        for source,rows in batch['sources'].items():
            old=read(ROOT/source);new=read(ROOT/'translation/compiled'/source)
            self.assertEqual(hashlib.sha256((ROOT/source).read_bytes()).hexdigest(),batch['source_hashes'][source])
            for i,j,mid,body in rows:
                total+=1;original=old['texts'][i]['lines'][j]
                value=LEADING.match(original).group()+body+TRAILING.search(original).group()
                self.assertEqual(old['texts'][i]['id'],mid)
                self.assertEqual(value,new['texts'][i]['lines'][j])
                self.assertEqual(TOKEN.findall(value),TOKEN.findall(original))
                nums=lambda t:Counter(re.findall(r'\d+',unicodedata.normalize('NFKC',TOKEN.sub('',t))))
                self.assertEqual(nums(value),nums(original))
                self.assertLessEqual(max(map(len,body.splitlines())),max(map(len,TOKEN.sub('',original).splitlines())))
                self.assertEqual(decode_display(encode_display(body,mapping),mapping),body)
        self.assertGreater(total,80)
        for row in read(ROOT/'translation/catalog.working.json'):
            if row['source'].startswith('export_dlc/0006/battle/support/') and int(re.search(r'_\((\d+)\)',row['source'])[1])<=53:
                self.assertTrue(row.get('translation'),row['key'])

if __name__=='__main__':unittest.main()
