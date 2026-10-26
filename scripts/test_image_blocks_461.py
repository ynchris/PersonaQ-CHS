import unittest
from patch_menu_blocks_461 import block_offset,layout
from compile_translation import ROOT,read

class Block461Tests(unittest.TestCase):
    def test_block_mapping_is_bijective(self):
        offsets={block_offset(x,y,512) for y in range(0,512,4) for x in range(0,512,4)}
        self.assertEqual(offsets,set(range(0,512*512,16)))

    def test_original_format_supported(self):
        raw=(ROOT/'data/camp/c_sub.spr3').read_bytes()
        start,w,h=layout(raw)
        self.assertEqual((w,h),(512,512))
        self.assertEqual(start+w*h,len(raw))

    def test_report_does_not_claim_runtime_or_visual_acceptance(self):
        d=read(ROOT/'translation/image_blocks_461.generated.json')
        self.assertEqual(len(d['blocks']),54)
        self.assertTrue(d['preserved_all_other_bytes'])
        self.assertTrue(d['preserved_pixels_outside_blocks'])
        self.assertTrue(d['visual_review_pending'])
        self.assertFalse(d['packaged'])
        self.assertFalse(d['runtime_tested'])

if __name__=='__main__':unittest.main()
