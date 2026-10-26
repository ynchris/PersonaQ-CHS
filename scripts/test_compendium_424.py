import unittest
import test_facility_423 as common
from compile_translation import ROOT,read,TOKEN

class CompendiumRewardsTests(common.FacilityTutorialTests):
    batch_name='424_compendium_rewards.generated.json'
    page_count=71
    def test_reuse_and_coverage(self):
        batch=read(ROOT/'translation/batches'/self.batch_name)
        catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')}
        self.assertEqual(len(batch['reuse_audit']),39)
        for a in batch['reuse_audit']:
            dst=catalog[a['target_key']];src=catalog[a['reference_key']]
            self.assertEqual(dst['original'],src['original']);self.assertEqual(dst['translation'],src['translation'])
            self.assertEqual(a['original'],src['original']);self.assertEqual(a['translation'],src['translation'])
        rows=[r for r in catalog.values() if r['source']=='export_base/facility/cmbtalk.bf.json' and 113<=r['message_index']<=136]
        self.assertEqual(len(rows),71);self.assertTrue(all(r.get('translation') for r in rows))
        discounts=[r for r in rows if '％割り引' in r['original']]
        self.assertEqual(len(discounts),8)
        for r in discounts:self.assertIn('减免',r['translation'])

if __name__=='__main__':unittest.main()
