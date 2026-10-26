"""Read-only source inspection on dark backgrounds. No edited game assets."""
from PIL import Image
from preview_tutorials_468 import ROOT
out=ROOT/'translation/previews_517';out.mkdir(exist_ok=True)
sources=['camp/panel_font.ctpk.00.png','battle/panel/panel_font.ctpk.00.png','camp/new_data1.spr3.00.png','font/window.spr3.00.png','font/info_base.spr3.00.png','facility/velvet.spr3.00.png','memcard/save_load.spr3.00.png','title/dlc.spr3.00.png','battle/panel/btl.spr3.00.png']
sources += ['facility/shop.spr3.00.png','facility/party.spr3.00.png','facility/noffice.spr3.00.png']
for rel in sources:
    src=Image.open(ROOT/'export_base'/rel).convert('RGBA')
    bg=Image.new('RGBA',src.size,'#202020');bg.alpha_composite(src)
    if src.height<100: bg=bg.resize((src.width*3,src.height*3),Image.Resampling.NEAREST)
    bg.save(out/(rel.replace('/','__')))
print('Inspection copies:',len(sources))
