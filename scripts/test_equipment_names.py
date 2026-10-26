import hashlib
import json
import re
import unittest
from equipment_names import ROOT,parse,load_drafts,build

class EquipmentNamesTests(unittest.TestCase):
    def test_full_scope_and_fixed_names(self):
        data,start,names,rows=load_drafts()
        self.assertEqual(len(rows),696)
        self.assertEqual(start,346144)
        self.assertEqual(names[1],'ゴルフクラブ')
        self.assertEqual(names[769],'ゴシックシャツ')
        self.assertEqual(names[1025],'元気の根付')
        self.assertEqual(rows[882],'壹式埃癸斯装甲')
        excluded={60,61,62,63,172,173,174,175,316,317,318,319,580,767,768,1023,1024,1279,*range(1262,1279)}
        actual={i for i,s in enumerate(names[:1280]) if not re.fullmatch(r'0x[0-9A-Fa-f]+',s)}
        self.assertEqual(actual-set(rows),excluded)
        self.assertTrue(set(rows).isdisjoint(excluded))

    def test_byte_preservation_and_readback(self):
        from raw_text_codec import decode_display
        data,start,names,rows=load_drafts()
        mapping=json.loads((ROOT/'translation/font_encoding.hex.json').read_text(encoding='utf-8'))
        result=build(data,start,rows,mapping)
        self.assertEqual(data[:start],result[:start])
        self.assertEqual(len(data),len(result))
        for i in range(len(names)):
            old=data[start+i*22:start+(i+1)*22]
            new=result[start+i*22:start+(i+1)*22]
            if i in rows:
                self.assertEqual(decode_display(new.rstrip(b'\0'),mapping),rows[i])
            else:
                self.assertEqual(old,new)

    def test_reject_overflow_and_bad_bank(self):
        data,start,names,rows=load_drafts()
        with self.assertRaises(ValueError):
            build(data,start,{1:'a'*22},{})
        with self.assertRaises(ValueError):
            parse(data[:-1])
        broken=bytearray(data)
        broken[16+3328*104]=0
        broken[16+3328*104+1]=0
        with self.assertRaises(ValueError):
            parse(bytes(broken))

if __name__=='__main__':
    unittest.main()
