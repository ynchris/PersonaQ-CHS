"""Measure static glyph advances; never equate this estimate with runtime fit."""
from functools import lru_cache
import hashlib
from compile_translation import ROOT, read, write, TOKEN
from raw_text_codec import encode_display


def measure(text, char_width):
    lines=TOKEN.sub('',text).splitlines()
    widths=[];missing=set()
    for line in lines:
        total=0
        for char in line:
            value=char_width(char)
            if value is None:missing.add(char)
            else:total+=value
        widths.append(total)
    return dict(line_widths=widths,max_width=max(widths,default=0),line_count=len(lines),missing=sorted(missing))


def font_width_functions():
    mapping=read(ROOT/'translation/font_encoding.hex.json')
    fonts={r['font']:read(ROOT/'full_work/font_verify'/r['font']/f'{r["font"]}_manifest.json')
           for r in read(ROOT/'translation/font_build.generated.json')}
    widths={}
    for name,font in fonts.items():
        def factory(font,translated):
            @lru_cache(None)
            def width(char):
                try:raw=encode_display(char,mapping) if translated else char.encode('cp932')
                except (UnicodeEncodeError,ValueError):return None
                glyph=font['glyphMap'].get(chr(int.from_bytes(raw,'big')))
                if glyph is None:return None
                return font['glyphWidths'].get(str(glyph),{}).get('char',font['fontInfo']['defaultWidth']['charWidth'])
            return width
        widths[name]=(factory(font,False),factory(font,True))
    return widths


def main():
    catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')}
    widths=font_width_functions()
    rows=[]
    for warning in read(ROOT/'translation/progress.generated.json')['warnings']:
        if warning['kind']!='layout_review':continue
        row=catalog[warning['key']];metrics={}
        for name,(old_width,new_width) in widths.items():
            old=measure(row['original'],old_width);new=measure(row['translation'],new_width)
            metrics[name]=dict(original=old,translation=new,growth_px=new['max_width']-old['max_width'])
        missing=any(m[side]['missing'] for m in metrics.values() for side in ['original','translation'])
        rows.append(dict(key=row['key'],translation_sha256=hashlib.sha256(row['translation'].encode('utf-8')).hexdigest(),
                         metrics=metrics,static_metrics_complete=not missing,
                         max_growth_px=max(m['growth_px'] for m in metrics.values()),
                         runtime_fit_verified=False))
    rows.sort(key=lambda r:(r['max_growth_px'],r['key']),reverse=True)
    write(ROOT/'translation/layout_metrics.generated.json',dict(rows=rows,count=len(rows),
        notes=['Uses CWDH advance widths from six rebuilt fonts, with actual translation byte mapping.',
               'Controls are omitted, not interpreted: dynamic names, values, icons, scale and positioning remain unknown.',
               'Font selection, line spacing and textbox bounds are not established; no row is marked runtime-safe.']))
    print('Measured layout warnings:',len(rows),'incomplete static metrics:',sum(not r['static_metrics_complete'] for r in rows))
    for r in rows[:20]:
        print(r['key'],r['max_growth_px'],repr(TOKEN.sub('',catalog[r['key']]['translation'])))


if __name__=='__main__':main()
