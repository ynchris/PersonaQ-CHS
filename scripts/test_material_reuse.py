import hashlib
import re
import unittest
import unicodedata
from collections import Counter
from compile_translation import ROOT, read, TOKEN, LEADING, TRAILING


class MaterialReuseTests(unittest.TestCase):
    def test_completion_383(self):
        source='export_base/init/datmaterialhelp.bmd.json'
        batch=read(ROOT/'translation/batches/383_materials_completion.generated.json')
        audit=read(ROOT/'translation/383_materials_completion.audit.generated.json')
        old,new=read(ROOT/source),read(ROOT/'translation/compiled'/source)
        self.assertEqual(hashlib.sha256((ROOT/source).read_bytes()).hexdigest(),batch['source_hashes'][source])
        rows=batch['sources'][source]
        self.assertEqual(len(rows),129)
        ref_path=ROOT.parent/audit['reference']
        self.assertEqual(hashlib.sha256(ref_path.read_bytes()).hexdigest(),audit['reference_sha256'])
        self.assertEqual(hashlib.sha256((ROOT/'translation/persona_names.review.json').read_bytes()).hexdigest(),audit['persona_draft_sha256'])
        refs=read(ref_path)
        entries={e['index']:e for e in audit['entries']}
        from persona_names import load_drafts
        _,names,translated=load_drafts()
        name_map={names[i]:t for i,t in translated.items()}
        for i,j,mid,body in rows:
            original=old['texts'][i]['lines'][j]
            self.assertEqual(mid,old['texts'][i]['id'])
            full=LEADING.match(original).group()+body+TRAILING.search(original).group()
            self.assertEqual(full,new['texts'][i]['lines'][j])
            self.assertEqual(TOKEN.findall(full),TOKEN.findall(original))
            self.assertEqual(body,entries[i]['final_body'])
            nums=lambda s:Counter(re.findall(r'\d+',unicodedata.normalize('NFKC',TOKEN.sub('',s))))
            self.assertEqual(nums(full),nums(original))
            self.assertLessEqual(max(map(len,body.splitlines())),max(map(len,TOKEN.sub('',original).splitlines())))
            for ref in entries[i]['enemy_references']:
                self.assertIn('討伐：'+ref['original'],original)
                self.assertIn('讨伐：'+ref['translation'],body)
                self.assertTrue(any(all(r.get(k)==v for k,v in ref.items()) for r in refs))
            for jp,zh in entries[i]['persona_name_reuse'].items():
                self.assertEqual(zh,name_map[jp])
                self.assertIn(jp,original)
                self.assertIn(zh,body)
        for row in read(ROOT/'translation/catalog.working.json'):
            if row['source']==source and not row.get('translation'):
                self.assertRegex(row['original'],r'ID_|ダミ|ブランク|リザーブ|枠最後')
                i,j=row['message_index'],row['line_index']
                self.assertEqual(old['texts'][i]['lines'][j],new['texts'][i]['lines'][j])

    def test_materials_382(self):
        batch=read(ROOT/'translation/batches/382_materials_q2_enemy_names.generated.json')
        audit=read(ROOT/'translation/382_materials_q2_enemy_names.audit.generated.json')
        source='export_base/init/datmaterialhelp.bmd.json'
        old=read(ROOT/source)
        new=read(ROOT/'translation/compiled'/source)
        self.assertEqual(hashlib.sha256((ROOT/source).read_bytes()).hexdigest(),batch['source_hashes'][source])
        rows=batch['sources'][source]
        self.assertEqual(len(rows),52)
        self.assertEqual(len({(i,j) for i,j,_,_ in rows}),52)
        entries={r['key']:r for r in audit['entries']}
        self.assertEqual(len(entries),52)
        ref_path=ROOT.parent/audit['reference']
        self.assertEqual(hashlib.sha256(ref_path.read_bytes()).hexdigest(),audit['reference_sha256'])
        refs=read(ref_path)
        for i,j,mid,body in rows:
            original=old['texts'][i]['lines'][j]
            self.assertNotIn('ID_',original)
            self.assertEqual(mid,old['texts'][i]['id'])
            full=LEADING.match(original).group()+body+TRAILING.search(original).group()
            self.assertEqual(full,new['texts'][i]['lines'][j])
            self.assertEqual(TOKEN.findall(full),TOKEN.findall(original))
            nums=lambda s:Counter(re.findall(r'\d+',unicodedata.normalize('NFKC',TOKEN.sub('',s))))
            self.assertEqual(nums(full),nums(original))
            self.assertLessEqual(max(map(len,body.splitlines())),max(map(len,TOKEN.sub('',original).splitlines())))
            self.assertEqual(len(body.splitlines()),len(TOKEN.sub('',original).strip().splitlines()))
            entry=entries[f'{source}:{i}:{j}']
            self.assertEqual(body,entry['final_body'])
            for ref in entry['enemy_name_references']:
                self.assertIn('討伐：'+ref['original'],original)
                self.assertIn('讨伐：'+ref['translation'],body)
                self.assertTrue(any(all(r.get(k)==v for k,v in ref.items()) for r in refs))
        self.assertEqual(sum(bool(r['enemy_name_references']) for r in entries.values()),51)
        for i in [202,208,220,222,223,224,238,266]:
            self.assertEqual(old['texts'][i],new['texts'][i])


if __name__=='__main__':
    unittest.main()
