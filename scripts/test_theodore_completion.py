import hashlib,re,unicodedata,unittest
from collections import Counter
from compile_translation import ROOT,read,TOKEN,LEADING,TRAILING
from raw_text_codec import encode_display,decode_display

class TheodoreCompletionTests(unittest.TestCase):
    def test_new_batch(self):
        batch=read(ROOT/'translation/batches/410_theodore_completion.generated.json');mapping=read(ROOT/'translation/font_encoding.hex.json')
        self.assertEqual(sum(map(len,batch['sources'].values())),258)
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
                if '_(064)' in source:self.assertIn('只能使用物理攻击',body)
                if '_(065)' in source:self.assertIn('无法回避或逃跑',body)
    def test_entire_scope(self):
        rows=[r for r in read(ROOT/'translation/catalog.working.json') if r['source'].startswith('export_dlc/0005/')]
        battle=[r for r in rows if '/battle/' in r['source']];dungeon=[r for r in rows if '/dungeon/' in r['source']]
        self.assertEqual(len(battle),582);self.assertEqual(sum(bool(r.get('translation')) for r in battle),542)
        self.assertEqual(sum(bool(r.get('translation')) for r in dungeon),106)
        unused=Counter(TOKEN.sub('',r['original']).strip() for r in dungeon if not r.get('translation'))
        self.assertEqual(unused,{'欠番':3,'カットセリフ（もうすぐレベルアップ）':6})
        for r in battle:
            if not r.get('translation'):self.assertIn(TOKEN.sub('',r['original']).strip(),{'ダミー','ダミーだよ','ダミーのまま入れ込む','ダミー・りせ用入れ込む','ダミー・風花用入れ込む'})
        for r in rows:
            if not r.get('translation'):
                p=ROOT/'translation/compiled'/r['source']
                if p.exists():self.assertEqual(read(ROOT/r['source'])['texts'][r['message_index']],read(p)['texts'][r['message_index']])
        cerberus=[r for r in rows if 'ケルベロス' in r['original']]
        self.assertEqual(len(cerberus),1);self.assertIn('克鲁贝洛斯',cerberus[0]['translation'])

if __name__=='__main__':unittest.main()
