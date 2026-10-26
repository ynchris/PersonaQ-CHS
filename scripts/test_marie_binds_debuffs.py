import unittest
import test_marie_statuses_a as common
from compile_translation import ROOT,read

class MarieBindsTests(common.MarieStatusesTests):
    batch_name='399_marie_binds_debuffs.generated.json'
    group_count=6
    def test_mechanics_and_character(self):
        batch=read(ROOT/'translation/batches'/self.batch_name)
        for source,rows in batch['sources'].items():
            for i,j,mid,body in rows:
                if '_(064)' in source:self.assertIn('只能用物理攻击',body)
                if '_(065)' in source:
                    self.assertRegex(body,'没法回避或逃跑|躲不了，也逃不掉')
                if any(f'_({m:03})' in source for m in (66,67,68)):self.assertIn('下降',body)
                if i==18 and any(f'_({m:03})' in source for m in (64,66)):self.assertNotIn('玲',body)
        speed=batch['sources']['export_dlc/0008/battle/support/bsv124.bvp_(068).BMD.json']
        self.assertIn('太极拳',next(r[3] for r in speed if r[0]==3))

if __name__=='__main__':unittest.main()
