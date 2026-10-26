import hashlib,unittest,re,unicodedata
from collections import Counter
from compile_translation import ROOT,read,TOKEN,LEADING,TRAILING
from raw_text_codec import encode_display,decode_display

class FacilityTutorialTests(unittest.TestCase):
    batch_name='423_navigation_party_tutorials.generated.json'
    page_count=8
    def test_batch(self):
        batch=read(ROOT/'translation/batches'/self.batch_name);mapping=read(ROOT/'translation/font_encoding.hex.json')
        self.assertEqual(sum(map(len,batch['sources'].values())),self.page_count)
        for s,rows in batch['sources'].items():
            old=read(ROOT/s);new=read(ROOT/'translation/compiled'/s)
            self.assertEqual(hashlib.sha256((ROOT/s).read_bytes()).hexdigest(),batch['source_hashes'][s])
            for i,j,mid,body in rows:
                original=old['texts'][i]['lines'][j];full=LEADING.match(original).group()+body+TRAILING.search(original).group()
                self.assertEqual(mid,old['texts'][i]['id']);self.assertEqual(full,new['texts'][i]['lines'][j])
                self.assertEqual(TOKEN.findall(original),TOKEN.findall(full))
                nums=lambda t:Counter(re.findall(r'\d+',unicodedata.normalize('NFKC',TOKEN.sub('',t))))
                self.assertEqual(nums(original),nums(full))
                a=TOKEN.sub('',original).splitlines();b=TOKEN.sub('',full).splitlines()
                self.assertLessEqual(len(b),len(a));self.assertLessEqual(max(map(len,b)),max(map(len,a)))
                plain=TOKEN.sub('',full);self.assertEqual(decode_display(encode_display(plain,mapping),mapping),plain)
                if s.endswith('scrpartyedit.bf.json') and i==2:
                    self.assertIn('只能使用',body);self.assertIn('各自负责',body)
                if s.endswith('scrgotodungeon.bf.json') and i==2:self.assertIn('２位不羁能力者一同前往',body)

if __name__=='__main__':unittest.main()
