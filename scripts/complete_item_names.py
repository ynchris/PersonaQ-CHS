"""Complete remaining display item names; preserve structural/internal slots."""
from compile_translation import ROOT,read,write
from equipment_names import load_drafts,EXPECTED_SHA
from q2_item_names import load as item_names
from q2_name_banks import load as banks,excluded

DRAFT=ROOT/'translation/item_names_completion.review.json'
TEXT={1537:'空白卡片',1538:'空白卡片',1539:'空白卡片',1540:'洒水壶',1541:'北栋钥匙',1542:'实习栋钥匙',1543:'南栋钥匙',1544:'黑暗钥匙',1545:'红色门禁卡',1546:'黄色门禁卡',1547:'蓝色门禁卡',1548:'火把',1549:'黑色兜裆布',1550:'玩偶',1551:'玩具戒指',1552:'一缕头发',1553:'留言卡片',1554:'皮封面笔记本',1555:'小门钥匙',1560:'空白卡片',1561:'空白卡片',1562:'理科准备室钥匙',1563:'白玫瑰',1564:'心形标记',1565:'注射器',1566:'扭绳头巾',1567:'多余的齿轮',1601:'残破的福音书',1686:'招魔雌竹',1712:'白色绒球',1713:'箭的样品',1714:'迷情药',1715:'地狱奶嘴',1716:'泻药',1717:'伊丽莎白的便条',1718:'男子汉印花短褂',1719:'不祥的钥匙',1720:'陈旧的手表',1721:'西奥多６６号',1722:'快坏掉的钥匙',1723:'冰之钥匙',1724:'扯断的锁链',1725:'黄色珠子',1726:'粉色珠子',1727:'黑色珠子',1728:'红色珠子',1729:'绯红脚环',1730:'石龙子的翅膀',1731:'天甜酒',1732:'祝福腰布',1735:'迷途羔羊人偶',1739:'会员证',1740:'阿达玛斯书签',1741:'白花发饰',1742:'黏糊糊的东西',1743:'浓眉毛',1744:'赎罪羔羊',1745:'脱线的赎罪羔羊',
1804:'银桌的餐具',1810:'大鹫的钩爪',1825:'甲虫壳',1851:'巫师的戒指',1857:'狂圣母的底座',1863:'封印的大蛇皮',1866:'银蛇的鳞片',1878:'岩石块',1884:'国王的王冠',1885:'财宝碎片',1948:'诅咒的监视者眼',1991:'老翁的拐杖',2031:'黑色兜裆布',2163:'残破的福音书',2304:'八岐大蛇之尾',2305:'皮克希的翅膀',2306:'玄武的甲壳',2307:'朱雀的羽毛',2308:'黑色灯笼',2309:'魔灯碎片',2310:'白虎之爪',2311:'王的雪球',2312:'魅惑信息素',2313:'鵺之爪',2314:'斯卡蒂的弓片',2315:'斗牛士的刺剑',2316:'青龙的鳞片',2317:'库柏勒的头发',2318:'铁棒碎片',2319:'雷帝的蓝铠碎片',2329:'不祥的獠牙',2335:'折断的魔枪',2337:'蝇王的杖片',2529:'招魔雌竹',2893:'治愈神风'}

def main():
    assert not DRAFT.exists()
    TEXT.update({2313:'奴延之爪',2314:'丝卡蒂的弓片'})
    _,_,names,equipment=load_drafts();existing=item_names()
    group=next(g for g in banks()['groups'] if g['source']=='battle/table/skillnametable.tbl')
    skills={r['original']:r for r in group['rows']}
    rows=[];retained=[]
    for i in range(1536,3328):
        if i in existing:continue
        name=names[i]
        if excluded(name) or name.endswith('開始') or name.startswith('条件つき') or i in {1733,3156}:
            retained.append(dict(index=i,original=name,reason='placeholder_or_internal'));continue
        ref=skills.get(name) if i>=2560 else None
        value=ref['translation'] if ref else TEXT.get(i)
        assert value is not None,(i,name)
        rows.append(dict(index=i,original=name,translation=value,skill_index=ref['index'] if ref else None))
    write(DRAFT,dict(source='init/itemtbl.bin',source_sha256=EXPECTED_SHA,rows=rows,retained=retained,runtime_tested=False))
    print('Additional names:',len(rows),'unique:',len({r['original'] for r in rows}))

if __name__=='__main__':main()
