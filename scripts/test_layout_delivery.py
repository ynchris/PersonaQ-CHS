import unittest
from compile_translation import ROOT,read
from pack_dlc_draft import sha
from pathlib import Path


class LayoutDeliveryTests(unittest.TestCase):
    def test_all_remaining_warnings_have_an_honest_disposition(self):
        queue=read(ROOT/'translation/layout_queue.generated.json')
        warnings={w['key'] for w in read(ROOT/'translation/progress.generated.json')['warnings'] if w['kind']=='layout_review'}
        self.assertEqual({r['key'] for r in queue['rows']},warnings)
        self.assertEqual(sum(queue['categories'].values()),len(warnings))
        self.assertFalse(queue['all_layout_complete'])
        self.assertTrue(all(not r['runtime_verified'] for r in queue['rows']))

    def test_base_cxi_matches_packaged_set(self):
        report=read(ROOT/'translation/localized_base_cxi.generated.json')
        packaged=read(ROOT/'translation/installable_set.generated.json')
        self.assertEqual(report['integrated_manifest_sha256'],packaged['integrated_manifest_sha256'])
        self.assertEqual(report['encoding_sha256'],packaged['encoding_sha256'])
        self.assertEqual(report['title_id'],'00040000000c3600')
        self.assertFalse(report['original_rom_modified'])
        self.assertFalse(report['runtime_tested'])
        self.assertTrue(report['romfs_inventory_verified'] and report['cxi_sections_verified'] and report['exefs_roundtrip_verified'])
        self.assertEqual(sha(Path(report['file'])),report['sha256'])
        self.assertEqual(next(r['sha256'] for r in packaged['resources'] if r['kind']=='base_cxi'),report['sha256'])


if __name__=='__main__':unittest.main()
