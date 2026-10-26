"""User-authorized deterministic text edit; keep TMX palette and BIN siblings."""
import hashlib
from PIL import Image,ImageDraw,ImageFont
from compile_translation import ROOT,write
from check_roundtrip import members
from caution_tmx_463 import decode

TITLE='注意事项'
LINES=['未经权利人许可，通过互联网传播、',
       '分发本游戏软件，或明知其为非法',
       '传播的软件仍进行下载，均为法律',
       '所严格禁止。敬请理解与配合。']
REGIONS=[(169,55,234,71),(28,80,375,155)]

def main():
    source=ROOT/'data/title/logo.bin'; blob=source.read_bytes()
    parts=members(source); original=dict(parts)['caution.tmx']
    image,palette=decode(original)
    scale=4
    for box in REGIONS:
        x0,y0,x1,y1=box
        color=image.getpixel((x0,y0)) if box==REGIONS[0] else (0,0,0,255)
        # Header is a flat gray plaque; body black. Never redraw its border.
        if box==REGIONS[0]:color=(40,40,40,255)
        region=Image.new('RGBA',((x1-x0)*scale,(y1-y0)*scale),color)
        draw=ImageDraw.Draw(region)
        font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',12*scale)
        lines=[TITLE] if box==REGIONS[0] else LINES
        for i,text in enumerate(lines):
            length=draw.textlength(text,font=font)
            assert length<region.width-4*scale
            x=(region.width-length)/2
            y=0 if box==REGIONS[0] else (2+i*18)*scale
            draw.text((x,y),text,font=font,fill=(210,210,210,255),anchor='lt')
        region=region.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS)
        image.paste(region,(x0,y0))
    assert all(r==g==b and a==255 for r,g,b,a in palette)
    nearest=[min(range(256),key=lambda j:abs(palette[j][0]-v)) for v in range(256)]
    edited=bytearray(original)
    allowed=set()
    for x0,y0,x1,y1 in REGIONS:
        for y in range(y0,y1):
            for x in range(x0,x1):
                pos=1088+y*image.width+x
                edited[pos]=nearest[image.getpixel((x,y))[0]];allowed.add(pos)
    assert edited[:1088]==original[:1088]
    assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,edited)))
    reread,_=decode(edited)
    preview=ROOT/'translation/caution_463_chinese.png';reread.save(preview)
    output=bytearray(blob);pos=4
    for name,data in parts:
        start=pos+36
        if name=='caution.tmx':output[start:start+len(data)]=edited
        pos=start+len(data)
    target=ROOT/'full_work/reviewed_images_463/title/logo.bin'
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(output)
    result=members(target)
    assert len(output)==len(blob) and [n for n,_ in result]==[n for n,_ in parts]
    for (name,before),(_,after) in zip(parts,result):
        assert after==(bytes(edited) if name=='caution.tmx' else before)
    write(ROOT/'translation/caution_463.generated.json',dict(source='title/logo.bin',member='caution.tmx',
       source_sha256=hashlib.sha256(blob).hexdigest(),output=target.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(output).hexdigest(),
       title=TITLE,lines=LINES,regions=REGIONS,palette_and_header_preserved=True,sibling_resources_preserved=True,
       pixels_outside_text_preserved=True,preview=preview.relative_to(ROOT).as_posix(),
       visual_review_pending=True,packaged=False,runtime_tested=False))
    print('Startup notice rebuilt, original palette and sibling logos preserved.')

if __name__=='__main__':main()
