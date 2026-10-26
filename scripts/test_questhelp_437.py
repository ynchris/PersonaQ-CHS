import unittest
import test_facility_423 as common
from compile_translation import ROOT,read
class QuestHelpTests(common.FacilityTutorialTests):
    batch_name='437_legacy_quest_help.generated.json'
    page_count=70
    def test_placeholders_preserved(self):
        s='export_base/init/datquesthelp.bmd.json';a=read(ROOT/s);b=read(ROOT/'translation/compiled'/s)
        self.assertEqual(a['texts'][70:],b['texts'][70:])
if __name__=='__main__':unittest.main()
