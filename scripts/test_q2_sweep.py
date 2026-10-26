import hashlib
import re
import unittest
from collections import defaultdict
from compile_translation import ROOT,read,TOKEN
from scan_q2_sweep import normalized
from scan_latest_q2_myth import LATEST
from q2_name_banks import load,parse,build_bank,excluded
from raw_text_codec import encode_display

class SweepTests(unittest.TestCase):
    def test_all_catalog_candidates_accounted(self):
        index=defaultdict(list)
        for p in LATEST.rglob('*.json'):
            for r in read(p):
                if isinstance(r,dict) and r.get('original') and r.get('translation'):
                    index[normalized(r['original'])].append(r)
        audit=read(ROOT/'translation/q2_sweep_384.audit.generated.json')['entries']
        statuses={r['key']:r['status'] for r in audit}
        self.assertEqual(len(statuses),606)
        self.assertEqual(sum(v=='applied' for v in statuses.values()),230)
        candidates=read(ROOT/'translation/q2_sweep_384.candidates.generated.json')
        self.assertEqual(set(statuses),{r['key'] for r in candidates})
        for row in read(ROOT/'translation/catalog.working.json'):
            if not row.get('translation') and normalized(row['original']) in index:
                if row['key'] not in statuses:
                    text=TOKEN.sub('',row['original'])
                    if '/gsobserver' in row['source']:
                        self.assertIn(text.strip(),{'TEST NONE','TEST NEWGAME','TEST GAMEOVER'})
                    else:self.assertIsNotNone(re.fullmatch(r'[\s…。＞？！]*',text))
                    continue
                self.assertIn(row['key'],statuses)
                self.assertNotEqual(statuses[row['key']],'applied')
        for r in audit:
            if r['status']!='applied':continue
            new=read(ROOT/'translation/compiled'/r['source'])['texts'][r['message_index']]['lines'][r['line_index']]
            self.assertEqual(TOKEN.findall(r['original']),TOKEN.findall(new))
            for ref in r['references']:
                self.assertEqual(hashlib.sha256((LATEST/ref['reference']).read_bytes()).hexdigest(),ref['sha256'])
                self.assertEqual(normalized(ref['original']),normalized(r['original']))
        for source,count in [('attraction/attrnametable.tbl',93),('attraction/attrquestnametable.tbl',30),('attraction/schwalkname.tbl',217)]:
            names=[c[:-1].decode('cp932') for c in parse((ROOT/'data'/source).read_bytes(),count)]
            self.assertFalse([x for x in names if not excluded(x) and normalized(x) in index])

    def test_fixed_tables_and_pending(self):
        for name in ['q2_sweep_384','q2_name_banks','q2_item_names']:
            self.assertEqual(read(ROOT/'translation'/f'{name}.pending.generated.json'),[])
        draft=read(ROOT/'translation/q2_fixed_rows.review.generated.json')
        self.assertEqual(len(draft['entries']),43)
        self.assertEqual(len(draft['excluded']),79)
        mapping=read(ROOT/'translation/font_encoding.hex.json')
        for r in draft['entries']:
            self.assertLess(len(encode_display(r['translation'],mapping)),r['capacity_bytes'])

    def test_name_banks_and_item_binary(self):
        mapping=read(ROOT/'translation/font_encoding.hex.json')
        groups=load()['groups']
        extras=read(ROOT/'translation/enemy_names_completion.review.json')['rows']
        self.assertEqual(len(extras),38)
        catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')}
        for entry in extras:
            for key in entry['local_catalog_references']:
                self.assertIn('討伐：'+entry['original']+'\n',catalog[key]['original'])
                self.assertIn('讨伐：'+entry['translation']+'\n',catalog[key]['translation'])
        skills=read(ROOT/'translation/skill_names_completion.review.json')['rows']
        self.assertEqual(sum(len(g['rows']) for g in groups),995+len(extras)+len(skills))
        enemy=next(g for g in groups if g['source']=='battle/table/enemynametable.tbl')
        self.assertEqual(len(enemy['rows']),335)
        self.assertEqual(len(enemy['excluded']),33)
        self.assertTrue(all(r['original']=='ｂｌａｎｋ' or r['reason']=='placeholder_or_internal' for r in enemy['excluded']))
        for g in groups:
            self.assertEqual(len(g['rows'])+len(g['excluded']),g['count'])
            self.assertEqual(hashlib.sha256((LATEST/g['reference']).read_bytes()).hexdigest(),g['reference_sha256'])
            output=build_bank((ROOT/'data'/g['source']).read_bytes(),g['count'],g['rows'],mapping)
            self.assertEqual(output,(ROOT/'full_work/q2_name_payload'/g['source']).read_bytes())
        from equipment_names import load_drafts,build,SOURCE
        from q2_item_names import load as extra,DRAFT
        data,start,names,rows=load_drafts();added=extra()
        consumables=read(ROOT/'translation/consumable_names_completion.review.json')['rows']
        item_completion=read(ROOT/'translation/item_names_completion.review.json')['rows']
        self.assertEqual(len(added),632+len(consumables)+len(item_completion))
        self.assertFalse(set(rows)&set(added))
        d=read(DRAFT)
        self.assertEqual(len(rows)+len(d['rows'])+len(d['excluded']),len(names))
        for r in d['rows']:
            self.assertTrue(any(x['original']==r['original'] and x['translation'].strip()==r['translation'] for x in r['references']))
        self.assertEqual(build(data,start,{**rows,**added},mapping),(ROOT/'full_work/equipment_payload'/SOURCE).read_bytes())

if __name__=='__main__':unittest.main()
