import hashlib
import re
import unittest
import unicodedata
from collections import Counter
from compile_translation import ROOT,read,TOKEN,LEADING,TRAILING
from raw_text_codec import encode_display,decode_display

class ElizabethCompletionTests(unittest.TestCase):
    def test_entire_navigator(self):
        rows=[r for r in read(ROOT/'translation/catalog.working.json') if r['source'].startswith('export_dlc/0006/battle/support/bsv121.bvp_')]
        self.assertEqual(len(rows),582)
        translated=[r for r in rows if r.get('translation')]
        self.assertEqual(len(translated),542)
        remaining=[r for r in rows if not r.get('translation')]
        self.assertEqual(len(remaining),40)
        self.assertEqual(Counter(TOKEN.sub('',r['original']).strip() for r in remaining),{'ダミー':29,'ダミーだよ':11})
        for r in remaining:
            path=ROOT/'translation/compiled'/r['source']
            if path.exists():self.assertEqual(read(path)['texts'][r['message_index']]['lines'][r['line_index']],r['original'])

    def test_final_batch_and_mechanics(self):
        batch=read(ROOT/'translation/batches/390_elizabeth_completion.generated.json')
        mapping=read(ROOT/'translation/font_encoding.hex.json')
        self.assertEqual(sum(map(len,batch['sources'].values())),91)
        for source,rows in batch['sources'].items():
            old=read(ROOT/source);new=read(ROOT/'translation/compiled'/source)
            self.assertEqual(hashlib.sha256((ROOT/source).read_bytes()).hexdigest(),batch['source_hashes'][source])
            for i,j,mid,body in rows:
                original=old['texts'][i]['lines'][j]
                full=LEADING.match(original).group()+body+TRAILING.search(original).group()
                self.assertEqual(mid,old['texts'][i]['id'])
                self.assertEqual(full,new['texts'][i]['lines'][j])
                self.assertEqual(TOKEN.findall(original),TOKEN.findall(full))
                nums=lambda t:Counter(re.findall(r'\d+',unicodedata.normalize('NFKC',TOKEN.sub('',t))))
                self.assertEqual(nums(full),nums(original))
                self.assertLessEqual(max(map(len,body.splitlines())),max(map(len,TOKEN.sub('',original).splitlines())))
                self.assertEqual(decode_display(encode_display(body,mapping),mapping),body)
                if '_(181)' in source:self.assertIn('倒计时',body);self.assertIn('１',body)
                if 'クロノス' in original:self.assertIn('克洛诺斯',body)
                if '誓' in original:self.assertRegex(body,'誓|发誓')

if __name__=='__main__':unittest.main()
