import unittest
from compile_translation import ROOT,read
from equipment_names import load_drafts,build,SOURCE
from q2_item_names import load
from q2_name_banks import load as load_banks,excluded

class ConsumableNameTests(unittest.TestCase):
    def test_entire_section_and_binary(self):
        draft=read(ROOT/'translation/consumable_names_completion.review.json')
        data,start,names,equipment=load_drafts();items=load()
        self.assertEqual(len(draft['rows']),30)
        selected={i for i in items if 1280<=i<1536}
        self.assertEqual(selected,{i for i in range(1281,1536) if not excluded(names[i])})
        self.assertEqual(len(selected)+len(draft['retained']),256)
        skills={r['index']:r for g in load_banks()['groups'] if g['source']=='battle/table/skillnametable.tbl' for r in g['rows']}
        for r in draft['rows']:
            if r['skill_index'] is not None:
                old=skills[r['skill_index']]
                self.assertEqual((old['original'],old['translation']),(r['original'],r['translation']))
        mapping=read(ROOT/'translation/font_encoding.hex.json')
        result=build(data,start,{**equipment,**items},mapping)
        self.assertEqual(result,(ROOT/'full_work/equipment_payload'/SOURCE).read_bytes())
        self.assertEqual(result[:start],data[:start])

if __name__=='__main__':unittest.main()
