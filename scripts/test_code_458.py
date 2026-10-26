import struct
import unittest
from compile_translation import ROOT,read
from raw_text_codec import encode_display

class Arcana458Tests(unittest.TestCase):
    def test_all_three_tables_resolve_all_names(self):
        review=read(ROOT/'translation/code_extra_458.review.json')
        mapping=read(ROOT/'translation/font_encoding.hex.json')
        self.assertFalse(review['code_written'])
        for f in review['files']:
            raw=(ROOT/f['source']).read_bytes()
            labels=[r for r in f['rows'] if 'pointer_slots' in r]
            self.assertEqual(len(labels),22)
            for r in labels:
                self.assertEqual(len(r['pointer_slots']),3)
                for slot in r['pointer_slots']:
                    self.assertEqual(struct.unpack_from('<I',raw,slot)[0]-0x100000,r['offset'])
                self.assertLessEqual(len(encode_display(r['translation'],mapping)),r['capacity_bytes'])

    def test_shared_tower_is_not_zero_padded(self):
        review=read(ROOT/'translation/code_extra_458.review.json')
        mapping=read(ROOT/'translation/font_encoding.hex.json')
        for f in review['files']:
            parent=next(r for r in f['rows'] if r['original']=='時計塔')
            tower=next(r for r in f['rows'] if r['original']=='塔')
            self.assertEqual(tower['offset'],parent['offset']+4)
            self.assertEqual(encode_display(parent['translation'],mapping)[4:],encode_display('塔',mapping))
            self.assertEqual(parent['supersedes_translation'],'钟楼')

if __name__=='__main__':unittest.main()
