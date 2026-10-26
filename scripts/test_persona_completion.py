import hashlib
import struct
import unittest
from compile_translation import ROOT, read
from persona_names import load_drafts, parse, build, DRAFT, is_placeholder
from raw_text_codec import decode_display


class PersonaCompletionTests(unittest.TestCase):
    def test_party_prompts_379(self):
        from prepare_party_persona_379 import normalize, decode_tags
        from compile_translation import TOKEN, LEADING, TRAILING
        batch=read(ROOT/'translation/batches/379_party_persona_prompts.generated.json')
        self.assertEqual(sum(map(len,batch['sources'].values())),34)
        for source, rows in batch['sources'].items():
            self.assertEqual(hashlib.sha256((ROOT/source).read_bytes()).hexdigest(),batch['source_hashes'][source])
            doc,new=read(ROOT/source),read(ROOT/'translation/compiled'/source)
            for mi,li,mid,body in rows:
                original=doc['texts'][mi]['lines'][li]
                self.assertEqual(mid,doc['texts'][mi]['id'])
                full=LEADING.match(original).group()+body+TRAILING.search(original).group()
                self.assertEqual(full,new['texts'][mi]['lines'][li])
                self.assertEqual(TOKEN.findall(original),TOKEN.findall(full))
                self.assertLessEqual(max(map(len,TOKEN.sub('',full).splitlines())),max(map(len,TOKEN.sub('',original).splitlines())))
        audit=read(ROOT/'translation/379_party_persona_prompts.audit.generated.json')
        reference=ROOT.parent/audit['reference']
        self.assertEqual(hashlib.sha256(reference.read_bytes()).hexdigest(),audit['reference_sha256'])
        refs=read(reference)
        self.assertEqual(len(audit['entries']),6)
        source='export_base/facility/msg_combine_lvup.bmd.json'
        rows={(i,j):b for i,j,_,b in batch['sources'][source]}
        for entry in audit['entries']:
            ref=next(r for r in refs if r['key']==entry['reference_key'])
            self.assertEqual(ref['original'],entry['reference_original'])
            self.assertEqual(ref['translation'],entry['reference_translation'])
            mi,li=entry['message_index'],entry['line_index']
            self.assertEqual(normalize(decode_tags(ref['original'])),normalize(read(ROOT/source)['texts'][mi]['lines'][li]))
            self.assertEqual(rows[mi,li],entry['final_body'])
        self.assertIn('要发生',rows[9,1])
        source='export_base/facility/party_edit.bmd.json'
        self.assertEqual({r[0] for r in batch['sources'][source]},set(range(29))-{4})
        self.assertEqual(read(ROOT/source)['texts'][4],read(ROOT/'translation/compiled'/source)['texts'][4])

    def test_complete_informative_compendium(self):
        rows=[r for r in read(ROOT/'translation/catalog.working.json') if r['source']=='export_base/facility/datmyth.bmd.json']
        self.assertEqual(len(rows),251)
        for r in rows:
            if 'ＲＥＳＥＲＶＥ\n神話' not in r['original']:
                self.assertTrue(r.get('translation'),r['key'])
            else:
                self.assertFalse(r.get('translation'),r['key'])

    def test_names_and_provenance(self):
        _,names,rows=load_drafts()
        self.assertEqual(len(rows),272)
        draft=read(DRAFT)
        reference=ROOT.parent/draft['reference']
        self.assertEqual(hashlib.sha256(reference.read_bytes()).hexdigest(),draft['reference_sha256'])
        refs=read(reference)
        self.assertEqual(sum(bool(r['references']) for r in draft['entries']),267)
        for r in draft['entries']:
            for ref in r['references']:
                self.assertTrue(any(x['key']==ref['key'] and x['original']==r['original'] and x['translation']==ref['translation'] for x in refs))
        self.assertEqual(rows[241],'伊邪那岐大神')
        self.assertEqual(rows[68],'八束水臣津野命')
        self.assertEqual(rows[211],'俄耳甫斯·改')
        self.assertEqual(rows[276],names[276])
        self.assertTrue(all(is_placeholder(n) for i,n in enumerate(names) if i not in rows))

    def test_binary_roundtrip_and_preservation(self):
        data,names,rows=load_drafts()
        mapping=read(ROOT/'translation/font_encoding.hex.json')
        result=build(data,rows,mapping)
        self.assertEqual(result[:2],data[:2])
        old,new=parse(data),parse(result)
        for i,chunk in enumerate(new):
            if i in rows:
                self.assertEqual(decode_display(chunk[:-1],mapping),rows[i])
            else:
                self.assertEqual(chunk,old[i])
        self.assertEqual(build(data,{},mapping),data)
        self.assertEqual(result,(ROOT/'full_work/persona_payload/battle/table/personanametable.tbl').read_bytes())

    def test_reject_corrupt_or_overflow(self):
        data,_,_=load_drafts()
        for broken in [b'',data[:-1],data+b'\0',data[:2]+b'\0\0'+data[4:]]:
            with self.assertRaises(ValueError):
                parse(broken)
        with self.assertRaises(ValueError):
            build(data,{2:'a'*65536},{})
        with self.assertRaises(ValueError):
            build(data,{288:'a'},{})


if __name__=='__main__':
    unittest.main()
