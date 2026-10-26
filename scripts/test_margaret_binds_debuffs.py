import hashlib
import re
import unittest
from compile_translation import ROOT,read,TOKEN,LEADING,TRAILING
from raw_text_codec import encode_display,decode_display

class MargaretBindsDebuffsTests(unittest.TestCase):
    def test_six_groups(self):
        batch=read(ROOT/'translation/batches/394_margaret_binds_debuffs.generated.json')
        mapping=read(ROOT/'translation/font_encoding.hex.json')
        self.assertEqual(len(batch['sources']),6)
        for source,rows in batch['sources'].items():
            m=int(re.search(r'_\((\d+)\)',source)[1])
            old=read(ROOT/source);new=read(ROOT/'translation/compiled'/source)
            self.assertEqual(hashlib.sha256((ROOT/source).read_bytes()).hexdigest(),batch['source_hashes'][source])
            self.assertEqual({r[0] for r in rows},set(range(22))-{5,13})
            for i in [5,13]:self.assertEqual(old['texts'][i],new['texts'][i])
            for i,j,mid,body in rows:
                original=old['texts'][i]['lines'][j]
                full=LEADING.match(original).group()+body+TRAILING.search(original).group()
                self.assertEqual(mid,old['texts'][i]['id'])
                self.assertEqual(new['texts'][i]['lines'][j],full)
                self.assertEqual(TOKEN.findall(original),TOKEN.findall(full))
                self.assertEqual(re.findall(r'\d+',TOKEN.sub('',original)),re.findall(r'\d+',body))
                self.assertLessEqual(len(body.splitlines()),len(TOKEN.sub('',original).splitlines()))
                self.assertLessEqual(max(map(len,body.splitlines())),max(map(len,TOKEN.sub('',original).splitlines())))
                self.assertEqual(decode_display(encode_display(body,mapping),mapping),body)
                if m==64:self.assertIn('只能使用物理攻击',body)
                if m==65:self.assertRegex(body,'无法.*回避|无法\n回避');self.assertIn('逃跑',body)
                if m in (66,67,68):self.assertRegex(body,'下降|低了');self.assertNotIn('上升',body)
                if m in (64,66) and i==18:self.assertNotIn('玲',body)
        for row in read(ROOT/'translation/catalog.working.json'):
            if row['source'].startswith('export_dlc/0007/battle/support/') and 61<=int(re.search(r'_\((\d+)\)',row['source'])[1])<=68:
                if row['message_index'] in (5,13):
                    self.assertIn(TOKEN.sub('',row['original']).strip(),('ダミーだよ','ダミー・りせ用入れ込む','ダミー・風花用入れ込む','ダミーのまま入れ込む'))
                    self.assertFalse(row.get('translation'))
                else:self.assertTrue(row.get('translation'),row['key'])

if __name__=='__main__':unittest.main()
