"""Reviewed party hints and Q2-derived skill-card prompts, without legacy placeholders."""
import hashlib
import re
from compile_translation import ROOT, read, write, LEADING, TRAILING, TOKEN

PARTY = {
0:'将战斗导航\n交给理世。',1:'将战斗导航\n交给风花。',
2:'将迷宫探索导航\n交给理世。',3:'将迷宫探索导航\n交给风花。',
5:'熟练运用伤害技能。',6:'熟练运用特殊技能。',7:'保护同伴免受敌人攻击。',8:'学会回复技能。',
9:'适合前排　武器：双手剑（斩击）',10:'适合前排　武器：单手剑（斩击）',
11:'适合前排　武器：短剑（斩击）',12:'适合前排　武器：腿（打击）',
13:'适合后排　武器：扇子（斩击）',14:'后方支援',15:'适合前排　武器：厚板（打击）',
16:'适合后排　武器：手枪（突刺）',17:'适合前排　武器：爪（斩击）',
18:'适合后排　武器：弓（突刺）',19:'适合前排　武器：双手剑（斩击）',
20:'适合前排　武器：拳（打击）',21:'适合前排　武器：刺剑（突刺）',22:'后方支援',
23:'适合后排　武器：重炮（打击）',24:'适合后排　武器：枪（突刺）',
25:'适合前排　武器：短剑（斩击）',26:'适合前排　武器：钝器（打击）',
27:'适合后排　武器：机械弓（突刺）',28:'适合后排　武器：机械弓（突刺）'}
SKILLS = {
(9,1):'＞“[颜色 02][占位A 02][颜色 01]”似乎\n　要发生什么变化……',
(11,0):'＞“[颜色 02][占位A 01][颜色 01]”竟然\n　强化成了“[颜色 02][占位A 02][颜色 01]”！',
(12,0):'＞“[颜色 02][占位A 01][颜色 01]”竟然\n　变成了“[颜色 02][占位A 02][颜色 01]”！',
(16,1):'＞“[颜色 02][占位A 01][颜色 01]”\n　递出了什么东西……',
(17,0):'＞竟然从“[颜色 02][占位A 01][颜色 01]”那里\n　得到了技能卡“[颜色 02][占位A 02][颜色 01]”！',
(18,0):'“技能卡”是\n能用在你的人格面具上的道具。\n人格面具会学到\n封在卡片里的技能。'}
TAGS = {'[颜色 02]':'{F2 01 02 01}','[颜色 01]':'{F2 01 01 01}',
        '[占位A 01]':'{F2 44 01 01}','[占位A 02]':'{F2 44 02 01}'}

def decode_tags(text):
    for tag,code in TAGS.items():
        text=text.replace(tag,code)
    assert '[' not in text
    return text

def normalize(text):
    text=TRAILING.sub('',LEADING.sub('',text)).strip()
    return text.translate(str.maketrans({'『':'"','』':'"','“':'"','”':'"'}))

def main():
    target=ROOT/'translation/batches/379_party_persona_prompts.generated.json'
    assert not target.exists(), 'Refusing to overwrite batch'
    current={r['key']:r for r in read(ROOT/'translation/catalog.working.json')}
    sources,hashes={},{}
    def add(source,mi,li,body):
        key=f'{source}:{mi}:{li}'
        assert not current[key].get('translation'),key
        original=current[key]['original']
        full=LEADING.match(original).group()+body+TRAILING.search(original).group()
        assert TOKEN.findall(original)==TOKEN.findall(full),key
        assert not re.search(r'[\u3041-\u3096\u30a1-\u30fa]',TOKEN.sub('',full)),key
        old,new=TOKEN.sub('',original).splitlines(),TOKEN.sub('',full).splitlines()
        assert len(new)<=len(old) and max(map(len,new))<=max(map(len,old)),key
        sources.setdefault(source,[]).append([mi,li,read(ROOT/source)['texts'][mi]['id'],body])
        hashes[source]=hashlib.sha256((ROOT/source).read_bytes()).hexdigest()
    for mi,text in PARTY.items():
        add('export_base/facility/party_edit.bmd.json',mi,0,text+'\n')
    source='export_base/facility/msg_combine_lvup.bmd.json'
    reference=ROOT.parent/'references/PersonaQ2ChsLocalization-latest-20260928/texts/zh_Hans/facility/msg_combine_lvup.bmd.json'
    refs=read(reference)
    doc=read(ROOT/source)
    audit=[]
    for (mi,li),text in SKILLS.items():
        key=doc['texts'][mi]['id']+'_'+str(li)
        ref=next(r for r in refs if r['key']==key)
        # Equality permits only quotation-style and documented tag normalization.
        assert normalize(decode_tags(ref['original']))==normalize(doc['texts'][mi]['lines'][li]),key
        body=decode_tags(text)+'\n'
        add(source,mi,li,body)
        audit.append({'message_index':mi,'line_index':li,'reference_key':key,
                      'reference_original':ref['original'],'reference_translation':ref['translation'],
                      'final_body':body,'amended':True})
    write(target,{'status':'draft','sources':sources,'source_hashes':hashes,
                  'review_notes':['队伍导航/武器定位28条依据一代原文翻译；第4条英雄类型说明占位保留。',
                                  '6条技能变化/技能卡提示参考二代15ca3ff，经标签和引号规范化核对同原文，保留一代控制码。',
                                  '将似乎已经发生修为似乎将要发生；调整行长和语气。受胎、电影等疑似旧作遗留不计本批完成。',
                                  '尚未运行验证，动态名称插入后的实际宽度仍需测试。']})
    write(ROOT/'translation/379_party_persona_prompts.audit.generated.json',{
        'reference':str(reference.relative_to(ROOT.parent)),
        'reference_sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),
        'reference_commit':'15ca3ffda260133bfb090fc8a5b5ea896553f37c',
        'entries':audit,'runtime_tested':False})
    print('Prepared 28 party hints and 6 Q2-derived skill prompts.')

if __name__=='__main__':
    main()
