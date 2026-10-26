"""Read-only candidates, not an executable patch or proof of string boundaries."""
import hashlib,re
from compile_translation import ROOT,write
def scan(path):
    raw=path.read_bytes();result=[]
    for m in re.finditer(rb'[^\x00]{4,}\x00',raw):
        data=m.group()[:-1]
        if len(data)>512:continue
        try:text=data.decode('cp932')
        except UnicodeDecodeError:continue
        if any(ord(c)<32 and c not in '\n\r\t' for c in text):continue
        if not re.search(r'[\u3041-\u3096\u30a1-\u30fa]',text):continue
        if any(0xe000<=ord(c)<=0xf8ff or 0xff61<=ord(c)<=0xff9f for c in text):continue
        result.append(dict(offset=m.start(),capacity_bytes=len(data),original=text,status='candidate_unreviewed'))
    return dict(source=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),candidates=result)
def main():
    reports=[scan(ROOT/s) for s in ['exefs/code.bin','update/exefs/code.bin']]
    write(ROOT/'translation/executable_candidates.generated.json',dict(files=reports,policy='NUL-delimited strict CP932 candidates only; false positives possible. No original or executable modified; exact capacity and references need review.'))
    for r in reports:print(r['source'],len(r['candidates']))
    for r in reports[1]['candidates'][:60]:print(hex(r['offset']),repr(r['original']))
if __name__=='__main__':main()
