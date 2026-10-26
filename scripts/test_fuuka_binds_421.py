import unittest
import test_marie_statuses_a as common
from compile_translation import ROOT,read,TOKEN

class FuukaBindsTests(common.MarieStatusesTests):
    batch_name='421_fuuka_binds_debuffs.generated.json'
    group_count=8
    def test_mechanics_and_addresses(self):
        batch=read(ROOT/'translation/batches'/self.batch_name)
        for s,rows in batch['sources'].items():
            for i,j,mid,body in rows:
                original=TOKEN.sub('',read(ROOT/s)['texts'][i]['lines'][j])
                if '(063)' in s:
                    self.assertIn('物理攻击',body);self.assertTrue('封住' in body or '无法使用' in body)
                if '(064)' in s:self.assertIn('只能使用物理',body)
                if '(065)' in s:
                    self.assertIn('无法闪避',body);self.assertTrue('逃跑' in body or '撤退' in body)
                for group,term in ((66,'攻击力'),(67,'防御力'),(68,'速度')):
                    if f'({group:03})' in s:
                        self.assertIn(term,body);self.assertTrue('降低' in body or '下降' in body)
                if '(068)' in s and i in (20,21):self.assertIn('命中率和闪避率均下降',body)
                if '玲ちゃん' in original:self.assertIn('玲',body)
                elif i==18:self.assertNotIn('玲',body)
                if i==11:self.assertIn('真田前辈',body)
                if i==12:self.assertIn('桐条前辈',body)
                if i==15:self.assertIn('天田',body)

if __name__=='__main__':unittest.main()
