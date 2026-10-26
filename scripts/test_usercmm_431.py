import unittest
import test_facility_423 as common
from compile_translation import ROOT,read,TOKEN

class UserCommunicationTests(common.FacilityTutorialTests):
    batch_name='431_usercmm_tutorial.generated.json'
    page_count=28
    def test_complete_scope_and_free_request(self):
        s='export_base/facility/msg_usercmm.bmd.json'
        rows=[r for r in read(ROOT/'translation/catalog.working.json') if r['source']==s]
        self.assertEqual(len(rows),28);self.assertTrue(all(r.get('translation') for r in rows))
        doc=read(ROOT/'translation/compiled'/s)
        for i,j,phrase in [(3,5,'不用花钱'),(6,4,'无需付费'),(9,5,'不用花钱')]:
            self.assertIn(phrase,TOKEN.sub('',doc['texts'][i]['lines'][j]))

if __name__=='__main__':unittest.main()
