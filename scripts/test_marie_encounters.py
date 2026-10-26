import hashlib,re,unicodedata,unittest
from collections import Counter
from compile_translation import ROOT,read,TOKEN,LEADING,TRAILING
from raw_text_codec import encode_display,decode_display

class MarieEncountersTests(unittest.TestCase):
    batch_name='396_marie_encounters.generated.json'
    scope='0008'
    def test_block(self):
        batch=read(ROOT/'translation/batches'/self.batch_name);mapping=read(ROOT/'translation/font_encoding.hex.json')
        self.assertEqual(sum(map(len,batch['sources'].values())),91)
        for source,rows in batch['sources'].items():
            old=read(ROOT/source);new=read(ROOT/'translation/compiled'/source)
            self.assertEqual(hashlib.sha256((ROOT/source).read_bytes()).hexdigest(),batch['source_hashes'][source])
            for i,j,mid,body in rows:
                original=old['texts'][i]['lines'][j];full=LEADING.match(original).group()+body+TRAILING.search(original).group()
                self.assertEqual(mid,old['texts'][i]['id']);self.assertEqual(new['texts'][i]['lines'][j],full)
                self.assertEqual(TOKEN.findall(original),TOKEN.findall(full))
                nums=lambda t:Counter(re.findall(r'\d+',unicodedata.normalize('NFKC',TOKEN.sub('',t))))
                self.assertEqual(nums(original),nums(body))
                self.assertLessEqual(len(body.splitlines()),len(TOKEN.sub('',original).splitlines()))
                self.assertLessEqual(max(map(len,body.splitlines())),max(map(len,TOKEN.sub('',original).splitlines())))
                self.assertEqual(decode_display(encode_display(body,mapping),mapping),body)
        for row in read(ROOT/'translation/catalog.working.json'):
            if row['source'].startswith(f'export_dlc/{self.scope}/battle/support/') and int(re.search(r'_\((\d+)\)',row['source'])[1])<=53:
                self.assertTrue(row.get('translation'),row['key'])

if __name__=='__main__':unittest.main()
