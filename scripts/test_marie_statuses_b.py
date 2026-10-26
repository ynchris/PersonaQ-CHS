import unittest
import test_marie_statuses_a as common
from compile_translation import ROOT,read

class MarieRemainingStatusesTests(common.MarieStatusesTests):
    batch_name='398_marie_statuses_b.generated.json'
    group_count=3

    def test_distinct_character_content(self):
        batch=read(ROOT/'translation/batches'/self.batch_name)
        for source,rows in batch['sources'].items():
            for i,j,mid,body in rows:
                if '_(059)' in source:
                    self.assertIn('麻痹',body)
                    self.assertIn('动',body)
                if '_(060)' in source:
                    self.assertIn('诅咒',body)
                    self.assertNotIn('反噬',body)
        sleep=batch['sources']['export_dlc/0008/battle/support/bsv124.bvp_(058).BMD.json']
        self.assertIn('冬眠',next(r[3] for r in sleep if r[0]==8))

if __name__=='__main__':unittest.main()
