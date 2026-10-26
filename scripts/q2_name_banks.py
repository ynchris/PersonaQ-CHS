"""Exact-reference name reuse in bounded cumulative-u16 string banks only."""
import hashlib
import re
import struct
import sys
from collections import Counter
from compile_translation import ROOT,read,write
from scan_latest_q2_myth import LATEST
from raw_text_codec import encode_display,decode_display

SOURCES={'battle/table/enemynametable.tbl':368,'battle/table/skillnametable.tbl':1376,
         'battle/table/playerskillnametable.tbl':422,'battle/table/enemyskillnametable.tbl':480,
         'battle/message/playerskillnametable.tbl':422,'battle/message/enemyskillnametable.tbl':480}
DRAFT=ROOT/'translation/q2_name_banks.review.generated.json'
CHOICES={'ナイアーム':'缴械','アサルトショット':'突击射击','獣の咆哮':'野兽咆哮','灼熱発破':'灼热爆破','連鎖の風':'连锁风'}

def parse(data,count):
    if len(data)<2+2*count or struct.unpack_from('<H',data)[0]!=count:raise ValueError('Unexpected count')
    ends=[0]+list(struct.unpack_from('<'+str(count)+'H',data,2));start=2+2*count
    if start+ends[-1]!=len(data):raise ValueError('Unexpected bank end')
    chunks=[]
    for a,b in zip(ends,ends[1:]):
        chunk=data[start+a:start+b]
        if b<=a or not chunk.endswith(b'\0') or b'\0' in chunk[:-1]:raise ValueError('Invalid name span')
        chunks.append(chunk)
    return chunks

def excluded(name):return not name.strip() or bool(re.search(r'ブランク|ダミ|^0x|未使用|リザーブ|（|\(|制御用|カメラ用',name))

def prepare():
    assert not DRAFT.exists()
    groups=[];pending=[]
    for source,count in SOURCES.items():
        refrel='battle/table/enemynametable.tbl.json' if source.endswith('/enemynametable.tbl') else 'battle/table/skillnametable.tbl.json'
        refpath=LATEST/refrel;refs=read(refpath)
        data=(ROOT/'data'/source).read_bytes();chunks=parse(data,count)
        rows=[];skipped=[]
        for i,chunk in enumerate(chunks):
            name=chunk[:-1].decode('cp932')
            if excluded(name):skipped.append({'index':i,'original':name,'reason':'placeholder_or_internal'});continue
            matches=[r for r in refs if r['original']==name and r.get('translation')]
            variants={r['translation'].strip() for r in matches}
            if not variants:skipped.append({'index':i,'original':name,'reason':'no_exact_reference'});continue
            if len(variants)!=1 and name not in CHOICES:pending.append((source,i,name,sorted(variants)));continue
            text=CHOICES.get(name,next(iter(variants)))
            assert text in variants
            if re.search(r'[\u3041-\u3096\u30a1-\u30fa{}\[\]\x00\r\n]',text):pending.append((source,i,name,text));continue
            rows.append({'index':i,'original':name,'translation':text,'references':[{k:r.get(k) for k in ['key','original','translation','stage']} for r in matches]})
        groups.append({'source':source,'count':count,'source_sha256':hashlib.sha256(data).hexdigest(),'reference':refrel,'reference_sha256':hashlib.sha256(refpath.read_bytes()).hexdigest(),'rows':rows,'excluded':skipped})
    write(ROOT/'translation/q2_name_banks.pending.generated.json',pending)
    if pending:print('Pending',pending);return
    write(DRAFT,{'status':'draft_exact_reference_reuse','reference_commit':'15ca3ffda260133bfb090fc8a5b5ea896553f37c','groups':groups,'runtime_tested':False})
    print('Name bank matched slots:',sum(len(g['rows']) for g in groups),'by source',[(g['source'],len(g['rows'])) for g in groups])

def load():
    draft=read(DRAFT)
    skill_path=ROOT/'translation/skill_names_completion.review.json'
    if skill_path.exists():
        skill=read(skill_path)
        group=next(g for g in draft['groups'] if g['source']==skill['source'])
        assert group['source_sha256']==skill['source_sha256']
        assert {r['index'] for r in group['excluded']}=={r['index'] for r in skill['rows']+skill['excluded']}
        group['rows'].extend(skill['rows'])
        group['excluded']=skill['excluded']
        draft['skill_completion_sha256']=hashlib.sha256(skill_path.read_bytes()).hexdigest()
    extra_path=ROOT/'translation/enemy_names_completion.review.json'
    if extra_path.exists():
        extra=read(extra_path)
        group=next(g for g in draft['groups'] if g['source']==extra['source'])
        assert group['source_sha256']==extra['source_sha256']
        indices={r['index'] for r in extra['rows']}
        assert indices <= {r['index'] for r in group['excluded']}
        group['rows'].extend(extra['rows'])
        group['excluded']=[r for r in group['excluded'] if r['index'] not in indices]
        draft['local_completion_sha256']=hashlib.sha256(extra_path.read_bytes()).hexdigest()
    for group in draft['groups']:
        source=group['source'];data=(ROOT/'data'/source).read_bytes()
        assert source in SOURCES and group['count']==SOURCES[source]
        assert hashlib.sha256(data).hexdigest()==group['source_sha256']
        chunks=parse(data,group['count']);seen=set()
        for row in group['rows']:
            i=row['index'];assert i not in seen and chunks[i][:-1].decode('cp932')==row['original'];seen.add(i)
            assert not excluded(row['original'])
            from terminology_555 import apply_bank
            apply_bank(source,row)
    return draft

def build_bank(data,count,rows,mapping):
    old=parse(data,count);new=list(old)
    for row in rows:
        raw=encode_display(row['translation'],mapping)
        if b'\0' in raw or not raw:raise ValueError('Invalid encoded name')
        new[row['index']]=raw+b'\0'
    ends=[];total=0
    for chunk in new:
        total+=len(chunk)
        if total>65535:raise ValueError('Name bank overflow')
        ends.append(total)
    result=struct.pack('<H',count)+struct.pack('<'+str(count)+'H',*ends)+b''.join(new)
    parsed=parse(result,count);translated={r['index']:r['translation'] for r in rows}
    for i,chunk in enumerate(parsed):
        if i in translated:assert decode_display(chunk[:-1],mapping)==translated[i]
        else:assert chunk==old[i]
    return result

def build():
    draft=load();enc=ROOT/'translation/font_encoding.hex.json';mapping=read(enc);files=[]
    for g in draft['groups']:
        data=(ROOT/'data'/g['source']).read_bytes()
        result=build_bank(data,g['count'],g['rows'],mapping)
        p=ROOT/'full_work/q2_name_payload'/g['source'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(result)
        files.append({'source':g['source'],'sha256':hashlib.sha256(result).hexdigest(),'source_sha256':g['source_sha256'],'rows':len(g['rows'])})
    write(ROOT/'translation/q2_name_banks_build.generated.json',{'draft_sha256':hashlib.sha256(DRAFT.read_bytes()).hexdigest(),'local_completion_sha256':draft.get('local_completion_sha256'),'skill_completion_sha256':draft.get('skill_completion_sha256'),'encoding_sha256':hashlib.sha256(enc.read_bytes()).hexdigest(),'roundtrip_verified':True,'unselected_bytes_preserved':True,'files':files,'runtime_tested':False})
    print('Verified name banks:',len(files),'slots:',sum(f['rows'] for f in files))

if __name__=='__main__':prepare() if sys.argv[1:] == ['prepare'] else build()
