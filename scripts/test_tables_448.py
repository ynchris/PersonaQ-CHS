import hashlib,unittest
from compile_translation import ROOT,read
from check_roundtrip import members
from raw_text_codec import encode_display,decode_display
class TableTailTests(unittest.TestCase):
    review_file='table_tail_448.review.json'
    expected_count=79
    def test_sources_capacity_and_encoding(self):
        entries=read(ROOT/'translation'/self.review_file)['entries'];self.assertEqual(len(entries),self.expected_count)
        mapping=read(ROOT/'translation/font_encoding.hex.json')
        compiled={r['key']:r for r in read(ROOT/'translation/tables.catalog.working.json')}
        banks={s:members(ROOT/'data'/s) for s in {r['source'] for r in entries}}
        for r in entries:
            name,data=banks[r['source']][r['member_index']]
            self.assertEqual(name,r['member_name']);self.assertEqual(hashlib.sha256(data).hexdigest(),r['member_sha256'])
            start=r['offset'];cap=r['capacity_bytes']
            self.assertEqual(data[start:start+cap].rstrip(b'\0').decode('cp932'),r['original'])
            encoded=encode_display(r['translation'],mapping)
            self.assertLess(len(encoded),cap)
            self.assertEqual(decode_display(encoded,mapping),r['translation'])
            self.assertEqual(compiled[r['key']]['translation'],r['translation'])
if __name__=='__main__':unittest.main()
