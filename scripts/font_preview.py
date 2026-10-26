"""Render magnified actual generated glyph cells (not an emulator screenshot)."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'tools/pq_python_deps'))
from PIL import Image,ImageDraw

chars='剧变开戏择时标确请适选难题游无'
mapped='劇変開戯択時標確請適選難題遊無'
names=['anito_13_13','anito_16_16','humming_d_12','humming_d_14','seurapro_12_12','seurapro_13_13']
canvas=Image.new('RGB',(1100,550),'#202020')
draw=ImageDraw.Draw(canvas)
for row,name in enumerate(names):
    folder=ROOT/'sample_work/fonts'/name
    manifest=json.loads((folder/f'{name}_manifest.json').read_text(encoding='utf-8'))
    texture=manifest['textureInfo']; cols=texture['sheetInfo']['cols']; rows=texture['sheetInfo']['rows']
    cw=texture['glyph']['width']+1; ch=texture['glyph']['height']+1
    draw.text((8,row*90+5),name,fill='white')
    for i,char in enumerate(mapped):
        key=chr(int.from_bytes(char.encode('cp932'),'big'))
        index=manifest['glyphMap'][key]
        sheet=Image.open(folder/f'{name}_sheet{index//(cols*rows)}.png').convert('RGBA')
        slot=index%(cols*rows); x=slot%cols*cw+1; y=slot//cols*ch+2
        glyph=sheet.crop((x,y,x+cw,y+ch))
        glyph=glyph.resize((cw*4,ch*4),Image.Resampling.NEAREST)
        canvas.paste(glyph,(185+i*69,row*90+12),glyph)
canvas.save(ROOT/'font_preview.png')
