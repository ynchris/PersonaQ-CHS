import unittest
import test_facility_423 as common
from compile_translation import ROOT,read
class ExactReuseTests(common.FacilityTutorialTests):
    batch_name='441_exact_reuse.generated.json'
    page_count=37
    def test_references(self):
        cat={r['key']:r for r in read(ROOT/'translation/catalog.working.json')}
        b=read(ROOT/'translation/batches'/self.batch_name)
        self.assertEqual(len(b['reuse_audit']),37)
        for a in b['reuse_audit']:
            target=cat[a['target_key']];ref=cat[a['reference_key']]
            self.assertEqual(target['original'],ref['original'])
            self.assertEqual(target['translation'],ref['translation'])
if __name__=='__main__':unittest.main()
