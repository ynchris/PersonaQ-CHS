"""Review unresolved camp labels using latest texture, not obsolete previews."""
import hashlib
from PIL import Image
from compile_translation import ROOT,read,write
out=ROOT/'translation/previews_561';out.mkdir(exist_ok=True)
source=ROOT/'translation/previews_552/camp_texture_1.png'
current=Image.open(source).convert('RGBA')
original=Image.open(ROOT/'translation/feedback_543/secondary_decoded/00.ctpk.00.png').convert('RGBA')
edits=next(a for a in read(ROOT/'translation/previews_546/review.json')['assets'] if a['unit']=='camp')['edits']
# Main/sub and detailed/back have separate reviewed revisions; do not revive them.
edits=[e for e in edits if e[1] not in ('主','副','详细')]
for name,group in [('controls',edits[:5]),('status',edits[5:9]),('stats',edits[9:])]:
    pair=Image.new('RGBA',(240,len(group)*28),'#444444')
    for row,e in enumerate(group):
        for col,im in enumerate([original,current]):pair.alpha_composite(im.crop(e[0]),(col*120+4,row*28+4))
    pair.resize((720,pair.height*3),Image.Resampling.NEAREST).save(out/f'{name}_compare.png')
write(out/'review.json',dict(status='pending_user_visual_review',source_png=source.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),labels=[e[1] for e in edits],new_pixel_edits=False,encoded=False,packaged=False))
