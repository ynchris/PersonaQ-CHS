import unittest
import test_facility_423 as common
from compile_translation import ROOT,read
class WeaponShopTests(common.FacilityTutorialTests):
    batch_name='435_weapon_shop_legacy.generated.json'
    page_count=125
    def test_scope(self):
        rows=[r for r in read(ROOT/'translation/catalog.working.json') if r['source']=='export_base/facility/msg_weapon.bmd.json' and 81<=r['message_index']<=114]
        self.assertEqual(len(rows),127)
        self.assertTrue(all(r.get('translation') for r in rows))
if __name__=='__main__':unittest.main()
