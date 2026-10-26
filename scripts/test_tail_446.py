import unittest
import test_facility_423 as common
from compile_translation import ROOT,read
class TailTests(common.FacilityTutorialTests):
    batch_name='446_battle_facility_skill_tail.generated.json'
    page_count=78
    def test_market_variable_positions(self):
        d=read(ROOT/'translation/compiled/export_base/facility/msg_market.bmd.json')
        t=d['texts'][1]['lines'][0].replace('{F2 03 01 FF}','')
        self.assertIn('＞{F2 44 02 01}个共{F2 44 03 01}日元。',t)
if __name__=='__main__':unittest.main()
