import unittest
from compile_translation import ROOT,read
from equipment_names import load_drafts,build,SOURCE
from q2_item_names import load
from q2_name_banks import excluded,load as banks

class ItemCompletionTests(unittest.TestCase):
    def test_all_sections(self):
        data,start,names,equipment=load_drafts();items=load()
        draft=read(ROOT/'translation/item_names_completion.review.json')
        self.assertEqual(len(draft['rows']),151)
        self.assertEqual(len(equipment)+len(items),1509)
        for i in range(1536,len(names)):
            if i not in items:
                self.assertTrue(excluded(names[i]) or names[i].endswith('開始') or names[i].startswith('条件つき') or i in {1733,3156},(i,names[i]))
        skills={r['index']:r for g in banks()['groups'] if g['source']=='battle/table/skillnametable.tbl' for r in g['rows']}
        for r in draft['rows']:
            if r['skill_index'] is not None:
                s=skills[r['skill_index']]
                self.assertEqual((s['original'],s['translation']),(r['original'],r['translation']))
        self.assertEqual(items[2313],'奴延之爪')
        self.assertEqual(items[2314],'丝卡蒂的弓片')
        mapping=read(ROOT/'translation/font_encoding.hex.json')
        binary=build(data,start,{**equipment,**items},mapping)
        self.assertEqual(binary,(ROOT/'full_work/equipment_payload'/SOURCE).read_bytes())
        self.assertEqual(binary[:start],data[:start])

if __name__=='__main__':unittest.main()
