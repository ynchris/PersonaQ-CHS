"""Decode the small legacy TMX sheet for visual source identification."""
from decode_opening_tmx_526 import ROOT,decode
from PIL import Image
out=ROOT/'translation/inspection_530';out.mkdir(exist_ok=True)
im=decode((ROOT/'data/font/f09_001.tmx').read_bytes())
canvas=Image.new('RGBA',im.size,'#222222');canvas.alpha_composite(im)
canvas.resize((768,768),Image.Resampling.NEAREST).save(out/'f09_original.png')
p=out/'demo_font/demo_font_sheet0.png'
if p.exists():
    im=Image.open(p).convert('RGBA');canvas=Image.new('RGBA',im.size,'#222222');canvas.alpha_composite(im)
    canvas.resize((768,768),Image.Resampling.NEAREST).save(out/'demo_original.png')
