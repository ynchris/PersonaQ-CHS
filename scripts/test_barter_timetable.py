"""Content invariants for the localized timetable and barter quest drafts."""
import re
import unittest
from compile_translation import ROOT, read, TOKEN


class QuestContentTests(unittest.TestCase):
    def test_timetable_cells_and_answers(self):
        scene = read(ROOT/'translation/route_drafts/timetable_puzzle.json')['scenes']['e723_115']
        pages = {(i, j): s for i, j, s in scene['pages']}
        source = read(ROOT/'export_base/event/e700/e723_115.bf.json')
        courses = ['社会', '技术', '美术', '国语', '音乐', '理科', '数学', '家政', '英语', '综合', '保健体育']
        expected = (courses * 3)[:25]
        tables = 0
        for (mi, li), text in pages.items():
            clean = TOKEN.sub('', text)
            if not clean.startswith('课程表\n'):
                continue
            tables += 1
            rows = clean.splitlines()[1:]
            self.assertEqual(len(rows), 5)
            cells = []
            for day, row in zip('一二三四五', rows):
                label, values = row.split('：')
                self.assertEqual(label, day)
                values = values.split('、')
                self.assertEqual(len(values), 5)
                cells.extend(values)
            for actual, full in zip(cells, expected):
                self.assertIn(actual, (full, full[0], '－', '？'))
            jp = TOKEN.sub('', source['texts'][mi]['lines'][li])
            jp_cells = [v for row in jp.splitlines()[1:] for v in row.split('：')[1].split('、')]
            self.assertEqual([i for i, v in enumerate(cells) if v in ('－', '？')],
                             [i for i, v in enumerate(jp_cells) if v in ('－', '？')])
        self.assertEqual(tables, 13)
        self.assertEqual(pages[53, 0], expected[3])
        self.assertEqual(pages[57, 2], expected[22])
        self.assertFalse(any(re.search('[ぁ-ヿ]', s) for s in pages.values()))

    def test_barter_all_source_pages_authored(self):
        scenes = {}
        for path in (ROOT/'translation/route_drafts').glob('barter_contest_*.json'):
            for code, scene in read(path)['scenes'].items():
                self.assertNotIn(code, scenes)
                scenes[code] = scene
        self.assertEqual(len(scenes), 15)
        for code, scene in scenes.items():
            doc = read(ROOT/f'export_base/event/e800/{code}.bf.json')
            expected = {(i, j) for i, m in enumerate(doc['texts']) for j in range(len(m['lines']))}
            self.assertEqual({(i, j) for i, j, s in scene['pages']}, expected, code)


if __name__ == '__main__':
    unittest.main()
