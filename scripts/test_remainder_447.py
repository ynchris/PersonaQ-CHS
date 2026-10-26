import unittest
import test_facility_423 as common
from compile_translation import ROOT,read
class RemainingMessagesTests(common.FacilityTutorialTests):
    batch_name='447_remaining_messages.generated.json'
    page_count=147
    def test_no_unreviewed_catalog_rows(self):
        audit=read(ROOT/'translation/remaining_audit.generated.json')
        self.assertEqual(audit['categories'].get('needs_review',0),0)
        self.assertEqual(audit['categories'].get('none_label_review',0),0)
        self.assertEqual(audit['total_catalog'],52253)
if __name__=='__main__':unittest.main()
