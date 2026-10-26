import hashlib
import unittest
from compile_translation import ROOT,read,TOKEN,LEADING,TRAILING
from raw_text_codec import encode_display,decode_display

class ElizabethBindsTests(unittest.TestCase):
    def test_all_six_groups(self):
        batch=read(ROOT/'translation/batches/388_elizabeth_binds.generated.json')
        self.assertEqual(sum(map(len,batch['sources'].values())),104)
        mapping=read(ROOT/'translation/font_encoding.hex.json')
        for source,rows in batch['sources'].items():
            old=read(ROOT/source);new=read(ROOT/'translation/compiled'/source)
            self.assertEqual(hashlib.sha256((ROOT/source).read_bytes()).hexdigest(),batch['source_hashes'][source])
            expected=set(range(4)) if '_(062)' in source else set(range(22))-{5,13}
            self.assertEqual({i for i,j,mid,body in rows},expected)
            for i,msg in enumerate(old['texts']):
                if i not in expected:self.assertEqual(msg,new['texts'][i])
            for i,j,mid,body in rows:
                original=old['texts'][i]['lines'][j]
                full=LEADING.match(original).group()+body+TRAILING.search(original).group()
                self.assertEqual(mid,old['texts'][i]['id'])
                self.assertEqual(full,new['texts'][i]['lines'][j])
                self.assertEqual(TOKEN.findall(original),TOKEN.findall(full))
                self.assertEqual(decode_display(encode_display(body,mapping),mapping),body)
                self.assertLessEqual(max(map(len,body.splitlines())),max(map(len,TOKEN.sub('',original).splitlines())))
                if '_(063)' in source:self.assertRegex(body,'封住|不能|无法');self.assertIn('物理',body)
                if '_(064)' in source:self.assertIn('只能使用物理攻击',body)
                if '_(065)' in source:self.assertIn('无法闪避或逃跑',body)
                if '_(066)' in source:self.assertIn('攻击力',body);self.assertRegex(body,'下|低|降')

if __name__=='__main__':unittest.main()
