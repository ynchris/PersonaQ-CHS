import unittest
import test_facility_423 as common
from compile_translation import ROOT,read

class VelvetEntryTests(common.FacilityTutorialTests):
    batch_name='425_velvet_entry_challenge.generated.json'
    page_count=11
    def test_choices_and_preserved_development_text(self):
        s='export_base/facility/cmbtalk.bf.json'
        old=read(ROOT/s);new=read(ROOT/'translation/compiled'/s)
        for i in (0,6,7,12):self.assertEqual(old['texts'][i],new['texts'][i])
        self.assertIn('准备好了',new['texts'][9]['lines'][0])
        self.assertIn('稍等一下',new['texts'][9]['lines'][1])

if __name__=='__main__':unittest.main()
