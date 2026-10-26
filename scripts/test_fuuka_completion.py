import hashlib,re,unittest,unicodedata
from collections import Counter
from compile_translation import ROOT,read,TOKEN,LEADING,TRAILING
from raw_text_codec import encode_display,decode_display

class FuukaCompletionTests(unittest.TestCase):
    def test_batch(self):
        batch=read(ROOT/'translation/batches/422_fuuka_completion.generated.json');mapping=read(ROOT/'translation/font_encoding.hex.json')
        self.assertEqual(sum(map(len,batch['sources'].values())),171)
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
                plain=TOKEN.sub('',full)
                self.assertEqual(decode_display(encode_display(plain,mapping),mapping),plain)
                if 'クロノス' in original:self.assertIn('克洛诺斯',body)
                if 'オラクル' in original:self.assertIn('神谕',body)

    def test_complete_scopes(self):
        rs=read(ROOT/'translation/catalog.working.json')
        battle=[r for r in rs if r['source'].startswith('export_base/battle/support/bsv108.')]
        self.assertEqual(len(battle),597);self.assertEqual(sum(bool(r.get('translation')) for r in battle),562)
        for r in battle:
            if not r.get('translation'):
                self.assertEqual(TOKEN.sub('',r['original']).strip(),'ダミーだよ')
                p=ROOT/'translation/compiled'/r['source']
                if p.exists():self.assertEqual(read(p)['texts'][r['message_index']]['lines'][r['line_index']],r['original'])
        scopes=['export_base/dungeon/script/fuka_support.bf.json','export_base/dungeon/pack/pc00e.arc_fuka_support.bf.json']
        for s in scopes:
            a=[r for r in rs if r['source']==s];self.assertEqual(len(a),96)
            self.assertTrue(all(r.get('translation') for r in a))
        self.assertEqual(read(ROOT/'translation/compiled'/scopes[0])['texts'],read(ROOT/'translation/compiled'/scopes[1])['texts'])
        named=[r for r in rs if any(t in str(r.get('speaker')) for t in ('風花','风花'))]
        self.assertEqual(len(named),1079)
        left=[r for r in named if not r.get('translation')];self.assertEqual(len(left),12)
        for r in left:self.assertEqual(TOKEN.sub('',r['original']).strip(),'リザーブ')

if __name__=='__main__':unittest.main()
