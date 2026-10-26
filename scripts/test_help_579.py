import unittest,json
from pathlib import Path
from check_roundtrip import members
from extract_fixed_tables import inspect
from raw_text_codec import encode_display,decode_display
R=Path(__file__).resolve().parent
class Help579Tests(unittest.TestCase):
    def test_all_facility_help_rows_covered(self):
        cat=json.loads((R/'translation/tables.catalog.working.json').read_text(encoding='utf-8'))
        lookup={r['key']:r for r in cat};mapping=json.loads((R/'translation/font_encoding.hex.json').read_text(encoding='utf-8'))
        for i,(name,b) in enumerate(members(R/'data/init/fcltable.bin')):
            if not name.startswith('fclHelpTable_'):continue
            for row in inspect(b,name):
                r=lookup[f'init/fcltable.bin:{i}:{name}:{row["row"]}'];self.assertTrue(r['translation'])
                e=encode_display(r['translation'],mapping);self.assertLess(len(e),row['capacity_bytes']);self.assertEqual(decode_display(e,mapping),r['translation'])
    def test_short_tail_still_checked(self):
        b=dict(members(R/'data/init/fcltable.bin'))['fclHelpTable_NOFFICE_M.ftd']
        self.assertEqual(inspect(b,'fclHelpTable_NOFFICE_M.ftd')[0]['original'],'治療')
        bad=bytearray(b);bad[-1]^=1
        with self.assertRaises(ValueError):inspect(bad,'fclHelpTable_NOFFICE_M.ftd')
    def test_infirmary_exit_names(self):
        d=json.loads((R/'translation/compiled/export_base/facility/noffice.bf.json').read_text(encoding='utf-8'))
        rows=[t for t in d['texts'] if t['id'].startswith('NOFFICE_OUT_')]
        self.assertEqual(len(rows),3)
        self.assertEqual([t['speaker'] for t in rows],['玛格丽特','伊丽莎白','伊丽莎白'])
if __name__=='__main__':unittest.main()
