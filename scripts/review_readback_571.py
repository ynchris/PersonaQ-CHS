"""Render review comparisons on gray without modifying encoded assets."""
import json
from pathlib import Path
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'translation/build_569/readback_review';OUT.mkdir(exist_ok=True)
report=json.loads((ROOT/'translation/build_569/images.json').read_text(encoding='utf-8'))
for i,row in enumerate(report['textures']):
    a=Image.open(ROOT/row['png']).convert('RGBA');b=Image.open(ROOT/row['readback']).convert('RGBA')
    w,h=a.size;pair=Image.new('RGBA',(w*2+16,h),'#444444')
    pair.alpha_composite(a);pair.alpha_composite(b,(w+16,0))
    pair.convert('RGB').save(OUT/f'{i:02}.png')
print('Seven before-encoding/readback comparison PNGs ready.')
