import hashlib
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING
MAP=['按Ｙ键可以放大、缩小地图。','触摸选择钢笔工具，\n就可以画出墙壁的线条。','画笔工具可以为地板涂色。','触摸并拖动图标，\n就可以将其放到地图上。','橡皮擦工具可以擦除线条，\n抹布工具可以擦除地板。','紫色图标表示通常状态。\n红色图标表示追踪状态，非常危险。','蓝色表示安全状态，随后会逐渐变为\n绿色、黄色，红色则表示危险状态。','迷宫中存在这样的捷径。\n请善用专用的捷径图标。','探索率显示在\n下屏幕右上角。','地图可以放大、缩小，也可以\n自动旋转来配合面朝的方向。','触摸并拖动图标，\n就可以将其放到地图上。','也可以通过“Ｃｏｌｏｒ”调色板更改颜色。','此外，操作出错时，可以按\n“ＵＮＤＯ”按钮撤销。','将放置的图标\n拖到垃圾桶上，就能删除。']
REI=['我试着往前走走看。','撞到墙了…','前面出现了可、可怕的章鱼烧，\n走不过去了…','可、可怕的章、章鱼烧…','该怎么办…？','左右都能走。\n该怎么办…？','右边有墙，走不过去，\n不过左边能走。\n该怎么办…？','左右都有墙，走不过去。\n该怎么办…？','左右都有可、可怕的…\n章鱼烧，走不过去。\n该怎么办…？','右边有可怕的章鱼烧，\n左边又有墙，走不过去。\n该怎么办…？','右边有可怕的章鱼烧，\n走不过去，不过左边能走。\n该怎么办…？','右边能走，可左边有\n可、可怕的章鱼烧，走不过去。\n该怎么办…？','右边能走，\n可左边有墙，走不过去。\n该怎么办…？','右边有墙，\n左边又有可、可怕的章鱼烧，\n走不过去。该怎么办…？','嗯，我试着往前走。','嗯，我试着往左走。','嗯，我试着往右走。','嗯，我试着往后走。','嗯…我回入口去。','嗯！我回你们那边！','那个，我回来了…','我必须去做…','必须救大家…']
SOURCES={
'export_base/event/e900/e999_010.bf.json':{(i,0):t+'\n' for i,t in enumerate(MAP)},
'export_base/event/e900/e999_111.bf.json':{(i,0):t+'\n' for i,t in enumerate(MAP)},
'export_base/event/e900/e999_998.bf.json':{**{(i,0):t+'\n' for i,t in enumerate(REI)},(23,5):'回到这里来'},
'export_base/battle/event/all_attack_help.bf.json':{
(0,0):'　\n　\n“追击”是\n由同伴发起的攻击。\n　\n　\n　\n',
(0,1):'　\n　\n可以对敌人\n造成伤害。\n请积极争取发动机会。\n　\n　\n',
(1,0):'　\n　\n“总攻击”是\n由全体同伴发起的全体攻击。\n　\n　\n　\n',
(1,1):'　\n　\n可以对全体敌人\n造成大量伤害。\n请积极争取发动机会。\n　\n　\n'},
'export_base/battle/event/boss001.bf.json':{(0,0):'吾乃阴影…真正的自我…\n',(1,0):'无聊的东西，全都砸烂…\n',(2,0):'首先…就从你开始！！\n',(4,0):'哼，就这点本事…？\n真无聊…\n',(5,0):'你这家伙，果然烦死了…\n好啊，我这就认真把你砸个稀烂！\n',(6,0):'烦死了…你烦死了！！\n别来碍事！！\n',(7,0):'可恶…我…我！！\n'},
}
def color(t):return '{F2 01 03 01}'+t+'{F2 01 01 01}'
for s in ['export_base/event/e900/e999_010.bf.json','export_base/event/e900/e999_111.bf.json']:
    SOURCES[s].update({(1,0):'触摸选择钢笔工具，\n就可以'+color('画出墙壁的线条')+'。\n',(2,0):'画笔工具可以'+color('为地板涂色')+'。\n',(4,0):'橡皮擦工具用于线条，\n抹布工具用于地板，都能'+color('擦除')+'。\n',(5,0):'紫色图标表示'+color('通常状态')+'。\n红色图标表示'+color('追踪状态，非常危险')+'。\n',(6,0):'蓝色表示安全状态{F2 01 01 01}，随后会逐渐变为\n绿色、黄色，'+color('红色则表示危险状态')+'。\n',(7,0):'迷宫中存在这样的'+color('捷径')+'。\n请善用专用的捷径图标。\n',(10,0):'触摸并拖动图标，\n就可以'+color('将其放到地图上')+'。\n',(11,0):'“Ｃｏｌｏｒ”调色板也可以'+color('更改颜色')+'。\n',(12,0):'此外，操作出错时，可以按'+color('“ＵＮＤＯ”按钮')+'\n'+color('撤销')+'操作。\n',(13,0):'放置的图标，\n'+color('拖到垃圾桶上就能删除')+'。\n'})
for i,t in [(0,'追击'),(1,'总攻击')]:
    s='export_base/battle/event/all_attack_help.bf.json'
    SOURCES[s][i,0]=SOURCES[s][i,0].replace(t,color(t))
SOURCES['export_base/battle/event/boss001.bf.json'][0,0]='吾乃影…真正的我…\n'
def main():
    p=ROOT/'translation/batches/445_map_battle_prompts.generated.json';assert not p.exists()
    cat={r['key']:r for r in read(ROOT/'translation/catalog.working.json')};sources={};hashes={}
    for s,texts in SOURCES.items():
        d=read(ROOT/s);rows=[]
        for (i,j),body in texts.items():
            r=cat[f'{s}:{i}:{j}'];assert not r.get('translation');old=r['original']
            if s=='export_base/battle/event/boss001.bf.json':
                from prepare_sklcard_428 import replace_slots
                full=replace_slots(old,body)
                pre=LEADING.match(old).group();suf=TRAILING.search(old).group();body=full[len(pre):len(full)-len(suf)]
            else:full=LEADING.match(old).group()+body+TRAILING.search(old).group()
            assert TOKEN.findall(full)==TOKEN.findall(old),(s,i,j)
            a=TOKEN.sub('',old).splitlines();b=TOKEN.sub('',full).splitlines()
            assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),(s,i,j)
            rows.append([i,j,d['texts'][i]['id'],body])
        sources[s]=rows;hashes[s]=hashlib.sha256((ROOT/s).read_bytes()).hexdigest()
    write(p,dict(status='draft',sources=sources,source_hashes=hashes,review_notes=['补齐两份地图操作说明、玲单独行动方向反馈、追击/总攻击说明及旧版boss001台词；明确的角色台词测试标记不修改。','地图中的Color/UNDO保留屏幕按钮原标签便于对应；两份地图原文一致，使用同一译文。']))
    print('Pages:',sum(map(len,sources.values())))
if __name__=='__main__':main()
