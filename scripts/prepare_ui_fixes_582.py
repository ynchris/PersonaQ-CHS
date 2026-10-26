"""Prepare audited UI strings and facility speaker fixes, without ROM packaging."""
import json,hashlib
from pathlib import Path
from raw_text_codec import encode_display,decode_display
R=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
T={'オーバーヒート':'过热','依頼を受けていません':'尚未接受委托','継承するスキルを選んでください':'请选择要继承的技能','全員元気です':'全员健康','次の迷宮へ向かいます':'前往下一座迷宫','装備できる武器がありません':'没有可装备的武器','ナビゲーションを設定します':'设置导航','所持ペルソナ数':'持有人格面具数','現在の装備者':'当前装备者'}
N={'マーガレット':'玛格丽特','エリザベス':'伊丽莎白','マリー':'玛丽','四六のおばちゃん':'四六大婶','紫路宮のママ':'紫路宫妈妈桑','だいだら．のオヤジ':'代达拉的老板','久慈川 りせ':'久慈川 理世','山岸 風花':'山岸 风花'}
mapping=read(R/'translation/font_encoding.hex.json');files=[]
for source in ['exefs/code.bin','update/exefs/code.bin']:
    raw=(R/source).read_bytes();rows=[]
    for jp,cn in T.items():
        n=jp.encode('cp932')+b'\0';pos=raw.find(n);assert pos>=0 and raw.find(n,pos+1)<0
        assert pos%4==0 or raw[pos-1]==0
        e=encode_display(cn,mapping);assert len(e)<len(n) and decode_display(e,mapping)==cn
        rows.append(dict(offset=pos,capacity_bytes=len(n)-1,original=jp,translation=cn))
    files.append(dict(source=source,sha256=hashlib.sha256(raw).hexdigest(),rows=rows))
write(R/'translation/code_ui_582.review.json',dict(files=files,code_written=False,packaged=False))
speakers={};hashes={};audit=[]
for p in sorted((R/'translation/compiled/export_base/facility').glob('*.json')):
    current=read(p);source='export_base/facility/'+p.name;original=read(R/source);fix=[]
    for i,jp in enumerate(current.get('speakers',[])):
        if jp not in N:continue
        cn=N[jp];assert original['speakers'][i]==jp
        encode_display(cn,mapping)
        fix.append([i,jp,cn]);audit.append(dict(source=source,index=i,original=jp,translation=cn,message_references=sum(t['speaker']==jp for t in current['texts'])))
    if fix:speakers[source]=fix;hashes[source]=hashlib.sha256((R/source).read_bytes()).hexdigest()
assert len(speakers)==8 and len(audit)==13,(len(speakers),len(audit))
write(R/'translation/batches/582_facility_speakers.json',dict(sources={},speakers=speakers,source_hashes=hashes))
write(R/'translation/ui_fixes_582.audit.json',dict(ui_phrases=T,speaker_rows=audit,speaker_files=len(speakers),packaged=False))
print('Prepared',len(T),'UI phrases x 2 executable versions;',len(audit),'speaker entries in',len(speakers),'files.')
