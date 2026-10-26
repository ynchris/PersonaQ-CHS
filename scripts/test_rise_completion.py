import hashlib,re,unittest,unicodedata
from collections import Counter
import test_marie_statuses_a as common
from compile_translation import ROOT,read,TOKEN,LEADING,TRAILING
from raw_text_codec import encode_display,decode_display

class RiseBindsTests(common.MarieStatusesTests):
    batch_name='416_rise_binds_debuffs.generated.json'
    group_count=7
    def test_effect_directions(self):
        batch=read(ROOT/'translation/batches'/self.batch_name)
        for s,rows in batch['sources'].items():
            for i,j,mid,body in rows:
                if '(064)' in s:
                    self.assertIn('只能',body);self.assertIn('物理',body)
                if '(065)' in s:
                    self.assertIn('无法闪避',body);self.assertIn('逃跑',body)
                for g,term in ((66,'攻击力'),(67,'防御力'),(68,'速度')):
                    if f'({g:03})' in s:
                        self.assertIn(term,body);self.assertTrue('降低' in body or '下降' in body)

class RiseCompletionTests(unittest.TestCase):
    def test_named_speaker_scope(self):
        rows=[r for r in read(ROOT/'translation/catalog.working.json') if any(t in str(r.get('speaker')) for t in ('りせ','理世'))]
        self.assertEqual(len(rows),1090)
        remaining=[r for r in rows if not r.get('translation')]
        self.assertEqual(len(remaining),12)
        for r in remaining:self.assertEqual(TOKEN.sub('',r['original']).strip(),'リザーブ')
        batch=read(ROOT/'translation/batches/418_rise_speaker_completion.generated.json');mapping=read(ROOT/'translation/font_encoding.hex.json')
        self.assertEqual(sum(map(len,batch['sources'].values())),3)
        for s,entries in batch['sources'].items():
            old=read(ROOT/s);new=read(ROOT/'translation/compiled'/s)
            self.assertEqual(hashlib.sha256((ROOT/s).read_bytes()).hexdigest(),batch['source_hashes'][s])
            for i,j,mid,body in entries:
                original=old['texts'][i]['lines'][j];full=LEADING.match(original).group()+body+TRAILING.search(original).group()
                self.assertEqual(mid,old['texts'][i]['id']);self.assertEqual(new['texts'][i]['lines'][j],full)
                self.assertEqual(TOKEN.findall(original),TOKEN.findall(full))
                self.assertLessEqual(len(body.splitlines()),len(TOKEN.sub('',original).splitlines()))
                self.assertLessEqual(max(map(len,body.splitlines())),max(map(len,TOKEN.sub('',original).splitlines())))
                self.assertEqual(decode_display(encode_display(body,mapping),mapping),body)

    def test_new_batch(self):
        batch=read(ROOT/'translation/batches/417_rise_completion.generated.json');mapping=read(ROOT/'translation/font_encoding.hex.json')
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
                if 'クロノス' in original:self.assertIn('克洛诺斯',body)

    def test_battle_and_dungeon_complete(self):
        catalog=read(ROOT/'translation/catalog.working.json')
        battle=[r for r in catalog if r['source'].startswith('export_base/battle/support/bsv105.')]
        self.assertEqual(len(battle),600)
        self.assertEqual(sum(bool(r.get('translation')) for r in battle),558)
        for r in battle:
            if not r.get('translation'):
                self.assertEqual(TOKEN.sub('',r['original']).strip(),'ダミーだよ')
                path=ROOT/'translation/compiled'/r['source']
                if path.exists():self.assertEqual(read(path)['texts'][r['message_index']]['lines'][r['line_index']],r['original'])
        scopes=['export_base/dungeon/script/rise_support.bf.json','export_base/dungeon/pack/pc006.arc_rise_support.bf.json']
        for source in scopes:
            rows=[r for r in catalog if r['source']==source]
            self.assertEqual(len(rows),115)
            self.assertTrue(all(r.get('translation') for r in rows))
        a=read(ROOT/'translation/compiled'/scopes[0]);b=read(ROOT/'translation/compiled'/scopes[1])
        self.assertEqual(a['texts'],b['texts'])

if __name__=='__main__':unittest.main()
