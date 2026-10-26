import unittest
import test_facility_423 as common
from compile_translation import ROOT,read,TOKEN

class CostumeTests(common.FacilityTutorialTests):
    batch_name='429_costume_confirmations.generated.json'
    page_count=7
    def test_variables_and_preserved_rows(self):
        s='export_base/facility/msg_costume.bmd.json';old=read(ROOT/s);new=read(ROOT/'translation/compiled'/s)
        for i in range(len(old['texts'])):
            if i not in (0,1,2,4,5,11):self.assertEqual(old['texts'][i],new['texts'][i])
        line=new['texts'][2]['lines'][0].replace('{F2 03 01 FF}','')
        self.assertIn('＞{F4 45 04 01 00 00 01 01}×{F2 44 02 01}件，卖出吗？',line)
        self.assertIn('所有人',TOKEN.sub('',new['texts'][11]['lines'][0]))

if __name__=='__main__':unittest.main()
