import unittest
import test_marie_statuses_a as common
from compile_translation import ROOT,read

class TheodoreRemainingStatusesTests(common.MarieStatusesTests):
    batch_name='409_theodore_statuses_b.generated.json'
    group_count=3
    def test_curse_direction(self):
        batch=read(ROOT/'translation/batches'/self.batch_name)
        rows=batch['sources']['export_dlc/0005/battle/support/bsv123.bvp_(060).BMD.json']
        for i,j,mid,body in rows:
            self.assertIn('诅咒',body)
            if i in (1,7,12,20,21):
                self.assertIn('攻击',body);self.assertIn('自身',body);self.assertNotIn('受到攻击',body)

if __name__=='__main__':unittest.main()
