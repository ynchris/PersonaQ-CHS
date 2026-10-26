import hashlib,unittest
from compile_translation import ROOT,read,TOKEN,LEADING,TRAILING
from raw_text_codec import encode_display,decode_display

class QuestCancelTests(unittest.TestCase):
    def test_batch_and_title_provenance(self):
        batch=read(ROOT/'translation/batches/411_quest_cancel_deadline.generated.json');mapping=read(ROOT/'translation/font_encoding.hex.json')
        tables={r['key']:r for r in read(ROOT/'translation/tables.catalog.working.json')}
        catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')}
        self.assertEqual(len(batch['title_reuse_audit']),47)
        for ref in batch['title_reuse_audit']:
            table=tables[ref['reference_table_key']]
            self.assertEqual(table['original'],ref['original_title']);self.assertEqual(table['translation'],ref['translated_title'])
            self.assertIn('“'+table['translation']+'”',catalog[ref['target']]['translation'])
        self.assertEqual(sum(map(len,batch['sources'].values())),65)
        for source,rows in batch['sources'].items():
            old=read(ROOT/source);new=read(ROOT/'translation/compiled'/source)
            self.assertEqual(hashlib.sha256((ROOT/source).read_bytes()).hexdigest(),batch['source_hashes'][source])
            changed={(i,j) for i,j,mid,body in rows}
            for i,j,mid,body in rows:
                original=old['texts'][i]['lines'][j];full=LEADING.match(original).group()+body+TRAILING.search(original).group()
                self.assertEqual(mid,old['texts'][i]['id']);self.assertEqual(new['texts'][i]['lines'][j],full)
                self.assertEqual(TOKEN.findall(original),TOKEN.findall(full))
                plain=TOKEN.sub('',body)
                self.assertLessEqual(max(map(len,plain.splitlines())),max(map(len,TOKEN.sub('',original).splitlines())))
                self.assertEqual(decode_display(encode_display(plain,mapping),mapping),plain)
            for i,entry in enumerate(old['texts']):
                for j,value in enumerate(entry['lines']):
                    if 'テスト' in value:self.assertEqual(new['texts'][i]['lines'][j],value)

if __name__=='__main__':unittest.main()
