"""Resolve every cached message/table candidate into applied or explicit exclusion."""
import hashlib
import re
import unicodedata
from collections import Counter,defaultdict
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING
from scan_q2_sweep import decode,normalized
from scan_latest_q2_myth import LATEST

def numbers(s):return Counter(re.findall(r'\d+',unicodedata.normalize('NFKC',TOKEN.sub('',s))))
def exclude(r):
    s=r['source'];text=TOKEN.sub('',r['original']).strip()
    if re.search(r'ダミ|だみ|ブランク|ＢＬＡＮＫ|ID_|枠最後|特殊イベントです|クエスト００|文章未定|仕様カット|継続用枠|挨拶[１２]|警告文|の解説|メッセージ$',text) or text=='なし':return 'placeholder_or_internal_slot'
    if any(x in s for x in ['cmbtalk.bf','msg_combine.bmd','msg_combine_lvup.bmd','msg_unite.bmd','cmppoem.bf','/e999_','mission_','gsobserver']):return 'legacy_or_debug_context'
    if 'party_edit_msg' in s:return 'placeholder_context'
    if 'datskillcardhelp' in s and re.search(r'（|\(|継続|持続|制御|カメラ',text):return 'internal_skill_card_slot'
    if 'dungeon03f' in s or 'dungeon41f' in s:return 'debug_selection_context'
    if s.endswith('msg_weapon.bmd.json') and r['message_index']==81:return 'legacy_shop_dialogue'
    if re.search(r'深王|オランピア|ゲートキーパー|神樹|楽園への導き手|名状し難き神|バーストゲージ|ルーンの導き|ボット|砲剣|石化|他のＰＬＡＹＥＲ',text):return 'legacy_battle_mechanic'
    return None

def render(old,translation):
    value=decode(translation).strip()
    # External controls are restored from PQ1. Remove only compatible edge runs.
    prefix=LEADING.match(old).group();suffix=TRAILING.search(old).group()
    lead=LEADING.match(value).group();tail=TRAILING.search(value).group()
    if lead and prefix.endswith(lead):value=value[len(lead):]
    if tail and suffix.startswith(tail):value=value[:-len(tail)]
    value=value.replace('瞬缘连接','擦肩通信').replace('瞬缘笔记','擦肩笔记').replace('从的周围','的周围')
    value=value.replace('队伍编辑','队伍编成').replace('通过合成','通过合体')
    value=value.replace('发出低吼声逼近','发出低吼扑了过来').replace('高举大镰刀逼近','高举大镰刀袭来')
    if TRAILING.sub('',LEADING.sub('',old)).endswith('\n'):value+='\n'
    full=prefix+value+suffix
    if TOKEN.findall(full)!=TOKEN.findall(old):return None,'controls'
    if re.search(r'[\u3041-\u3096\u30a1-\u30fa\[\]]',TOKEN.sub('',value)):return None,'kana_or_unknown_tags'
    if numbers(full)!=numbers(old):return None,'numbers'
    oldlines=TOKEN.sub('',old).strip().splitlines()
    width=max(map(len,oldlines),default=1)
    if max(map(len,TOKEN.sub('',value).splitlines()),default=0)>width:
        # Wrap visible characters without splitting control tokens or changing order.
        parts=re.findall(TOKEN.pattern+r'|[^{}]',value)
        out=[];col=0
        for p in parts:
            if TOKEN.fullmatch(p):out.append(p);continue
            if p=='\n':out.append(p);col=0;continue
            if col==width:out.append('\n');col=0
            out.append(p);col+=1
        value=''.join(out)
    if len(TOKEN.sub('',value).strip().splitlines())>len(oldlines):return None,'line_count'
    return value,None

def main():
    plan=read(ROOT/'translation/q2_sweep_384.review.json')
    candidates=read(ROOT/'translation/q2_sweep_384.candidates.generated.json')
    current={r['key']:r for r in read(ROOT/'translation/catalog.working.json')}
    report=[];pending=[];sources=defaultdict(list);hashes={};cache={}
    for r in candidates:
        reason=exclude(r)
        if reason:report.append({'key':r['key'],'status':reason});continue
        if current[r['key']].get('translation'):raise ValueError('Already translated '+r['key'])
        refs=r['references'];same=[x for x in refs if x['reference']==r['source'].removeprefix('export_base/')]
        choices=same or refs
        variants={decode(x['translation']).strip() for x in choices}
        override=plan['overrides'].get(r['key'])
        if len(variants)>1 and override is None:
            pending.append({'key':r['key'],'reason':'conflict','original':r['original'],'variants':sorted(variants)});continue
        value,issue=render(r['original'],override if override is not None else choices[0]['translation'])
        if issue:
            pending.append({'key':r['key'],'reason':issue,'original':r['original'],'translation':choices[0]['translation']});continue
        for ref in choices:
            p=LATEST/ref['reference']
            if p not in cache:cache[p]=(hashlib.sha256(p.read_bytes()).hexdigest(),read(p))
            digest,items=cache[p]
            assert digest==ref['sha256']
            assert normalized(ref['original'])==normalized(r['original'])
            assert any(x.get('key')==ref['key'] and x.get('original')==ref['original'] and x.get('translation')==ref['translation'] for x in items)
        source=r['source'];mi=r['message_index'];li=r['line_index']
        doc=read(ROOT/source)
        sources[source].append([mi,li,doc['texts'][mi]['id'],value])
        hashes[source]=hashlib.sha256((ROOT/source).read_bytes()).hexdigest()
        report.append({**r,'references':choices,'status':'applied','final_body':value,'override':override})
    write(ROOT/'translation/q2_sweep_384.pending.generated.json',pending)
    print('Messages:',Counter(r['status'] for r in report),'pending',len(pending))
    if pending:return
    target=ROOT/'translation/batches/384_q2_normalized_sweep.generated.json'
    assert not target.exists()
    write(target,{'status':'draft','sources':dict(sources),'source_hashes':hashes,'review_notes':['对全量未译候选进行格式规范化匹配；保留一代外层控制码及完整内部控制序列。','冲突和布局不合自动拒绝，审校后才导入。占位、明确旧作/调试语境单独记录，不计入已译。','运行未验证，泛用战斗语句并不保证每项会在PQ1出现。']})
    write(ROOT/'translation/q2_sweep_384.audit.generated.json',{'reference_commit':'15ca3ffda260133bfb090fc8a5b5ea896553f37c','plan_sha256':hashlib.sha256((ROOT/'translation/q2_sweep_384.review.json').read_bytes()).hexdigest(),'entries':report,'runtime_tested':False})

if __name__=='__main__':main()
