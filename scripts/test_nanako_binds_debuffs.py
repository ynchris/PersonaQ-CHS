import unittest
import test_marie_statuses_a as common
from compile_translation import ROOT,read

class NanakoBindsTests(common.MarieStatusesTests):
    batch_name='405_nanako_binds_debuffs.generated.json'
    group_count=6
    def test_meanings(self):
        batch=read(ROOT/'translation/batches'/self.batch_name)
        for source,rows in batch['sources'].items():
            for i,j,mid,body in rows:
                if '_(064)' in source:self.assertIn('物理',body);self.assertIn('只能',body)
                if '_(065)' in source:
                    if i in (16,17):self.assertIn('全部打中',body)
                    else:self.assertIn('不能',body);self.assertIn('逃跑',body)
                if any(f'_({m:03})' in source for m in (66,67)):self.assertRegex(body,'弱|降低')
                if i==18 and any(f'_({m:03})' in source for m in (64,66)):self.assertNotIn('玲',body)

if __name__=='__main__':unittest.main()
