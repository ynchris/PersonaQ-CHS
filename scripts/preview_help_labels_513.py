"""Two PNG-only help atlases. Preserve icons and all pixels outside text boxes."""
import json
from PIL import Image, ImageDraw, ImageFont, ImageChops
from preview_tutorials_468 import ROOT, digest

out = ROOT / 'translation/previews_513'
out.mkdir(exist_ok=True)
assets = [
    ('battle/panel/info.ctpk.00.png', [((111,107,148,124), '返回', 10), ((162,85,234,103), '切换地图显示', 10)], (94,76,236,126)),
    ('camp/c_sub.spr3.00.png', [((174,349,226,370), '菜单', 12)], (155,346,230,373)),
]
reviews = []
for rel, edits, crop in assets:
    src = ROOT / 'export_base' / rel
    original = Image.open(src).convert('RGBA')
    im = original.copy()
    for box, text, size in edits:
        l,t,r,b = box
        patch = Image.new('RGBA', ((r-l)*4,(b-t)*4))
        d = ImageDraw.Draw(patch)
        font = ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc', size*4)
        bb = d.textbbox((0,0), text, font=font)
        assert bb[2]-bb[0] <= patch.width
        d.text((8-bb[0], (patch.height-bb[3]+bb[1])/2-bb[1]), text, font=font, fill='#333333', stroke_width=6, stroke_fill='white')
        rendered = patch.resize((r-l,b-t),Image.Resampling.LANCZOS)
        if text == '返回':
            # The original has a white button plate, not just a glyph outline.
            # Preserve its exact alpha silhouette, replacing only the dark text.
            plate = Image.new('RGBA', (r-l,b-t), 'white')
            plate.putalpha(original.crop(box).getchannel('A'))
            plate.alpha_composite(rendered)
            rendered = plate
        im.paste(rendered,(l,t))
    check = im.copy()
    for box,*_ in edits:
        check.paste(original.crop(box),box[:2])
    assert not any(c.getbbox() for c in ImageChops.difference(check,original).split())
    target = out / src.name
    im.save(target)
    full = Image.new('RGBA',(original.width*2+8,original.height),'#dddddd')
    full.alpha_composite(original,(0,0))
    full.alpha_composite(im,(original.width+8,0))
    full.save(out / (src.stem+'.full.png'))
    w,h = crop[2]-crop[0],crop[3]-crop[1]
    detail = Image.new('RGBA',(w*2+8,h),'#dddddd')
    detail.alpha_composite(original.crop(crop),(0,0))
    detail.alpha_composite(im.crop(crop),(w+8,0))
    detail.resize((detail.width*3,h*3),Image.Resampling.NEAREST).save(out / (src.stem+'.detail.png'))
    reviews.append(dict(source=src.relative_to(ROOT).as_posix(),png=target.relative_to(ROOT).as_posix(),sha256=digest(target),edits=edits,outside_boxes_rgba_unchanged=True))
(out/'review.json').write_text(json.dumps(dict(status='pending_user_visual_review',assets=reviews,encoded=False,packaged=False),ensure_ascii=False,indent=2),encoding='utf-8')
