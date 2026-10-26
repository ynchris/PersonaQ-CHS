import unittest
import test_facility_423 as common
from compile_translation import ROOT,read

class NofficeTests(common.FacilityTutorialTests):
    batch_name='426_noffice_deadlines.generated.json'
    page_count=12
    def test_coverage_and_preserved_development_text(self):
        s='export_base/facility/noffice.bf.json'
        old=read(ROOT/s);new=read(ROOT/'translation/compiled'/s)
        for i in (8,9,13,14):self.assertEqual(old['texts'][i],new['texts'][i])
        rows=[r for r in read(ROOT/'translation/catalog.working.json') if r['source']==s]
        self.assertEqual({r['message_index'] for r in rows if not r.get('translation')},{8,9,13,14})
        self.assertIn('过期',new['texts'][5]['lines'][0])
        self.assertIn('也别忘了我',new['texts'][5]['lines'][1])

if __name__=='__main__':unittest.main()
