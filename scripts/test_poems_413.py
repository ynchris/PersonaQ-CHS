import hashlib,re,unicodedata,unittest
from collections import Counter
from compile_translation import ROOT,read,TOKEN,LEADING,TRAILING
from raw_text_codec import encode_display,decode_display

class PoemViewerTests(unittest.TestCase):
    def test_all_pages_controls_and_encoding(self):
        batch=read(ROOT/'translation/batches/413_poem_viewer.generated.json')
        mapping=read(ROOT/'translation/font_encoding.hex.json')
        self.assertEqual(sum(map(len,batch['sources'].values())),81)
        for s,rows in batch['sources'].items():
            old=read(ROOT/s);new=read(ROOT/'translation/compiled'/s)
            self.assertEqual(hashlib.sha256((ROOT/s).read_bytes()).hexdigest(),batch['source_hashes'][s])
            for i,j,mid,body in rows:
                original=old['texts'][i]['lines'][j]
                full=LEADING.match(original).group()+body+TRAILING.search(original).group()
                self.assertEqual(mid,old['texts'][i]['id'])
                self.assertEqual(full,new['texts'][i]['lines'][j])
                self.assertEqual(TOKEN.findall(full),TOKEN.findall(original))
                a=TOKEN.sub('',original);b=TOKEN.sub('',full)
                self.assertEqual(Counter(re.findall(r'\d+',unicodedata.normalize('NFKC',a))),Counter(re.findall(r'\d+',unicodedata.normalize('NFKC',b))))
                self.assertLessEqual(len(b.splitlines()),len(a.splitlines()))
                self.assertLessEqual(max(map(len,b.splitlines())),max(map(len,a.splitlines())))
                self.assertEqual(decode_display(encode_display(b,mapping),mapping),b)
                self.assertFalse(re.search(r'[\u3041-\u3096\u30a1-\u30fa]',b))

    def test_complete_scope_and_retained_blanks(self):
        catalog=read(ROOT/'translation/catalog.working.json')
        camp=[r for r in catalog if r['source']=='export_base/camp/cmppoem.bf.json' and not r.get('translation')]
        poem=[r for r in catalog if r['source']=='export_base/event/msg_POEM.bmd.json' and not r.get('translation')]
        self.assertEqual(len(camp),12);self.assertEqual(len(poem),5)
        for r in camp:self.assertEqual(TOKEN.sub('',r['original']),'？？？？')
        for r in poem:self.assertFalse(TOKEN.sub('',r['original']).strip())
        for r in camp+poem:
            doc=read(ROOT/'translation/compiled'/r['source'])
            self.assertEqual(doc['texts'][r['message_index']]['lines'][r['line_index']],r['original'])
        doc=read(ROOT/'translation/compiled/export_base/event/msg_POEM.bmd.json')
        self.assertIn('真实……',TOKEN.sub('',doc['texts'][18]['lines'][0]))
        self.assertIn('通往你的车票',TOKEN.sub('',doc['texts'][30]['lines'][1]).replace('\n',''))

if __name__=='__main__':unittest.main()
