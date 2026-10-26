import unittest
from pathlib import Path
from compile_translation import ROOT, read
from pack_dlc_draft import sha


class UpdateCiaTests(unittest.TestCase):
    def test_build_identity_and_pairing(self):
        report = read(ROOT/'translation/localized_update_cia.generated.json')
        manifest = read(ROOT/'translation/integrated_build.generated.json')
        self.assertEqual(report['title_id'], '0004000e000c3600')
        self.assertEqual(report['version'], 2096)
        self.assertEqual(report['encoding_sha256'], manifest['encoding_sha256'])
        self.assertEqual(report['integrated_manifest_sha256'], sha(ROOT/'translation/integrated_build.generated.json'))
        self.assertEqual(sha(Path(report['file'])), report['sha256'])
        self.assertEqual(report['exefs_inventory']['code.bin'], report['code_sha256'])
        self.assertTrue(report['cia_content_roundtrip_verified'])
        self.assertTrue(report['code_decompression_roundtrip_verified'])
        self.assertTrue(report['other_sections_preserved'])
        self.assertFalse(report['installed'])
        self.assertFalse(report['runtime_tested'])

    def test_manual_and_original_contents_unchanged(self):
        report = read(ROOT/'translation/localized_update_cia.generated.json')
        self.assertEqual([c['localized'] for c in report['contents']], [True, False])
        for row in report['contents']:
            self.assertEqual(sha(ROOT/'update'/f'cia_contents.{row["index"]}.{row["content_id"]}'), row['original_sha256'])
            self.assertEqual(sha(Path(row['file'])), row['sha256'])
        self.assertEqual(report['contents'][1]['sha256'], sha(ROOT/'cia_rebuild/update/0001/decrypted.cfa'))


if __name__ == '__main__':
    unittest.main()
