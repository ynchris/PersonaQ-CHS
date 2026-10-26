"""Regression checks for non-destructive BVP member replacement."""
import struct
import unittest
from repack_bvp_text import entries, replace_members


def fixture(payloads):
    output=bytearray((len(payloads)+1)*12)
    for index,payload in enumerate(payloads):
        output.extend(b'\0'*((-len(output))%16))
        struct.pack_into('<3I',output,index*12,0x10001+index*0x10000,len(output),len(payload))
        output.extend(payload)
    return bytes(output)


class BvpTests(unittest.TestCase):
    def test_longer_replacement_keeps_others_and_flags(self):
        old=fixture([b'original first',b'untouched second',b'untouched third'])
        new=fixture([b'translated first much longer',b'normalized second',b'normalized third'])
        result,preserved=replace_members(old,new,{'(000).BMD'})
        self.assertEqual(preserved,2)
        self.assertEqual(entries(result)[1:],entries(old)[1:])
        self.assertEqual(entries(result)[0][0],entries(old)[0][0])
        self.assertEqual(result[12:len(old)],old[12:])

    def test_multiple_replacements(self):
        old=fixture([b'a'*30,b'b'*31,b'c'*32])
        new=fixture([b'd',b'e'*100,b'f'*10])
        result,preserved=replace_members(old,new,{'(000).BMD','(002).BMD'})
        self.assertEqual(preserved,1)
        self.assertEqual(entries(result)[1],entries(old)[1])

    def test_reject_changed_flags(self):
        old=fixture([b'first'])
        new=bytearray(old)
        new[0]^=1
        with self.assertRaises(AssertionError):
            replace_members(old,new,{'(000).BMD'})

    def test_reject_bad_name(self):
        old=fixture([b'first'])
        with self.assertRaises(AssertionError):
            replace_members(old,old,{'other.bmd'})

    def test_reject_out_of_bounds(self):
        old=bytearray(fixture([b'first']))
        struct.pack_into('<I',old,8,0xffffffff)
        with self.assertRaises(AssertionError):
            entries(old)

    def test_reject_overlapping_payloads(self):
        old=bytearray(fixture([b'first',b'second']))
        struct.pack_into('<I',old,16,struct.unpack_from('<I',old,4)[0])
        with self.assertRaises(AssertionError):
            entries(old)

    def test_no_edits_identity(self):
        old=fixture([b'first',b'second'])
        result,preserved=replace_members(old,old,set())
        self.assertEqual(result,old)
        self.assertEqual(preserved,2)


if __name__=='__main__':
    unittest.main()
