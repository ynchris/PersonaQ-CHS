import unittest
import test_marie_statuses_a as common
from compile_translation import ROOT,read

class NanakoStatusesTests(common.MarieStatusesTests):
    batch_name='403_nanako_statuses_a.generated.json'
    group_count=4
    def test_addresses(self):
        batch=read(ROOT/'translation/batches'/self.batch_name)
        for source,rows in batch['sources'].items():
            by_id={r[0]:r[3] for r in rows}
            self.assertIn('哥哥',by_id[0]);self.assertIn('副队长',by_id[1])
            self.assertIn('哥哥',by_id[20]);self.assertIn('队长',by_id[21])
            self.assertIn('小虎',by_id[16])

if __name__=='__main__':unittest.main()
