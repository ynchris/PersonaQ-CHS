"""Build an explicitly partial PQ1 Chinese sample with preserved BIN members."""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORK = ROOT.parent
sys.path.insert(0, str(WORK/'tools/pq_python_deps'))
from PIL import Image, ImageDraw, ImageFont
from check_roundtrip import members

FONT_TOOL = WORK/'references/PersonaQ2ChsLocalization/bin/3dstools/bcfnt.py'
HELPER = WORK/'references/PersonaQ2ChsLocalization/bin/PersonaQ2ChsLocalizationHelper/PersonaQ2ChsLocalizationHelper/bin/Release/net8.0-windows/publish/PersonaQ2ChsLocalizationHelper.dll'
DOTNET = WORK/'tools/dotnet8/dotnet.exe'
MAPPING = dict(zip('剧变开戏择时标确请适选难题游无', '劇変開戯択時標確請適選難題遊無'))

def run(args, cwd=ROOT):
    env = os.environ.copy()
    env['PYTHONPATH'] = str(WORK/'tools/pq_python_deps')
    env['PYTHONIOENCODING'] = 'utf-8'
    subprocess.run([str(a) for a in args], cwd=cwd, env=env, check=True)

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    run([sys.executable, ROOT/'validate_translation.py'])
    # Every encoded surrogate must be valid CP932. Glyphs are changed consistently.
    for char in MAPPING.values():
        char.encode('cp932')
    source = json.loads((ROOT/'test_json/difficultyselect.bin_difficultyselect.bmd.json').read_text(encoding='utf-8'))
    translation = json.loads((ROOT/'translation/difficultyselect.zh-Hans.json').read_text(encoding='utf-8'))
    for msg, lines in zip(source['texts'], translation['messages']):
        msg['lines'] = [''.join(MAPPING.get(c,c) for c in s) for s in lines]
        for line in msg['lines']:
            line.encode('cp932', errors='strict')
    stage = ROOT/'sample_work'
    incoming = stage/'messages'
    incoming.mkdir(parents=True,exist_ok=True)
    (incoming/'difficultyselect.bin_difficultyselect.bmd.json').write_text(json.dumps(source,ensure_ascii=False,indent=2),encoding='utf-8')
    run([DOTNET, HELPER, 'import', '-i', ROOT/'test_input', '-j', incoming, '-o', stage/'rebuilt'])
    payload = ROOT/'sample_payload_v3'
    payload.mkdir(exist_ok=True)
    target = payload/'title/difficultyselect.bin'
    # The preservation tool intentionally rejects overwrites.
    if target.exists():
        expected = dict(members(ROOT/'test_input/difficultyselect.bin'))
        expected['difficultyselect.bmd'] = dict(members(stage/'rebuilt/difficultyselect.bin'))['difficultyselect.bmd']
        assert dict(members(target)) == expected, 'Existing sample differs; preserve it and stop'
    else:
        run([sys.executable, ROOT/'repack_text_member.py', ROOT/'test_input/difficultyselect.bin',stage/'rebuilt/difficultyselect.bin','difficultyselect.bmd',target])
    font_report = []
    for fontpath in sorted((ROOT/'data/font').glob('*.bcfnt')):
        name = fontpath.stem
        directory = stage/'fonts'/name
        directory.mkdir(parents=True,exist_ok=True)
        run([sys.executable,FONT_TOOL,'-x','-y','-f',fontpath],directory)
        manifestpath=directory/f'{name}_manifest.json'
        manifest=json.loads(manifestpath.read_text(encoding='utf-8'))
        info=manifest['textureInfo']
        cols=info['sheetInfo']['cols']; rows=info['sheetInfo']['rows']
        cellw=info['glyph']['width']+1; cellh=info['glyph']['height']+1
        sheets={}; changed=[]; missing=[]
        font_size=max(8,manifest['fontInfo']['width']-1)
        face=ImageFont.truetype(str(ROOT/'fonts/SourceHanSansSC-Medium.otf'),font_size*4)
        for chinese, encoded in MAPPING.items():
            code=chr(int.from_bytes(encoded.encode('cp932'),'big'))
            index=manifest['glyphMap'].get(code)
            if index is None:
                missing.append(chinese); continue
            sheetno=index//(cols*rows); slot=index%(cols*rows)
            if sheetno not in sheets:
                sheets[sheetno]=Image.open(directory/f'{name}_sheet{sheetno}.png').convert('RGBA')
            x=(slot%cols)*cellw+1; y=(slot//cols)*cellh+2
            glyph=Image.new('RGBA',(cellw*4,cellh*4))
            draw=ImageDraw.Draw(glyph)
            draw.text((0,(manifest['fontInfo']['ascent']+0.5)*4),chinese,font=face,fill='white',anchor='ls')
            glyph=glyph.resize((cellw,cellh),Image.Resampling.LANCZOS)
            sheets[sheetno].paste(glyph,(x,y))
            changed.append(chinese)
        for number,sheet in sheets.items():
            sheet.save(directory/f'{name}_sheet{number}.png')
        if changed:
            (payload/'font').mkdir(exist_ok=True)
            run([sys.executable,FONT_TOOL,'-c','-y','-f',payload/'font'/fontpath.name],directory)
        font_report.append(dict(font=name,changed=changed,missing=missing))
    (ROOT/'sample_font_report.json').write_text(json.dumps(font_report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Partial sample payload generated; packaging and runtime checks are still required.')

if __name__=='__main__':
    main()
