import unittest
import test_facility_423 as common
from compile_translation import ROOT,read

class CombineTests(common.FacilityTutorialTests):
    batch_name='430_combine_strengthening.generated.json'
    page_count=12
    def test_scope_and_semantics(self):
        s='export_base/facility/msg_combine.bmd.json'
        rows=[r for r in read(ROOT/'translation/catalog.working.json') if r['source']==s and 51<=r['message_index']<=61]
        self.assertEqual(len(rows),12);self.assertTrue(all(r.get('translation') for r in rows))
        doc=read(ROOT/'translation/compiled'/s)
        for i,phrase in [(52,'无法代为保管'),(53,'强化素材'),(54,'中止强化'),(59,'腾出空位')]:self.assertIn(phrase,doc['texts'][i]['lines'][0])

if __name__=='__main__':unittest.main()
