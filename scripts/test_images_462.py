import unittest
from compile_translation import ROOT,read
from reuse_menu_image_460 import sha
from patch_menu_blocks_461 import layout,block_offset

class Images462Tests(unittest.TestCase):
    def test_all_nonselected_bytes_unchanged(self):
        d=read(ROOT/'translation/images_462.accepted.json')
        self.assertFalse(d['packaged'])
        self.assertEqual(len(d['files']),2)
        for f in d['files']:
            original=ROOT/'data'/f['source']; final=ROOT/f['output']
            self.assertEqual(sha(original),f['source_sha256'])
            self.assertEqual(sha(final),f['sha256'])
            a=original.read_bytes(); b=final.read_bytes()
            start,w,h=layout(a)
            self.assertEqual(layout(b),(start,w,h))
            allowed=set()
            for x,y in f['blocks']:
                pos=start+block_offset(x,y,w);allowed.update(range(pos,pos+16))
            self.assertEqual(len(a),len(b))
            self.assertTrue(all(x==y or i in allowed for i,(x,y) in enumerate(zip(a,b))))
            self.assertFalse(f['runtime_tested'])

if __name__=='__main__':unittest.main()
