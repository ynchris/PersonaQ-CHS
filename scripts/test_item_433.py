import unittest
import test_facility_423 as common
from compile_translation import ROOT,read,TOKEN
class ItemTests(common.FacilityTutorialTests):
    batch_name='433_item_shop_legacy.generated.json'
    page_count=108
    def test_discount(self):
        d=read(ROOT/'translation/compiled/export_base/facility/msg_item.bmd.json')
        self.assertIn('降价２成',TOKEN.sub('',d['texts'][10]['lines'][1]))
if __name__=='__main__':unittest.main()
