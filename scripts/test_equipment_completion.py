import hashlib
import json
import re
import unittest
from pathlib import Path
from compile_translation import ROOT,TOKEN,LEADING,TRAILING
from extract_fixed_tables import inspect
from check_roundtrip import members
from raw_text_codec import encode_display

def read(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8-sig'))

class EquipmentCompletionTests(unittest.TestCase):
    def test_batches(self):
        for number,count in [(360,95),(361,100),(362,92),(363,4),(364,160),(365,60),(366,60),(367,482),(368,50),(369,43),(370,27),(371,4),(372,24),(373,45),(374,24),(375,24),(376,24),(377,26),(378,1)]:
            batch=read(next((ROOT/'translation/batches').glob(str(number)+'_*.json')))
            self.assertEqual(sum(len(r) for r in batch['sources'].values()),count)
            for source,rows in batch['sources'].items():
                self.assertEqual(hashlib.sha256((ROOT/source).read_bytes()).hexdigest(),batch['source_hashes'][source])
                doc=read(source)
                compiled=read('translation/compiled/'+source)
                self.assertEqual(len({(r[0],r[1]) for r in rows}),len(rows))
                for mi,li,mid,body in rows:
                    with self.subTest(batch=number,index=mi):
                        original=doc['texts'][mi]['lines'][li]
                        value=LEADING.match(original).group()+body+TRAILING.search(original).group()
                        self.assertEqual(doc['texts'][mi]['id'],mid)
                        self.assertEqual(compiled['texts'][mi]['lines'][li],value)
                        self.assertEqual(TOKEN.findall(original),TOKEN.findall(value))
                        self.assertLessEqual(max(map(len,TOKEN.sub('',body).splitlines())),max(map(len,TOKEN.sub('',original).splitlines())))

    def test_no_untranslated_informative_descriptions(self):
        catalog=read('translation/catalog.working.json')
        for group in ['weapon','armor','accessory']:
            source=f'export_base/init/dat{group}help.bmd.json'
            remaining=[r for r in catalog if r['source']==source and not r.get('translation')]
            for row in remaining:
                self.assertRegex(row['original'],r'ID_|ブランク|ダミー|枠最後')
        for row in catalog:
            if row['source']=='export_base/init/dataddeffecthelp.bmd.json' and not row.get('translation'):
                self.assertEqual(TOKEN.sub('',row['original']).strip(),'なし')

    def test_scoped_shop_layout(self):
        original=members(ROOT/'data/init/fcltable.bin')
        mapping=read('translation/font_encoding.hex.json')
        batch=read('translation/table_batches/01_equipment_shop.json')
        for member in batch['members']:
            name,data=original[member['index']]
            rows=inspect(data,name)
            self.assertEqual([r['original'] for r in rows],[x[0] for x in member['rows']])
            for row,(_,text) in zip(rows,member['rows']):
                self.assertLess(len(encode_display(text,mapping)),row['capacity_bytes'])
        # 449 intentionally recognizes valid 32-byte text layouts independent
        # of filename. A broken row-count header must still be rejected.
        self.assertEqual(inspect(original[0][1],'unrecognized.ftd'),inspect(original[0][1],original[0][0]))
        damaged=bytearray(original[0][1]);damaged[4:8]=b'\0'*4
        with self.assertRaises(ValueError):
            inspect(bytes(damaged),'unrecognized.ftd')

if __name__=='__main__':
    unittest.main()
