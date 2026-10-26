"""Six screenshot tutorial PNGs; no binary imports or packaging."""
import json
import preview_tutorials_468 as rendering
from PIL import Image, ImageChops, ImageDraw
from preview_tutorials_468 import ROOT, label, digest

OUT=ROOT/'translation/previews_472'

def main():
    OUT.mkdir(exist_ok=True)
    bank=json.loads((ROOT/'translation/q2_name_banks.review.generated.json').read_text(encoding='utf-8'))
    group=next(g for g in bank['groups'] if g['source']=='battle/table/enemynametable.tbl')
    name=next(r['translation'] for r in group['rows'] if r['original']=='臆病のマーヤ')
    assert name=='懦弱之魔影'
    records=[]
    for n in (7,8,32,33,23,24):
        src=ROOT/f'export_base/tutorial/t{n:03}.ctpk.00.png'
        original=Image.open(src).convert('RGBA')
        im=original.copy()
        if n in (7,8,32,33):
            box=(113,11,181,24)
            text=name
            bg=original.getpixel((100,17))
            rendering.FONT='C:/Windows/Fonts/msyhbd.ttc'
            label(im,box,text,'white',bg,size=9,align='center')
        else:
            box=(23,118,169,129)
            text='召唤和登录副人格面具'
            bg=original.getpixel((175,124))
            rendering.FONT='C:/Windows/Fonts/msyh.ttc'
            label(im,box,text,(151,151,151,255),bg,size=9)
        # Hard boundary test: no change to screenshot characters, stats, icons or circles.
        restored=im.copy()
        restored.paste(original.crop(box),box[:2])
        for mode in ('RGB','RGBA'):
            assert ImageChops.difference(restored,original).convert(mode).getbbox() is None
        target=OUT/f't{n:03}.ctpk.00.png'
        im.save(target)
        pair=Image.new('RGBA',(592,184),'black')
        pair.paste(original.crop((0,0,296,184)),(0,0))
        pair.paste(im.crop((0,0,296,184)),(296,0))
        pair.resize((1184,368),Image.Resampling.NEAREST).save(OUT/f't{n:03}_compare.png')
        records.append(dict(png=target.relative_to(ROOT).as_posix(),sha256=digest(target),source=src.relative_to(ROOT).as_posix(),edit_box=box,text=text,status='pending_user_review',outside_box_unchanged=True))
    (OUT/'review.json').write_text(json.dumps(dict(images=records,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
    # Compact overview of the four separately preserved battle screenshots.
    sheet=Image.new('RGBA',(1184,368*4),'black')
    for i,n in enumerate((7,8,32,33)):
        sheet.paste(Image.open(OUT/f't{n:03}_compare.png'),(0,368*i))
    sheet.save(OUT/'battle_comparisons.png')
    print('Six PNG previews created. No binary writes.')

if __name__=='__main__':
    main()
