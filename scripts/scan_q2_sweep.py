"""Inventory remaining exact/format-normalized references once, with provenance."""
import hashlib
import re
from collections import defaultdict,Counter
from compile_translation import ROOT,read,write,LEADING,TRAILING
from scan_latest_q2_myth import LATEST

def decode(text):
    text=re.sub(r'\[(占位A|颜色) ([0-9A-F]{2})\]',lambda m:'{F2 '+('44' if m[1]=='占位A' else '01')+' '+m[2]+' 01}',text)
    text=re.sub(r'\[占位B ([0-9A-F]{2})\]',r'{F4 45 04 01 00 00 \1 01}',text)
    text=re.sub(r'\[道具 ([0-9A-F]{2})([0-9A-F]{2})\]',r'{F4 84 04 01 01 01 \2 \1}',text)
    for tag,code in [('P4姓','0D'),('P4名','0E'),('P4全','0F'),('P3姓','10'),('P3名','11'),('P3全','12'),('P3P姓','1B'),('P3P名','1C'),('P3P全','1D'),('P5姓','1E'),('P5名','1F'),('P5全','20')]:
        text=text.replace('['+tag+']','{F5 C1 '+code+' 01 01 01 01 01 01 01}')
    return re.sub(r'\[([0-9A-F]{2}(?: [0-9A-F]{2})*)\]',r'{\1}',text)

def normalized(text):
    # Whitespace and quotation forms only: never delete control codes or words.
    text=decode(text)
    text=TRAILING.sub('',LEADING.sub('',text))
    return re.sub(r'\s+','',text.translate(str.maketrans({'『':'"','』':'"','“':'"','”':'"'})))

def main():
    index=defaultdict(list)
    for p in sorted(LATEST.rglob('*.json')):
        rows=read(p)
        if not isinstance(rows,list):continue
        digest=hashlib.sha256(p.read_bytes()).hexdigest()
        for r in rows:
            if not isinstance(r,dict) or not r.get('original') or not r.get('translation'):continue
            original=r['original']
            if not re.search(r'[\u3041-\u30fa\u3400-\u9fff]',original):continue
            index[normalized(original)].append({'reference':p.relative_to(LATEST).as_posix(),'sha256':digest,'key':r.get('key'),'original':original,'translation':r['translation'],'stage':r.get('stage')})
    result=[]
    for r in read(ROOT/'translation/catalog.working.json'):
        if r.get('translation'):continue
        refs=index.get(normalized(r['original']),[])
        if refs:
            result.append({'key':r['key'],'source':r['source'],'message_index':r['message_index'],'line_index':r['line_index'],'original':r['original'],'references':refs})
    write(ROOT/'translation/q2_sweep_384.candidates.generated.json',result)
    tables=[]
    for r in read(ROOT/'translation/tables.catalog.working.json'):
        if r.get('translation'):continue
        refs=index.get(normalized(r['original']),[])
        if refs:tables.append({**r,'references':refs})
    write(ROOT/'translation/q2_sweep_384.tables.generated.json',tables)
    print('Message candidates:',len(result),'Table candidates:',len(tables))
    print(Counter(r['source'] for r in result).most_common(20))

if __name__=='__main__':main()
