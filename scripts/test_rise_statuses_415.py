import unittest
import test_marie_statuses_a as common
from compile_translation import ROOT,read,TOKEN

class RiseStatusTests(common.MarieStatusesTests):
    batch_name='415_rise_statuses.generated.json'
    group_count=7

    def test_mechanics_and_addresses(self):
        batch=read(ROOT/'translation/batches'/self.batch_name)
        for s,rows in batch['sources'].items():
            by_id={r[0]:r[3] for r in rows}
            self.assertIn('前辈',by_id[0]);self.assertIn('副队长',by_id[1])
            self.assertIn('花村前辈',by_id[2]);self.assertIn('乾',by_id[15])
            self.assertIn('小虎',by_id[16]);self.assertIn('前辈',by_id[20]);self.assertIn('队长',by_id[21])
            if '(059)' in s:
                for text in by_id.values():self.assertTrue(any(t in text for t in ('可能','不知道','能动')))
            if '(060)' in s:
                for text in by_id.values():
                    self.assertIn('攻击',text)
                    self.assertNotIn('受到攻击',text)
                for i in (2,4,6,10,12,14,15,17,20,21):self.assertIn('自己',by_id[i])

if __name__=='__main__':unittest.main()
