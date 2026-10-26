import hashlib
import unittest
from compile_translation import ROOT, read, TOKEN
from raw_text_codec import encode_message


class Review451Tests(unittest.TestCase):
    def test_exact_corrections_and_control_streams(self):
        rows=read(ROOT/'translation/text_corrections.review.json')['rows']
        rows=[r for r in rows if not r['reason'].startswith(('452','453','454'))]
        catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')}
        mapping=read(ROOT/'translation/font_encoding.hex.json')
        self.assertEqual(len(rows),5)
        for row in rows:
            self.assertEqual(catalog[row['key']]['translation'],row['after'])
            self.assertEqual(TOKEN.findall(row['original']),TOKEN.findall(row['after']))
            self.assertEqual(TOKEN.findall(row['before']),TOKEN.findall(row['after']))
            encode_message(row['after'],mapping)
            if '640.bf' in row['key']:
                self.assertEqual(len(TOKEN.sub('',row['after']).splitlines()),3)
                self.assertLess(max(map(len,TOKEN.sub('',row['after']).splitlines())),max(map(len,TOKEN.sub('',row['before']).splitlines())))
            else:
                self.assertIn('１个平假名',row['after'])

    def test_numeric_snapshot_review_is_not_blanket_suppression(self):
        audit=read(ROOT/'translation/numeric_review_451.json')
        self.assertEqual(len(audit['rows']),236)
        for row in audit['rows']:
            self.assertEqual(hashlib.sha256(row['translation'].encode('utf-8')).hexdigest(),row['translation_sha256'])
        report=read(ROOT/'translation/warning_disposition.generated.json')
        self.assertEqual(report['numeric_review_pending'],0)
        self.assertEqual(len(report['numeric_dispositions']),233)
        self.assertEqual(report['warning_counts']['numeric_review'],233)
        self.assertTrue(report['compiler_warnings_preserved'])
        self.assertEqual(report['layout_review_pending'],sum(w['kind']=='layout_review' for w in read(ROOT/'translation/progress.generated.json')['warnings']))


if __name__=='__main__':unittest.main()
