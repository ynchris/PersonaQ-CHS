import unittest
from test_tables_448 import TableTailTests as Common
from compile_translation import ROOT,read
from check_roundtrip import members
from extract_fixed_tables import inspect
from raw_text_codec import encode_display
class ExpandedTableTests(Common):
    review_file='table_expansion_449.review.json'
    expected_count=135
    def test_layout_and_metadata(self):
        data=members(ROOT/'data/init/fcltable.bin');mapping=read(ROOT/'translation/font_encoding.hex.json')
        entries=read(ROOT/'translation'/self.review_file)['entries']
        for entry in entries:
            name,raw=data[entry['member_index']]
            extracted=inspect(raw,name)[entry['row']]
            self.assertEqual(extracted['original'],entry['original'])
            self.assertEqual(extracted['offset'],entry['offset'])
            self.assertEqual(extracted['capacity_bytes'],32)
            start=entry['offset'];end=start+32;out=bytearray(raw)
            out[start:end]=encode_display(entry['translation'],mapping).ljust(32,b'\0')
            self.assertEqual(len(out),len(raw));self.assertEqual(out[:start],raw[:start]);self.assertEqual(out[end:],raw[end:])
        with self.assertRaises(ValueError):inspect(data[65][1],data[65][0])
        with self.assertRaises(ValueError):inspect(data[103][1],data[103][0])
if __name__=='__main__':unittest.main()
