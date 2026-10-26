"""Freeze current post-540 image selections, no encoding or ROM mutation."""
import hashlib,struct
from PIL import Image
from compile_translation import ROOT,read,write
from localize_ctpk_464 import layout
out=ROOT/'translation/preflight_562';out.mkdir(exist_ok=True)
inventory={r['unit']:r for r in read(ROOT/'translation/feedback_543/secondary_textures.json')}
specs=[('00.ctpk','translation/previews_552/camp_texture_1.png',552),
       ('14.ctpk','translation/previews_554/shop_texture_1.png',554),
       ('17.ctpk','translation/previews_556/velvet_texture_2.png',556),
       ('05.ctpk','translation/previews_558/05.ctpk.00.png',558),
       ('10.ctpk','translation/previews_558/10.ctpk.00.png',558),
       ('13.ctpk','translation/previews_560/pink.ctpk.00.png',560)]
rows=[]
def hashes(o):
    if isinstance(o,dict):
        for k,v in o.items():
            if k.endswith('sha256'):yield v
            else:yield from hashes(v)
    elif isinstance(o,list):
        for v in o:yield from hashes(v)
for unit,png,rev in specs:
    src=inventory[unit];container=src['source'];offset=src['offset']
    raw=(ROOT/'data'/container).read_bytes();ctpk=raw[offset:offset+src['bytes']]
    assert ctpk[:4]==b'CTPK';start,w,h,bs=layout(ctpk)
    image=Image.open(ROOT/png).convert('RGBA')
    original_path=f'translation/feedback_543/secondary_decoded/{unit}.00.png'
    original=Image.open(ROOT/original_path).convert('RGBA');assert image.size==original.size==(w,h)
    digest=hashlib.sha256((ROOT/png).read_bytes()).hexdigest()
    assert digest in set(hashes(read(ROOT/f'translation/previews_{rev}/review.json')))
    changed=sum(a!=b for a,b in zip(original.getdata(),image.getdata()))
    assert changed>0
    rows.append(dict(container=container,texture_index=src['texture_index'],texture_offset=offset,texture_bytes=src['bytes'],source=original_path,png=png,sha256=digest,size=[w,h],changed_pixels=changed))
raw=(ROOT/'data/camp/c_main.spr3').read_bytes();off=struct.unpack_from('<I',raw,36)[0]
section,size=struct.unpack_from('<II',raw,off+8)
png='translation/previews_548/camp_texture_0.png';digest=hashlib.sha256((ROOT/png).read_bytes()).hexdigest()
assert digest==read(ROOT/'translation/previews_548/review.json')['first_texture_sha256']
rows.insert(0,dict(container='camp/c_main.spr3',texture_index=0,texture_offset=off,texture_bytes=section+size,source='export_base/camp/c_main.spr3.00.png',png=png,sha256=digest,size=[512,512]))
assert len({(r['container'],r['texture_offset']) for r in rows})==7
# Explicitly guard against the withdrawn decorative logo and black-orb mistake.
a=Image.open(ROOT/'translation/feedback_543/secondary_decoded/14.ctpk.00.png').convert('RGBA')
b=Image.open(ROOT/'translation/previews_554/shop_texture_1.png').convert('RGBA')
assert a.crop((1,1,170,149)).tobytes()==b.crop((1,1,170,149)).tobytes()
a=Image.open(ROOT/'translation/feedback_543/secondary_decoded/00.ctpk.00.png').convert('RGBA')
b=Image.open(ROOT/'translation/previews_552/camp_texture_1.png').convert('RGBA')
assert a.crop((299,39,319,59)).tobytes()==b.crop((299,39,319,59)).tobytes()
assert not any('553' in r['png'] or '559' in r['png'] or '557' in r['png'] for r in rows)
write(out/'image_selection.json',dict(status='preflight_passed',scope='Seven changed textures after TEST_540; first atlas override plus six additional atlases. Not a complete game image inventory.',files=rows,original_shop_logo_preserved=True,black_orb_preserved=True,encoded=False,packaged=False))
print('PASS: 7 texture selections, 4 containers, original decorative logo and black orb preserved.')
