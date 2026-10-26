"""Validate approved PNG selections only. Never encode or package game files."""
import json
from pathlib import Path
from PIL import Image
from preview_tutorials_468 import ROOT, digest

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

inventory_path=ROOT/'translation/previews_511/map_tutorial_inventory.json'
inventory=read(inventory_path)
assert inventory['total']==22
for row in inventory['rows']:
    assert digest(ROOT/row['png'])==row['sha256'],row['png']
    row['status']='user_approved'
inventory['approved']=22
inventory['pending']=0
inventory_path.write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf-8')

selection=[
 (518,'memcard/save_load.spr3.00.png'),
 (519,'facility/velvet.spr3.00.png'),
 (522,'facility/party.spr3.00.png'),
 (521,'title/dlc.spr3.00.png'),
 (493,'event/skip_btn.spr3.00.png'),
 (498,'facility/shop.spr3.00.png'),
 (500,'facility/noffice.spr3.00.png'),
 (516,'camp/c_main.spr3.00.png'),
 (503,'mapdat/tex/map_tutorial.spr3.00.png'),
 (507,'mapdat/tex/map_plt_icon.ctpk.00.png'),
 (512,'battle/panel/btl.spr3.00.png'),
 (513,'battle/panel/info.ctpk.00.png'),
 (513,'camp/c_sub.spr3.00.png'),
 (514,'battle/result/persona_get.bin_card.spr3.00.png'),
 (514,'facility/root_image.spr3.00.png'),
]
rows=[]
for batch,source in selection:
    p=ROOT/f'translation/previews_{batch}'/Path(source).name
    rows.append(dict(source='export_base/'+source,png=p.relative_to(ROOT).as_posix(),sha256=digest(p)))
for row in inventory['rows']:
    rows.append(dict(source='export_base/'+row['source']+'.00.png',png=row['png'],sha256=row['sha256']))

keyboard=read(ROOT/'translation/previews_525/review.json')
assert keyboard['status']=='approved_by_user'
assert digest(ROOT/keyboard['png'])==keyboard['sha256']
for item in keyboard['related_textures']:
    assert item['identical_pixels']
    with Image.open(ROOT/item['source']) as a, Image.open(ROOT/keyboard['source']) as b:
        assert a.convert('RGBA').tobytes()==b.convert('RGBA').tobytes()
    rows.append(dict(source=item['source'],png=keyboard['png'],sha256=keyboard['sha256']))

assert len({r['source'] for r in rows})==len(rows),'Conflicting target selection'
def hashes(obj):
    if isinstance(obj,dict):
        if 'sha256' in obj: yield obj['sha256']
        for v in obj.values(): yield from hashes(v)
    elif isinstance(obj,list):
        for v in obj: yield from hashes(v)

for row in rows:
    p=ROOT/row['png']; original=ROOT/row['source']
    with Image.open(p) as image, Image.open(original) as src:
        assert image.size==src.size,(p,image.size,src.size)
        assert image.mode=='RGBA',(p,image.mode)
        row['size']=list(image.size)
    evidence=list(p.parent.glob('*.json'))
    assert any(row['sha256'] in set(hashes(read(f))) for f in evidence),f'No matching recorded hash: {p}'
    row['original_sha256']=digest(original)
    row['approved_hash_verified']=True
    row['older_candidates']=[q.relative_to(ROOT).as_posix() for q in (ROOT/'translation').glob('previews_*/'+p.name) if q!=p]

result=dict(scope='Latest approved menu atlases, 22 map tutorials and four identical keyboard textures with five translated labels; excludes separate tutorial/tNNN series, executable patches, opening TMX, pinyin functionality and movies.',count=len(rows),map_tutorials=22,menus=len(selection),keyboard_targets=len(keyboard['related_textures']),status='preflight_passed',encoded=False,packaged=False,files=rows)
target=ROOT/'translation/image_selection_515.json'
target.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='files'},ensure_ascii=False))
