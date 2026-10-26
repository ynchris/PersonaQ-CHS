import unittest
import test_facility_423 as common
from compile_translation import ROOT,read,TOKEN
class TradeTests(common.FacilityTutorialTests):
    batch_name='434_trade_shop_reuse.generated.json'
    page_count=93
    def test_reuse(self):
        batch=read(ROOT/'translation/batches'/self.batch_name)
        catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')}
        self.assertEqual(len(batch['reuse_audit']),88)
        for r in batch['reuse_audit']:
            ref=catalog[r['reference_key']];target=catalog[r['target_key']]
            self.assertEqual(TOKEN.sub('',ref['original']),TOKEN.sub('',target['original']))
            self.assertEqual(TOKEN.sub('',ref['translation']),TOKEN.sub('',target['translation']))
            self.assertEqual(TOKEN.findall(target['original']),TOKEN.findall(target['translation']))
if __name__=='__main__':unittest.main()
