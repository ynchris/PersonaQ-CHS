import unittest
from compile_translation import ROOT,read
from check_roundtrip import members
from caution_tmx_463 import decode
from reuse_menu_image_460 import sha

class Caution463Tests(unittest.TestCase):
    def test_resource_and_unmodified_siblings(self):
        d=read(ROOT/'translation/caution_463.generated.json')
        source=ROOT/'data'/d['source']; output=ROOT/d['output']
        self.assertEqual(sha(source),d['source_sha256'])
        self.assertEqual(sha(output),d['sha256'])
        before=members(source);after=members(output)
        self.assertEqual([n for n,b in before],[n for n,b in after])
        for (n,a),(_,b) in zip(before,after):
            self.assertEqual(len(a),len(b))
            if n!='caution.tmx':self.assertEqual(a,b)
            else:
                self.assertEqual(a[:1088],b[:1088])
                old,_=decode(a);new,_=decode(b)
                self.assertEqual(old.size,(512,256))
                for y in range(256):
                    for x in range(512):
                        if not any(l<=x<r and t<=y<bottom for l,t,r,bottom in d['regions']):
                            self.assertEqual(old.getpixel((x,y)),new.getpixel((x,y)))

    def test_preserves_warning_meaning_and_scope(self):
        d=read(ROOT/'translation/caution_463.generated.json')
        text=''.join(d['lines'])
        for phrase in ['未经权利人许可','明知','非法','下载','法律','禁止']:
            self.assertIn(phrase,text)
        self.assertFalse(d['runtime_tested'])
        self.assertFalse(d['packaged'])

if __name__=='__main__':unittest.main()
