import hashlib
import unittest
from collections import Counter
from compile_translation import ROOT,read,TOKEN,LEADING,TRAILING
from raw_text_codec import encode_display,decode_display

class SharedNavigationTests(unittest.TestCase):
    def test_provenance_and_complete_matches(self):
        batch=read(ROOT/'translation/batches/391_shared_dlc_navigation.generated.json')
        audit=read(ROOT/'translation/391_shared_dlc_navigation.audit.generated.json')
        rows=read(ROOT/'translation/catalog.working.json');catalog={r['key']:r for r in rows}
        self.assertEqual(len(audit['entries']),200)
        self.assertEqual(audit['counts'],{'0005':50,'0007':50,'0008':50,'0009':50})
        mapping=read(ROOT/'translation/font_encoding.hex.json')
        for source,sha in batch['source_hashes'].items():self.assertEqual(hashlib.sha256((ROOT/source).read_bytes()).hexdigest(),sha)
        for entry in audit['entries']:
            row=catalog[entry['key']];ref=catalog[entry['reference_key']]
            self.assertEqual(row['original'],ref['original'])
            self.assertEqual(row['translation'],ref['translation'])
            self.assertEqual(row['translation'],entry['translation'])
            self.assertEqual(ref['batch'],entry['reference_batch'])
            self.assertEqual(TOKEN.findall(row['original']),TOKEN.findall(row['translation']))
            text=TOKEN.sub('',row['translation'])
            self.assertEqual(decode_display(encode_display(text,mapping),mapping),text)
            doc=read(ROOT/'translation/compiled'/row['source'])
            self.assertEqual(doc['texts'][row['message_index']]['lines'][row['line_index']],row['translation'])
        exact={r['original'] for r in rows if r.get('translation') and r['source'].startswith('export_dlc/0006/battle/support/')}
        self.assertFalse([r['key'] for r in rows if not r.get('translation') and r['source'].startswith('export_dlc/') and '/battle/support/' in r['source'] and r['original'] in exact])

if __name__=='__main__':unittest.main()
