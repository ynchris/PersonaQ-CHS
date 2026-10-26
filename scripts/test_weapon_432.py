import unittest
import test_facility_423 as common
from compile_translation import ROOT,read

class WeaponTests(common.FacilityTutorialTests):
    batch_name='432_weapon_legacy_dialogue.generated.json'
    page_count=60
    def test_scope(self):
        s='export_base/facility/weapon.bf.json'
        rows=[r for r in read(ROOT/'translation/catalog.working.json') if r['source']==s and not r.get('translation')]
        self.assertEqual({r['message_index'] for r in rows},{4,5,21,31,40,41})
        from audit_remaining_text import classify
        self.assertTrue(all(r['message_index'] in (4,5) or classify(r['original'])[0]=='punctuation_only' for r in rows))

if __name__=='__main__':unittest.main()
