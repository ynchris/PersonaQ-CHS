"""Nested text replacement must keep opaque siblings, padding and BF code."""
import struct
import unittest
from compile_translation import ROOT
from check_roundtrip import parse_members
from nested_text_members import extract_nested, replace_nested


def container(rows, padding=b''):
    return struct.pack('<I', len(rows)) + b''.join(
        n.encode('ascii').ljust(32, b'\0') + struct.pack('<I', len(d)) + d
        for n, d in rows) + padding


class NestedTextTests(unittest.TestCase):
    def test_changes_nested_text_only_and_preserves_padding(self):
        before = container([('test.gsd', container([('map.tbl', b'MAP'), ('text.bmd', b'OLD')], b'\0'*20)), ('model.bam', b'MODEL')])
        rebuilt = container([('test.gsd', container([('map.tbl', b'CORRUPTED'), ('text.bmd', b'NEW LONGER')], b'\0'*5)), ('model.bam', b'CORRUPTED')])
        result, preserved = replace_nested(before, rebuilt, {'test.gsd_text.bmd'})
        expected = container([('test.gsd', container([('map.tbl', b'MAP'), ('text.bmd', b'NEW LONGER')], b'\0'*20)), ('model.bam', b'MODEL')])
        self.assertEqual(result, expected)
        self.assertEqual(preserved, 2)
        self.assertEqual(extract_nested(result, 'test.gsd_text.bmd'), b'NEW LONGER')

    def test_real_nested_bf_identity(self):
        for filename, selector in [('f02_01.arc', 'dungeon11f.gsd_dungeon11f.bf'),
                                   ('f03_04.arc', 'dungeon24f.gsd_dungeon24f.bf')]:
            original = (ROOT/'data/dungeon/pack/field'/filename).read_bytes()
            result, preserved = replace_nested(original, original, {selector})
            self.assertEqual(result, original)
            self.assertGreater(preserved, 0)

    def test_preserves_observed_header_copy_trailer(self):
        before = container([('text.bmd', b'OLD')])
        tail = before[:20]
        before += tail
        rebuilt = container([('text.bmd', b'LONGER NEW TEXT')])
        actual, _ = replace_nested(before, rebuilt, {'text.bmd'})
        self.assertEqual(actual, rebuilt + tail)
        self.assertEqual(extract_nested(actual, 'text.bmd'), b'LONGER NEW TEXT')

    def test_preserves_unselected_duplicate_names(self):
        before = container([('same.bin', b'A'), ('text.bmd', b'OLD'), ('same.bin', b'B')])
        rebuilt = container([('text.bmd', b'NEW')])
        actual, _ = replace_nested(before, rebuilt, {'text.bmd'})
        self.assertEqual(actual, container([('same.bin', b'A'), ('text.bmd', b'NEW'), ('same.bin', b'B')]))

    def test_updates_all_identical_bmd_duplicates(self):
        before = container([('q.bmd', b'OLD'), ('model.bam', b'KEEP'), ('q.bmd', b'OLD')])
        rebuilt = container([('q.bmd', b'LONGER'), ('model.bam', b'CHANGED'), ('q.bmd', b'LONGER')])
        actual, _ = replace_nested(before, rebuilt, {'q.bmd'})
        self.assertEqual(actual, container([('q.bmd', b'LONGER'), ('model.bam', b'KEEP'), ('q.bmd', b'LONGER')]))
        self.assertEqual(extract_nested(actual, 'q.bmd'), b'LONGER')

    def test_rejects_lost_or_divergent_duplicate_bmd(self):
        before = container([('q.bmd', b'OLD'), ('q.bmd', b'OLD')])
        for rows in [[('q.bmd', b'NEW')], [('q.bmd', b'NEW'), ('q.bmd', b'OTHER')]]:
            with self.assertRaises(ValueError):
                replace_nested(before, container(rows), {'q.bmd'})
        with self.assertRaises(ValueError):
            extract_nested(container([('q.bf', b'SAME'), ('q.bf', b'SAME')]), 'q.bf')

    def test_real_group_date_duplicate_bmd_identity(self):
        original = (ROOT/'data/event/gcs.bin').read_bytes()
        copies = [data for name, data in parse_members(original) if name == 'gconSelectQuestionMessage.bmd']
        self.assertEqual(len(copies), 2)
        self.assertEqual(copies[0], copies[1])
        actual, _ = replace_nested(original, original, {'gconSelectQuestionMessage.bmd', 'gconSelectQuestion.bf'})
        self.assertEqual(actual, original)

    def test_rejects_missing_duplicate_nontext_and_garbage(self):
        original = container([('map.tbl', b'MAP'), ('text.bmd', b'OLD')])
        for selector in ['missing.bmd', 'map.tbl']:
            with self.assertRaises(ValueError):
                replace_nested(original, original, {selector})
        duplicated = container([('text.bmd', b'A'), ('text.bmd', b'B')])
        with self.assertRaises(ValueError):
            extract_nested(duplicated, 'text.bmd')
        with self.assertRaises(AssertionError):
            parse_members(original + b'garbage', allow_padding=True)
        with self.assertRaises(AssertionError):
            parse_members(original[:-1], allow_padding=True)


if __name__ == '__main__':
    unittest.main()
