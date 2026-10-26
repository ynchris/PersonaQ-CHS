"""Decode PQ1's previously unexported 8-bit TMX startup notice."""
import struct
from PIL import Image
from check_roundtrip import members
from compile_translation import ROOT

def decode(raw):
    assert raw[8:12]==b'TMX0' and raw[16:18]==b'\x01\x00'
    assert raw[22:26]==b'\x13\x00\x00\x00'
    width,height=struct.unpack_from('<HH',raw,18)
    assert len(raw)==1088+width*height==struct.unpack_from('<I',raw,4)[0]
    order=[base+j for base in range(0,256,32) for block in [0,16,8,24] for j in range(block,block+8)]
    palette=[tuple(raw[64+i*4:68+i*4]) for i in order]
    rgba=[(r,g,b,min(a*2,255)) for r,g,b,a in palette]
    image=Image.new('RGBA',(width,height));image.putdata([rgba[i] for i in raw[1088:]])
    return image,rgba

if __name__=='__main__':
    raw=dict(members(ROOT/'data/title/logo.bin'))['caution.tmx']
    image,palette=decode(raw)
    image.save(ROOT/'translation/caution_463_original.png')
    print('Decoded caution:',image.size)
