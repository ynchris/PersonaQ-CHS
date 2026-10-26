"""Wrap raw STEX ETC1A4 payloads in diagnostic CTPKs for existing decoder."""
import struct,subprocess,json
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
out=ROOT/'translation/stex_inspection_531';(out/'source').mkdir(parents=True,exist_ok=True)
from check_roundtrip import parse_members
template=dict(parse_members((ROOT/'data/init/nameentry.arc').read_bytes()))['key_board_button.ctpk'][:128]
rows=[]
for p in sorted((ROOT/'data/effect').glob('*.stex')):
    raw=p.read_bytes();w,h=struct.unpack_from('<II',raw,12);start=struct.unpack_from('<I',raw,32)[0]
    assert raw[:4]==b'STEX' and struct.unpack_from('<I',raw,24)[0]==0x675b
    payload=raw[start:];assert len(payload)==w*h
    header=bytearray(template)
    struct.pack_into('<II',header,8,128,len(payload))
    struct.pack_into('<IIIHH',header,36,len(payload),0,13,w,h)
    (out/'source'/(p.stem+'.ctpk')).write_bytes(header+payload)
    rows.append(dict(source=p.relative_to(ROOT).as_posix(),width=w,height=h))
dotnet=ROOT.parent/'tools/dotnet8/dotnet.exe'
helper=ROOT.parent/'references/PersonaQ2ChsLocalization/bin/PersonaQ2ChsLocalizationHelper/PersonaQ2ChsLocalizationHelper/bin/Release/net8.0-windows/publish/PersonaQ2ChsLocalizationHelper.dll'
subprocess.run([str(dotnet),str(helper),'export','-i',str(out/'source'),'-o',str(out/'decoded')],check=True)
(out/'report.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
canvas=Image.new('RGB',(1024,6*276),'#222222');d=ImageDraw.Draw(canvas)
for i,p in enumerate(sorted((out/'decoded').glob('*.png'))):
    im=Image.open(p).convert('RGBA');x=i%4*256;y=i//4*276
    canvas.paste(im,(x,y),im);d.text((x,y+257),p.name,fill='white')
canvas.save(out/'stex_contact.png')
