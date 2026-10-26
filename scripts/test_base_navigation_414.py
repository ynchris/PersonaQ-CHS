import hashlib,re,unittest,unicodedata
from collections import Counter
from compile_translation import ROOT,read,TOKEN,LEADING,TRAILING
from raw_text_codec import encode_display,decode_display

class BaseNavigationTests(unittest.TestCase):
    batch_name='414_base_navigation.generated.json'
    page_count=138
    reuse_count=47
    scope_prefix='export_base/battle/support/bsv105.'
    def test_batch_and_reuse(self):
        batch=read(ROOT/'translation/batches'/self.batch_name)
        mapping=read(ROOT/'translation/font_encoding.hex.json')
        catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')}
        self.assertEqual(sum(map(len,batch['sources'].values())),self.page_count)
        self.assertEqual(len(batch['reuse_audit']),self.reuse_count)
        for a in batch['reuse_audit']:
            target=catalog[a['target_key']];ref=catalog[a['reference_key']]
            self.assertEqual(target['original'],ref['original'])
            self.assertEqual(target['translation'],ref['translation'])
            self.assertEqual(a['original'],ref['original'])
            self.assertEqual(a['translation'],ref['translation'])
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
                nums=lambda t:Counter(re.findall(r'\d+',unicodedata.normalize('NFKC',t)))
                self.assertEqual(nums(a),nums(b))
                self.assertLessEqual(len(b.splitlines()),len(a.splitlines()))
                self.assertLessEqual(max(map(len,b.splitlines())),max(map(len,a.splitlines())))
                self.assertEqual(decode_display(encode_display(b,mapping),mapping),b)

    def test_encounter_scope_complete(self):
        catalog=read(ROOT/'translation/catalog.working.json')
        scope=[r for r in catalog if r['source'].startswith(self.scope_prefix) and int(re.search(r'_\((\d+)\)',r['source'])[1])<=53]
        self.assertEqual(len(scope),94)
        self.assertTrue(all(r.get('translation') for r in scope))

if __name__=='__main__':unittest.main()
