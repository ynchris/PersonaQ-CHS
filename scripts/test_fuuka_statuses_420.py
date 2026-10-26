import unittest
import test_marie_statuses_a as common
from compile_translation import ROOT,read

class FuukaStatusTests(common.MarieStatusesTests):
    batch_name='420_fuuka_statuses.generated.json'
    group_count=7
    def test_addresses_and_effects(self):
        batch=read(ROOT/'translation/batches'/self.batch_name)
        for source,rows in batch['sources'].items():
            texts={i:body for i,j,mid,body in rows}
            for i,term in ((0,'副队长'),(1,'副队长'),(2,'花村'),(6,'巽'),(11,'真田前辈'),(12,'桐条前辈'),(15,'天田'),(16,'小虎'),(17,'荒垣前辈'),(20,'队长'),(21,'队长')):
                self.assertIn(term,texts[i])
            if '(059)' in source:
                for body in texts.values():self.assertTrue(any(t in body for t in ('可能','能否','能行动吗')))
            if '(060)' in source:
                for body in texts.values():
                    self.assertIn('攻击',body);self.assertNotIn('受到攻击',body)
                for i in (0,4,10,14,15,21):self.assertIn('自己',texts[i])

if __name__=='__main__':unittest.main()
