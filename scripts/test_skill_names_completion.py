import re
import unittest
from compile_translation import ROOT,read
from q2_name_banks import load,build_bank
from q2_item_names import load as load_items
from complete_skill_names import EXTRA,INTERNAL,marker

class SkillNameCompletionTests(unittest.TestCase):
    def test_complete_scope_and_provenance(self):
        extra=read(EXTRA)
        self.assertEqual(len(extra['rows']),141)
        self.assertEqual(len({r['original'] for r in extra['rows']}),113)
        group=next(g for g in load()['groups'] if g['source']==extra['source'])
        self.assertEqual(len(group['rows']),755)
        self.assertEqual(len(group['excluded']),621)
        self.assertEqual({r['index'] for r in group['rows']+group['excluded']},set(range(1376)))
        catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')}
        items=load_items()
        for r in extra['rows']:
            self.assertNotIn(r['index'],INTERNAL)
            self.assertFalse(marker(r['original']))
            ref=r['local_reference']
            if ref and ref.startswith('itemtbl:'):
                self.assertEqual(r['translation'],items[int(ref.split(':')[1])])
            elif ref:
                self.assertIn('“'+r['original']+'”',catalog[ref]['original'])
                match=re.search('[“「](.*?)[”」]',catalog[ref]['translation'])
                self.assertEqual(r['translation'],match[1])
        mapping=read(ROOT/'translation/font_encoding.hex.json')
        result=build_bank((ROOT/'data'/group['source']).read_bytes(),1376,group['rows'],mapping)
        self.assertEqual(result,(ROOT/'full_work/q2_name_payload'/group['source']).read_bytes())

if __name__=='__main__':unittest.main()
