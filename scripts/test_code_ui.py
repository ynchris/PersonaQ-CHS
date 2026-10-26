import hashlib,re,unittest
from compile_translation import ROOT,read
from raw_text_codec import decode_display
class CodeUiTests(unittest.TestCase):
    def test_both_versions_preserve_every_nonstring_byte(self):
        review=read(ROOT/'translation/code_ui_450.review.json');report=read(ROOT/'translation/code_ui_build.generated.json');mapping=read(ROOT/'translation/font_encoding.hex.json')
        sha=lambda b:hashlib.sha256(b).hexdigest()
        self.assertEqual(report['encoding_sha256'],sha((ROOT/'translation/font_encoding.hex.json').read_bytes()))
        self.assertEqual(report['review_sha256'],sha((ROOT/'translation/code_ui_450.review.json').read_bytes()))
        self.assertEqual([len(f['rows']) for f in review['files']],[153,162])
        for f,built in zip(review['files'],report['files']):
            original=(ROOT/f['source']).read_bytes();out=(ROOT/built['output']).read_bytes();allowed=set()
            self.assertEqual(sha(original),f['sha256']);self.assertEqual(sha(out),built['sha256']);self.assertEqual(len(original),len(out))
            for r in f['rows']:
                pos=r['offset'];end=pos+r['capacity_bytes'];allowed.update(range(pos,end))
                self.assertEqual(out[end],0)
                self.assertEqual(decode_display(out[pos:end].rstrip(b'\0'),mapping),r['translation'])
                self.assertEqual(re.findall(r'%[sd]',r['original']),re.findall(r'%[sd]',r['translation']))
            self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,out))))
if __name__=='__main__':unittest.main()
