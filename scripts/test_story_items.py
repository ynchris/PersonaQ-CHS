import hashlib
import re
import unittest
from compile_translation import ROOT,read,TOKEN,LEADING,TRAILING
from raw_text_codec import encode_display,decode_display
from prepare_story_items_385 import SOURCE

class StoryItemTests(unittest.TestCase):
    def test_batch_and_encoding(self):
        batch=read(ROOT/'translation/batches/385_story_key_items.generated.json')
        mapping=read(ROOT/'translation/font_encoding.hex.json')
        self.assertEqual(sum(map(len,batch['sources'].values())),37)
        for source,rows in batch['sources'].items():
            old=read(ROOT/source);new=read(ROOT/'translation/compiled'/source)
            self.assertEqual(hashlib.sha256((ROOT/source).read_bytes()).hexdigest(),batch['source_hashes'][source])
            for i,j,mid,body in rows:
                original=old['texts'][i]['lines'][j]
                full=LEADING.match(original).group()+body+TRAILING.search(original).group()
                self.assertEqual(mid,old['texts'][i]['id'])
                self.assertEqual(new['texts'][i]['lines'][j],full)
                self.assertEqual(TOKEN.findall(full),TOKEN.findall(original))
                self.assertEqual(decode_display(encode_display(TOKEN.sub('',full),mapping),mapping),TOKEN.sub('',full))
                self.assertLessEqual(max(map(len,TOKEN.sub('',full).splitlines())),max(map(len,TOKEN.sub('',original).splitlines())))

    def test_key_item_completion_and_reuse(self):
        audit=read(ROOT/'translation/385_story_key_items.audit.generated.json')
        catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')}
        self.assertEqual(len(audit['key_item_indices']),36)
        for row in catalog.values():
            if row['source']==SOURCE and not row.get('translation'):
                self.assertIsNotNone(re.search(r'ID_|ブランク|貴重品枠最後',TOKEN.sub('',row['original'])))
        for entry in audit['local_reuse']:
            self.assertEqual(entry['translation'],TRAILING.sub('',LEADING.sub('',catalog[entry['catalog_key']]['translation'])))
        for i,rate,discount in [(20,'２５','１０'),(21,'５０','１５'),(22,'７５','２０'),(23,'１００','２５')]:
            text=catalog[f'{SOURCE}:{i}:0']['translation']
            self.assertIn(rate+'％',text)
            self.assertIn('减免'+discount+'％',text)

if __name__=='__main__':unittest.main()
