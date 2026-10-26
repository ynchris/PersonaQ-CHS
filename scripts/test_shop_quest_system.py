import hashlib
import json
import re
import unicodedata
import unittest
from collections import Counter
from pathlib import Path
from compile_translation import LEADING, TRAILING, TOKEN
from reviewed_test_expectations import authored_translation

ROOT = Path(__file__).resolve().parent

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

class ShopQuestTests(unittest.TestCase):
    def test_authored_batches_and_untouched_pages(self):
        for filename, count in [('345_workshop_infirmary_and_network.json',219), ('346_quest_objectives_both_routes.json',94)]:
            batch = read(ROOT/'translation/batches'/filename)
            self.assertEqual(sum(map(len,batch['sources'].values())), count)
            for source, rows in batch['sources'].items():
                self.assertEqual(hashlib.sha256((ROOT/source).read_bytes()).hexdigest(), batch['source_hashes'][source])
                old = read(ROOT/source)
                new = read(ROOT/'translation/compiled'/source)
                selected = set()
                for mi, li, mid, body in rows:
                    self.assertNotIn((mi,li), selected)
                    selected.add((mi,li))
                    original = old['texts'][mi]['lines'][li]
                    value = new['texts'][mi]['lines'][li]
                    self.assertEqual(old['texts'][mi]['id'],mid)
                    self.assertEqual(value,LEADING.match(original).group()+body+TRAILING.search(original).group())
                    self.assertEqual(TOKEN.findall(original),TOKEN.findall(value))
                    self.assertEqual(original.count('\n'),value.count('\n'))
                    numbers = lambda s: Counter(re.findall(r'\d+',unicodedata.normalize('NFKC',TOKEN.sub('',s))))
                    self.assertEqual(numbers(original),numbers(value))
                deferred=set()
                followup=read(ROOT/'translation/batches/381_q2_short_choices_and_prompts.generated.json')
                additions={(i,j):v for i,j,_,v in followup['sources'].get(source,[])}
                sweep=read(ROOT/'translation/batches/384_q2_normalized_sweep.generated.json')
                additions.update({(i,j):v for i,j,_,v in sweep['sources'].get(source,[])})
                for mi,li,body in batch['deferred_pages'][source]:
                    deferred.add((mi,li))
                    original=old['texts'][mi]['lines'][li]
                    self.assertEqual(body,TRAILING.sub('',LEADING.sub('',original)))
                    expected=original if (mi,li) not in additions else LEADING.match(original).group()+additions[mi,li]+TRAILING.search(original).group()
                    self.assertEqual(authored_translation(source,mi,li,original),new['texts'][mi]['lines'][li])
                self.assertFalse(selected & deferred)
                self.assertEqual(selected | deferred,{(i,j) for i,m in enumerate(old['texts']) for j in range(len(m['lines']))})
                for i,jp,zh in batch.get('speakers',{}).get(source,[]):
                    self.assertEqual(old['speakers'][i],jp)
                    self.assertEqual(new['speakers'][i],zh)

    def test_route_differences_and_objective_coverage(self):
        batch=read(ROOT/'translation/batches/346_quest_objectives_both_routes.json')
        a,b=batch['sources'].values()
        self.assertEqual([r[0] for r in a],list(range(1,48)))
        self.assertEqual([r[0] for r in b],list(range(1,48)))
        self.assertEqual([x[0] for x,y in zip(a,b) if x[3]!=y[3]],[11,32,37])
        self.assertIn('伊织',a[31][3])
        self.assertIn('天田',b[31][3])

    def test_limits_and_destructive_action_warnings(self):
        batch=read(ROOT/'translation/batches/345_workshop_infirmary_and_network.json')
        def rows(s):
            return {(i,j):v for i,j,mid,v in batch['sources']['export_base/facility/'+s]}
        net=rows('msg_network.bmd.json')
        self.assertIn('覆盖',net[8,0])
        self.assertIn('不把更新内容应用',net[43,0])
        self.assertIn('５',net[39,0])
        shop=rows('msg_weapon.bmd.json')
        self.assertIn('９９',shop[51,1])
        self.assertIn('９９',shop[51,2])
        office=rows('msg_noffice.bmd.json')
        self.assertIn('５',office[9,0])
        self.assertIn('不收取费用',office[20,2])

if __name__=='__main__':
    unittest.main()
