"""Pinned authoring checks for hotpot choices and the 45% campus milestone."""
import re
import unittest
from compile_translation import ROOT, read, TOKEN


class HotpotCampusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenes = {}
        for path in (ROOT / 'translation/route_drafts').glob('*.json'):
            draft = read(path)
            if 211 <= int(draft['batch'].split('_')[0]) <= 219:
                for code, scene in draft['scenes'].items():
                    assert code not in cls.scenes
                    cls.scenes[code] = scene

    def page(self, code, mi, li=0):
        return next(t for i, j, t in self.scenes[code]['pages'] if (i, j) == (mi, li))

    def test_complete_pinned_sources(self):
        self.assertEqual(len(self.scenes), 62)
        self.assertEqual(sum(len(s['pages']) for s in self.scenes.values()), 2591)
        for code, scene in self.scenes.items():
            source = read(ROOT / f'export_base/event/e{code[1]}00/{code}.bf.json')
            expected = {(i, j) for i, m in enumerate(source['texts']) for j in range(len(m['lines']))}
            self.assertEqual({(i, j) for i, j, t in scene['pages']}, expected, code)
            for i, j, text in scene['pages']:
                self.assertIsNone(re.search('[\u3041-\u3096\u30a1-\u30fa]', TOKEN.sub('', text)), (code, i, j))

    def test_recipe_hints_match_choice_labels(self):
        highlighted = lambda t: re.findall(r'\{F2 01 03 01\}(.*?)\{F2 01 01 01\}', t, re.S)
        expected = {(9, 0): ['大葱', '白菜'], (9, 1): ['蘑菇'],
                    (10, 0): ['水菜', '大葱'], (10, 1): ['蘑菇'],
                    (11, 1): ['油豆腐', '豆腐皮'], (11, 2): ['豆腐皮', '粉丝'],
                    (11, 3): ['豆腐', '粉丝'], (11, 4): ['豆腐', '油豆腐']}
        for (mi, li), words in expected.items():
            self.assertEqual(highlighted(self.page('e821_530', mi, li)), words)
        for mi, choices in [(11, ['扇贝', '真鳕', '肉丸', '五花肉']),
                            (21, ['白菜', '大葱', '水菜', '蘑菇']),
                            (31, ['豆腐', '油豆腐', '豆腐皮', '粉丝'])]:
            self.assertEqual([self.page('e821_540', mi, j) for j in range(4)], choices)
        self.assertIn('３种', self.page('e821_530', 6, 1))

    def test_hotpot_outcomes_and_rewards(self):
        for mi, text in [(72, '特别满意'), (77, '似乎很满意'), (82, '没能打动')]:
            self.assertIn(text, self.page('e821_540', mi))
        for mi, token in [(3, '{F4 45 04 01 00 00 01 01}'),
                          (6, '{F4 45 04 01 00 00 02 01}'),
                          (8, '{F4 45 04 01 00 00 03 01}')]:
            self.assertEqual(TOKEN.findall(self.page('e821_550', mi)), [token])

    def test_route_specific_name_controls(self):
        for code, token in [('e905_250', '{F5 C1 10 01 01 01 01 01 01 01}'),
                             ('e915_250', '{F5 C1 0D 01 01 01 01 01 01 01}')]:
            self.assertEqual(TOKEN.findall(self.page(code, 5)), [token])
        self.assertIn('反过来', self.page('e905_250', 7, 1))
        self.assertEqual(self.page('e915_250', 7, 1), '不用了')
        self.assertIn('哥哥', self.page('e905_261', 32))
        self.assertIn('幼儿园', self.page('e915_261', 7))


if __name__ == '__main__':
    unittest.main()
