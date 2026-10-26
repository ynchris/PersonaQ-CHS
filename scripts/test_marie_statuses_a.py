import hashlib,re,unittest
from compile_translation import ROOT,read,TOKEN,LEADING,TRAILING
from raw_text_codec import encode_display,decode_display

class MarieStatusesTests(unittest.TestCase):
    batch_name='397_marie_statuses_a.generated.json'
    group_count=4
    def test_four_groups(self):
        batch=read(ROOT/'translation/batches'/self.batch_name);mapping=read(ROOT/'translation/font_encoding.hex.json')
        self.assertEqual(len(batch['sources']),self.group_count)
        for source,rows in batch['sources'].items():
            old=read(ROOT/source);new=read(ROOT/'translation/compiled'/source)
            self.assertEqual(hashlib.sha256((ROOT/source).read_bytes()).hexdigest(),batch['source_hashes'][source])
            self.assertEqual({r[0] for r in rows},set(range(22))-{5,13})
            for i in (5,13):self.assertEqual(old['texts'][i],new['texts'][i])
            for i,j,mid,body in rows:
                original=old['texts'][i]['lines'][j];full=LEADING.match(original).group()+body+TRAILING.search(original).group()
                self.assertEqual(mid,old['texts'][i]['id']);self.assertEqual(new['texts'][i]['lines'][j],full)
                self.assertEqual(TOKEN.findall(original),TOKEN.findall(full))
                self.assertEqual(re.findall(r'\d+',TOKEN.sub('',original)),re.findall(r'\d+',body))
                self.assertLessEqual(len(body.splitlines()),len(TOKEN.sub('',original).splitlines()))
                self.assertLessEqual(max(map(len,body.splitlines())),max(map(len,TOKEN.sub('',original).splitlines())))
                self.assertEqual(decode_display(encode_display(body,mapping),mapping),body)

if __name__=='__main__':unittest.main()
