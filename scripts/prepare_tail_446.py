import hashlib
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING
from prepare_sklcard_428 import replace_slots
BATTLE={169:'其他玩家正在输入。\n请稍候。',183:'展开了火焰机器人！',184:'展开了冰冻机器人！',185:'展开了雷电机器人！',198:'神树的触手',203:'符文的引导对{F2 44 02 01}的弱点产生了反应！',210:'乐园引路人出现了！',211:'乐园引路人',212:'扭曲的丰穰神树',232:'爆发槽减少了！',241:'做好了追击的准备！',245:'难以名状之神苏醒了！',248:'击败了深王和奥林匹亚！',249:'击败了守门人！',275:'爆发槽降低了！',276:'的炮剑过热了！',277:'的炮剑冷却，恢复了功能！'}
SOURCES={s:{(i,0):t+'\n' for i,t in BATTLE.items()} for s in ['export_base/battle/message/battlemessage.bmd.json','export_base/battle/pack/btl_com.arc_battlemessage.bmd.json']}
SOURCES.update({
'export_base/facility/msg_combine_lvup.bmd.json':{(10,0):'＞听到了“{F2 01 02 01}{F2 44 01 01}{F2 01 01 01}”的哭声…\n',(13,0):'＞人格面具“{F2 01 02 01}{F2 44 01 01}{F2 01 01 01}”\n　似乎即将产下什么东西…\n',(14,0):'＞“{F2 01 02 01}{F2 44 01 01}{F2 01 01 01}”的\n　“受胎征兆”消失了…\n',(15,0):'＞“{F2 01 02 01}{F2 44 01 01}{F2 01 01 01}”竟然\n　产下了“{F2 01 02 01}{F2 44 02 01}{F2 01 01 01}”！\n',(20,0):'＞看过电影后，各项能力获得了额外加成！\n'},
'export_base/facility/msg_market.bmd.json':{(1,0):'＞个共日元。\n　购买吗？\n',(11,0):'＞就这样出售，可以吗？\n'},
'export_base/facility/msg_unite.bmd.json':{(1,0):'＞确定选择这件武器吗？\n',(2,0):'＞{F2 01 02 01}{F2 44 01 01}{F2 01 01 01}\n已获得。\n'},
'export_base/facility/party_edit_msg.bmd.json':{(1,0):'狂欢模式的说明。\n毕竟，这可是艺术。\n',(1,1):'我可是满心期待啊！\n'},
'export_base/facility/town.bf.json':{(1,0):'“编队”{F2 01 01 01}\n功能已开放。\n　\n来实际编组一下队伍吧。\n',(6,0):'“手工工坊”{F2 01 01 01}\n现已开放。\n　\n可以在这里买卖装备和道具，\n也可以寄存随身物品。\n'},
'export_base/init/datskillhelp.bmd.json':{(141,0):'延迟突刺（实体）\n',(148,0):'复仇重击（实体）\n',(173,0):'乾坤一掷后：麻痹\n',(359,0):'《情报支援用》\n促进治愈的持续效果栏位\n',(503,0):'爆发槽更容易积攒。\n',(935,0):'乾坤一掷后：麻痹\n',(1212,0):'大蜘蛛第一形态时\n普通ＡＴＴＡＣＫ\n'},
})
CARD={141:('物理','（残心的一击）'),148:('物理','（忍耐的一击）'),173:('物理','（光明波）'),294:('辅助','（冥府的邀约）'),296:('辅助','（灾厄到来）'),300:('辅助','（再生竖琴）'),360:('情报支援','总攻击（镜头用）'),373:('情报支援','丰厚礼物（控制用）'),374:('情报支援','神圣礼物（控制用）'),384:('持续','开始'),394:('持续','持续魔封'),404:('埃癸斯','狂欢模式（发动）'),407:('辅助','（回复纪念品）'),409:('辅助','（解放纪念品）'),411:('辅助','（自净纪念品）'),414:('辅助','（绝命反击）'),416:('辅助','（死亡追逐者）'),418:('辅助','（猛攻架势）'),426:('物理','（连锁炎刃）'),428:('物理','（连锁冰刃）'),430:('物理','（连锁雷刃）'),432:('物理','（连锁风刃）'),435:('姿态','猛袭之舞（持续）'),596:('自动效果','（审判之剑）')}
SOURCES['export_base/init/datskillcardhelp.bmd.json']={(i,0):f'可以习得{kind}技能\n“{name}”的技能卡。\n' for i,(kind,name) in CARD.items()}
SOURCES['export_base/init/datskillhelp.bmd.json'][359,0]='《情报支援用》\n促进治愈的持续栏位\n'
def main():
    p=ROOT/'translation/batches/446_battle_facility_skill_tail.generated.json';assert not p.exists()
    cat={r['key']:r for r in read(ROOT/'translation/catalog.working.json')};sources={};hashes={}
    for s,texts in SOURCES.items():
        d=read(ROOT/s);rows=[]
        for (i,j),body in texts.items():
            r=cat[f'{s}:{i}:{j}'];assert not r.get('translation');old=r['original'];pre=LEADING.match(old).group();suf=TRAILING.search(old).group()
            if s.endswith('msg_market.bmd.json'):
                full=replace_slots(old,body);body=full[len(pre):len(full)-len(suf)]
            else:full=pre+body+suf
            assert TOKEN.findall(full)==TOKEN.findall(old),(s,i,j)
            a=TOKEN.sub('',old).splitlines();b=TOKEN.sub('',full).splitlines()
            assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),(s,i,j)
            rows.append([i,j,d['texts'][i]['id'],body])
        sources[s]=rows;hashes[s]=hashlib.sha256((ROOT/s).read_bytes()).hexdigest()
    write(p,dict(status='draft',sources=sources,source_hashes=hashes,review_notes=['补齐战斗遗留提示、设施、合体受胎提示和24项括号/内部技能卡说明；保留括号和控制用途，不凭括号判断可达性。','技能名优先沿用Q2复用表及本作补译表；内部旧名延迟突刺/复仇重击等按原文翻译，未改游戏机制。','市场数量和金额变量维持原字槽位置：数量后个共、金额后日元；自称老夫的复用候选改为中性我，避免跨角色误用。']))
    print('Pages:',sum(map(len,sources.values())))
if __name__=='__main__':main()
