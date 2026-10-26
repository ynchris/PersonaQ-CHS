import unittest
from plan_raw_font import allocate, valid_pair
from raw_text_codec import validate, encode_display, decode_display, literal_message


class RawFontTests(unittest.TestCase):
    def test_hex_seed_assignments_are_stable(self):
        mapping, _, _ = allocate({'译','汉'},set(),{'译':'81AD'},hexadecimal=True)
        self.assertEqual(mapping['译'],0x81ad)
        self.assertNotEqual(mapping['汉'],0x81ad)

    def test_full_capacity_fails_instead_of_overwriting(self):
        reserved={c for c in range(0x8140,0xeffd) if valid_pair(c)}
        with self.assertRaises(ValueError):
            allocate({'译'},reserved,{},hexadecimal=True)

    def test_byte_codec_roundtrip(self):
        mapping={'译':'81AD','文':'95B6'}
        validate(mapping)
        text='译文 A\n'
        self.assertEqual(decode_display(encode_display(text,mapping),mapping),text)

    def test_byte_codec_rejects_missing_and_controls(self):
        with self.assertRaises(ValueError):
            encode_display('译',{})
        with self.assertRaises(ValueError):
            validate({'译':'F040'})
        with self.assertRaises(ValueError):
            validate({'译':'81AD','字':'81AD'})

    def test_message_controls_preserved(self):
        self.assertEqual(literal_message('{F1 41}译\n{00}',{'译':'81AD'}),
                         '{F1 41}{81 AD}\n{00}')

    def test_controls_and_invalid_trails(self):
        for c in (0xf040, 0xfa40, 0x817f, 0x813f, 0x81fd, 0xa040):
            self.assertFalse(valid_pair(c))
        for c in (0x8140, 0x9ffc, 0xe040, 0xeffc):
            self.assertTrue(valid_pair(c))

    def test_preserve_original_and_existing_map(self):
        old = {'游':'遊'}
        reserved = {0x8140, int.from_bytes('遊'.encode('cp932'), 'big')}
        mapping, _, missing = allocate(set('游译'), reserved, old)
        self.assertEqual(mapping['游'], int.from_bytes('遊'.encode('cp932'), 'big'))
        self.assertNotIn(mapping['译'], reserved)
        self.assertIn('译', missing)

    def test_undefined_pairs_are_available(self):
        reserved = set()
        for c in range(0x8140, 0xeffd):
            if valid_pair(c):
                try:
                    c.to_bytes(2, 'big').decode('cp932')
                    reserved.add(c)
                except UnicodeError:
                    pass
        mapping, _, _ = allocate({'译'}, reserved, {})
        with self.assertRaises(UnicodeError):
            mapping['译'].to_bytes(2, 'big').decode('cp932')


if __name__ == '__main__':
    unittest.main()
