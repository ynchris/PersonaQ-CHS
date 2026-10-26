import unittest
import test_facility_423 as common
from compile_translation import ROOT,read,TOKEN

class SkillCardTests(common.FacilityTutorialTests):
    batch_name='428_skillcard_copy_dialogue.generated.json'
    page_count=32
    def test_complete_scope_and_dynamic_names(self):
        s='export_base/facility/msg_sklcard.bmd.json'
        rows=[r for r in read(ROOT/'translation/catalog.working.json') if r['source']==s]
        self.assertEqual(len(rows),32);self.assertTrue(all(r.get('translation') for r in rows))
        doc=read(ROOT/'translation/compiled'/s)
        # Remove only the interleaved glyph control; dynamic name must stay in place.
        for i,prefix in [(1,''),(2,''),(6,''),(7,''),(11,'啊…'),(12,'…')]:
            line=doc['texts'][i]['lines'][0].replace('{F2 03 01 FF}','')
            self.assertIn(prefix+'{F4 45 04 01 00 00 01 01}，',line)
        self.assertIn('无法归还',TOKEN.sub('',doc['texts'][10]['lines'][2]))

if __name__=='__main__':unittest.main()
