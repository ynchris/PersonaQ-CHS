import unittest
from compile_translation import ROOT,read
from raw_text_codec import encode_display

class QuestFacilityTests(unittest.TestCase):
    def test_titles_and_capacity(self):
        draft=read(ROOT/'translation/quest_facility_completion.review.json')
        rows=read(ROOT/'translation/tables.catalog.working.json')
        lookup={r['key']:r for r in rows}
        mapping=read(ROOT/'translation/font_encoding.hex.json')
        for entry in draft['entries']:
            self.assertEqual(lookup[entry['key']]['translation'],entry['translation'])
            self.assertLess(len(encode_display(entry['translation'],mapping)),entry['capacity_bytes'])
        quest=[r for r in rows if r['member_name']=='qstQuestNameText.qtd']
        self.assertEqual([r['row'] for r in quest if not r.get('translation')],[0,48,49])
        self.assertEqual(len([r for r in quest if r.get('translation')]),47)

if __name__=='__main__':unittest.main()
