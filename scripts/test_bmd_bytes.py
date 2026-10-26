"""Cross-check independent BMD parser against original helper exports."""
import re
import unittest
from compile_translation import ROOT, read, TOKEN
from bmd_bytes import read_document, parse


def original_bytes(text):
    return b''.join(bytes.fromhex(p[1:-1]) if TOKEN.fullmatch(p) else p.encode('cp932')
                    for p in re.split('('+TOKEN.pattern+')',text))


class ByteReaderTests(unittest.TestCase):
    def check_source(self, source, path, member=None):
        exported=read(ROOT/source)
        binary=read_document(ROOT/path,member)
        self.assertEqual(binary['speakers'],[original_bytes(s) for s in exported['speakers']])
        self.assertEqual(len(binary['texts']),len(exported['texts']))
        for got,want in zip(binary['texts'],exported['texts']):
            self.assertEqual(got['id'],want['id'])
            self.assertEqual(got['lines'],[original_bytes(s) for s in want['lines']])

    def test_bin_choices_and_control_bytes(self):
        self.check_source('export_base/title/difficultyselect.bin_difficultyselect.bmd.json',
                          'data/title/difficultyselect.bin','difficultyselect.bmd')

    def test_bf_speakers_and_multiple_pages(self):
        self.check_source('export_base/event/e100/e100_160.bf.json','data/event/e100/e100_160.bf')

    def test_rejects_non_bmd(self):
        with self.assertRaises(AssertionError):
            parse(b'\0'*64)

    def test_gsd_and_nested_arc_gsd(self):
        self.check_source('export_base/dungeon/script/dungeon11f.gsd_dungeon11f.bf.json',
                          'data/dungeon/script/dungeon11f.gsd', 'dungeon11f.bf')
        self.check_source('export_base/dungeon/pack/field/f02_01.arc_dungeon11f.gsd_dungeon11f.bf.json',
                          'data/dungeon/pack/field/f02_01.arc', 'dungeon11f.gsd_dungeon11f.bf')

    def test_identical_duplicate_group_date_questions(self):
        self.check_source('export_base/event/gcs.bin_gconSelectQuestionMessage.bmd.json',
                          'data/event/gcs.bin', 'gconSelectQuestionMessage.bmd')


if __name__=='__main__':
    unittest.main()
