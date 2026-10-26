import unittest
from compile_translation import ROOT,read
from localize_ctpk_464 import layout
from patch_menu_blocks_461 import block_offset
from reuse_menu_image_460 import sha

class Images464Tests(unittest.TestCase):
    def test_three_resources_and_preserved_bytes(self):
        d=read(ROOT/'translation/images_464.generated.json')
        self.assertEqual({f['source'] for f in d['files']},{'title/fiction.ctpk','tutorial/t043.ctpk','tutorial/t044.ctpk'})
        for f in d['files']:
            old=ROOT/'data'/f['source'];new=ROOT/f['output']
            self.assertEqual(sha(old),f['source_sha256']);self.assertEqual(sha(new),f['sha256'])
            a=old.read_bytes();b=new.read_bytes();start,w,h,bs=layout(a)
            self.assertEqual(layout(b),(start,w,h,bs));self.assertEqual(len(a),len(b))
            allowed=set()
            for x,y in f['blocks']:
                pos=start+block_offset(x,y,w)*bs//16;allowed.update(range(pos,pos+bs))
            self.assertTrue(all(x==y or i in allowed for i,(x,y) in enumerate(zip(a,b))))
        self.assertFalse(d['packaged']);self.assertFalse(d['runtime_tested'])

    def test_both_compression_formats(self):
        self.assertEqual(layout((ROOT/'data/title/fiction.ctpk').read_bytes())[-1],8)
        self.assertEqual(layout((ROOT/'data/tutorial/t043.ctpk').read_bytes())[-1],16)

if __name__=='__main__':unittest.main()
