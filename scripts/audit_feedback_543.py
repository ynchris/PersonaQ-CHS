"""Audit actual glyph cells, enemy references, and multi-texture SPR3 files."""
import struct,hashlib
from PIL import Image,ImageDraw
from compile_translation import ROOT,read,write,TOKEN
from q2_name_banks import load
from check_roundtrip import parse_members
OUT=ROOT/'translation/feedback_543'

def fonts():
    mapping=read(ROOT/'translation/font_encoding.hex.json');report=[]
    phrases=['蕾丝衬衫','京折扇','更换谁的装备？','谎言夸口者','记忆光标位置']
    folders=sorted((ROOT/'full_work/font_verify').glob('*'))
    canvas=Image.new('RGB',(1050,len(folders)*105),'#222222');draw=ImageDraw.Draw(canvas)
    for row,folder in enumerate(folders):
        name=folder.name;m=read(folder/f'{name}_manifest.json')
        old=read(ROOT/f'full_work/font_original/{name}/{name}_manifest.json')
        tx=m['textureInfo'];si=tx['sheetInfo'];cw=tx['glyph']['width']+1;ch=tx['glyph']['height']+1;per=si['cols']*si['rows'];cache={}
        draw.text((5,row*105+3),name,fill='white')
        x=5
        for phrase in phrases:
            for char in phrase:
                code=chr(int(mapping[char],16));index=m['glyphMap'][code]
                sheet,slot=divmod(index,per)
                if sheet not in cache:cache[sheet]=Image.open(folder/f'{name}_sheet{sheet}.png').convert('RGBA')
                sx=slot%si['cols']*cw+1;sy=slot//si['cols']*ch+2
                glyph=cache[sheet].crop((sx,sy,sx+cw,sy+ch))
                report.append(dict(font=name,char=char,original=code in old['glyphMap'],index=index,
                    bbox=glyph.getchannel('A').getbbox(),metrics=m['glyphWidths'][str(index)],fontInfo=m['fontInfo'],cell=[cw,ch]))
                canvas.paste(glyph.resize((cw*2,ch*2),Image.Resampling.NEAREST),(x,row*105+30),glyph.resize((cw*2,ch*2),Image.Resampling.NEAREST))
                x+=m['glyphWidths'][str(index)]['char']*2
            x+=20
    canvas.save(OUT/'actual_font_samples.png');write(OUT/'font_metrics.json',report)
    for r in report:
        if r['char'] in '蕾丝衬衫':print({k:r[k] for k in ['font','char','original','bbox','metrics','cell']})

def enemies():
    names={r['original']:r['translation'] for g in load()['groups'] if g['source']=='battle/table/enemynametable.tbl' for r in g['rows']}
    rows=[]
    for r in read(ROOT/'translation/catalog.working.json'):
        if not r.get('translation'):continue
        original=TOKEN.sub('',r['original']);translated=TOKEN.sub('',r['translation'])
        found=[n for n in names if n in original]
        found=[n for n in found if not any(n!=m and n in m for m in found)]
        for n in found:
            if names[n] not in translated:rows.append(dict(key=r['key'],enemy=n,expected=names[n],original=original,translation=translated))
    write(OUT/'enemy_candidates.json',rows);print('Enemy reference candidates:',len(rows))

def textures():
    rows=[]
    def inspect(label,raw):
        if raw[8:12]!=b'SPR3':return
        count=struct.unpack_from('<H',raw,20)[0]
        if count<2:return
        records=[];pos=0
        while True:
            off=raw.find(b'CTPK',pos)
            if off<0:break
            section,size=struct.unpack_from('<II',raw,off+8)
            assert off+section+size<=len(raw),label
            records.append(dict(offset=off,bytes=section+size));pos=off+section+size
        rows.append(dict(source=label,header_count=count,textures=records))
    for p in (ROOT/'data').rglob('*'):
        if not p.is_file() or p.suffix not in ('.spr3','.arc','.bin'):continue
        raw=p.read_bytes();label=p.relative_to(ROOT/'data').as_posix()
        if p.suffix=='.spr3':inspect(label,raw)
        else:
            try:parts=parse_members(raw)
            except Exception:continue
            for name,b in parts:
                if name.endswith('.spr3'):inspect(label+'::'+name,b)
    write(OUT/'multi_texture_inventory.json',rows);print('Multi-texture SPR3:',len(rows))

if __name__=='__main__':
    OUT.mkdir(exist_ok=True);fonts();enemies();textures()
