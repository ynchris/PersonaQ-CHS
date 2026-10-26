import hashlib
import re
import unittest
from compile_translation import ROOT, read
from raw_text_codec import encode_message
from audit_ui_456 import text_with_controls
from prepare_system_455 import PREFIX

class System456Tests(unittest.TestCase):
    def test_full_discovered_dialog_family(self):
        review=read(ROOT/'translation/system_456.review.json')
        mapping=read(ROOT/'translation/font_encoding.hex.json')
        self.assertEqual([len(f['rows']) for f in review['files']],[96,106])
        self.assertFalse(review['packaged'])
        for f in review['files']:
            raw=(ROOT/f['source']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),f['sha256'])
            self.assertEqual({m.end() for m in re.finditer(re.escape(PREFIX),raw)}, {r['offset'] for r in f['rows']})
            for r in f['rows']:
                data=raw[r['offset']:r['offset']+r['capacity_bytes']]
                self.assertEqual(data.hex(),r['original_hex'])
                self.assertEqual(text_with_controls(data),r['original'])
                self.assertEqual(re.findall(r'\{[0-9A-F ]+\}',r['original']),re.findall(r'\{[0-9A-F ]+\}',r['translation']))
                self.assertLessEqual(len(encode_message(r['translation'],mapping)),len(data))
                self.assertNotRegex(r['translation'],r'[ぁ-ゖァ-ヺ]')

    def test_reported_startup_and_dlc_messages_present(self):
        review=read(ROOT/'translation/system_456.review.json')
        for f in review['files']:
            translations='\n'.join(r['translation'] for r in f['rows'])
            self.assertIn('未插入SD卡时',translations)
            self.assertIn('保存完成',translations)
        self.assertIn('正在检查追加内容。', '\n'.join(r['translation'] for r in review['files'][1]['rows']))

    def test_inventory_is_not_claimed_complete(self):
        d=read(ROOT/'translation/ui_inventory_456.generated.json')
        self.assertFalse(d['coverage_complete'])
        self.assertEqual(d['image_groups']['tutorial'],46)
        self.assertEqual(len(d['tables']),146)

if __name__=='__main__':unittest.main()
