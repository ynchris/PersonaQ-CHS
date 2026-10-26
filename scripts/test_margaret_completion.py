import hashlib,re,unicodedata,unittest
from collections import Counter
from compile_translation import ROOT,read,TOKEN,LEADING,TRAILING
from raw_text_codec import encode_display,decode_display

class MargaretCompletionTests(unittest.TestCase):
    def test_new_pages(self):
        batch=read(ROOT/'translation/batches/395_margaret_completion.generated.json');mapping=read(ROOT/'translation/font_encoding.hex.json')
        self.assertEqual(sum(map(len,batch['sources'].values())),138)
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
                if any(f'_({n:03})' in source for n in (183,184,185)):self.assertIn('克洛诺斯',body)
    def test_whole_bank(self):
        rows=[r for r in read(ROOT/'translation/catalog.working.json') if r['source'].startswith('export_dlc/0007/battle/support/')]
        self.assertEqual(len(rows),582)
        self.assertEqual(sum(bool(r.get('translation')) for r in rows),542)
        remaining=[r for r in rows if not r.get('translation')]
        self.assertEqual(len(remaining),40)
        allowed={'ダミーだよ','ダミーのまま入れ込む','ダミー・りせ用入れ込む','ダミー・風花用入れ込む'}
        for r in remaining:
            self.assertIn(TOKEN.sub('',r['original']).strip(),allowed)
            old=read(ROOT/r['source'])
            compiled=ROOT/'translation/compiled'/r['source']
            if compiled.exists():self.assertEqual(old['texts'][r['message_index']],read(compiled)['texts'][r['message_index']])

if __name__=='__main__':unittest.main()
