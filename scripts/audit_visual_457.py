"""Record human visual inspection of all 46 exported tutorial images.

No pixels, executable or installer are changed. Source hashes bind observations.
"""
import hashlib
from compile_translation import ROOT, write

TUTORIALS={
1:('english_ui','战斗截图：英文指令、帮助；与最终菜单风格保持一致'),
2:('japanese','角色与副人格面具的HP/SP标签'),
3:('japanese','开发占位字“仮”；不能当成正式界面示例，另审替换截图'),
4:('japanese','技能名称、5回合暴击率说明、强化/全体/返回'),
5:('english_ui','战斗截图：英文指令与按钮说明'),
6:('japanese','异常优先级、无法战斗、诅咒等标签'),
7:('japanese','敌人名称；截图内固定文字'),
8:('japanese','敌人名称；截图内固定文字'),
9:('english_ui','埃癸斯特殊指令示意；与最终指令名称保持一致'),
10:('japanese','狂欢模式状态标签'),
11:('japanese','过热状态标签'),
12:('japanese','过热状态标签'),
13:('japanese','地图标题及缩放示意中的日文迷宫标志'),
14:('japanese','绘图面板截图中的迷宫标志'),
15:('english_ui','绘图操作截图：Color等英文按钮'),
16:('japanese','图标选择截图中的迷宫标志'),
17:('japanese','画笔/橡皮截图中的迷宫标志'),
18:('no_text_observed','玩家朝向与图标示意，未见需翻译文字'),
19:('no_text_observed','危险度四色图标，未见需翻译文字'),
20:('japanese','地图弹出标签“抜け道”应与捷径术语一致'),
21:('japanese','地图完成度截图中的迷宫标志'),
22:('japanese','委托列表、任务名、目标和报酬截图'),
23:('japanese','P4路线菜单底部副人格面具召唤/登录说明'),
24:('japanese','P3路线同类菜单说明，非同一截图'),
25:('japanese','系统菜单：委托、教程、设置、读取、返回标题'),
26:('japanese','委托详情、任务名、报酬和详细帮助'),
27:('japanese','委托提示弹窗及后面的委托详情'),
28:('english_ui','P3战斗指令截图'),
29:('japanese','P3角色与副人格面具HP/SP标签'),
30:('japanese','技能名称、3回合攻击提升说明及按钮'),
31:('english_ui','P3战斗指令截图'),
32:('japanese','敌人名称；P3路线截图'),
33:('japanese','敌人名称；P3路线截图'),
34:('japanese','属性效果表：日文字形及属性术语'),
35:('japanese','异常效果表：诅咒、混乱及三种封印标签'),
36:('japanese','能力提升表：运、命中率、暴击率等'),
37:('japanese','范围攻击、贯通、扩散标签'),
38:('japanese','方角固定/视野方向固定及地图标志'),
39:('japanese','自动行走截图的地图标志'),
40:('japanese','调色截图的地图标志'),
41:('japanese','绘图模式截图的地图标志'),
42:('japanese','删除图标截图的地图标志'),
43:('japanese','移动说明：L/R键平移、方向键上下前进/后退、左右转向'),
44:('japanese','B键组合的快速移动及环视说明'),
45:('english_ui','场景截图仅见View按键说明'),
46:('english_ui','地图局部仅见Color等英文；无需假定没有文字'),
}
SHEETS={
'event/skip_btn.spr3.00.png':{'バックログ':'对话回顾','ウィンドウ消去':'隐藏窗口','高速SKIP':'快速跳过','Aボタン':'A键'},
'facility/velvet.spr3.00.png':{'ペルソナ切替':'切换人格面具','表示切替':'切换显示','全書登録済':'已登录全书','スキルヘルプ':'技能说明','ページ切替':'切换页面','手帳切替':'切换手册','召喚':'召唤','保護':'保护','消去':'删除','登録':'登录','選択':'选择','メニュー':'菜单'},
'facility/party.spr3.00.png':{'外す':'卸下','ステータス':'状态','ボイス変更':'切换语音','消去':'删除','現在のナビ設定':'当前导航设置','戦闘':'战斗','迷宮':'迷宫'},
'title/dlc.spr3.00.png':{'残高':'余额','必要ブロック数':'所需空间','ブロック':'区块','価格':'价格','購入済み':'已购买','受信済み':'已接收','受信可能':'可接收'},
'camp/c_sub.spr3.00.png':{'メニュー':'菜单'},
'memcard/save_load.spr3.00.png':{'スロット切替':'切换存档槽','決定':'确定'},
}
ARCANA={'愚者':'愚者','魔術師':'魔术师','女教皇':'女教皇','女帝':'女帝','皇帝':'皇帝','法王':'教皇','恋愛':'恋爱','戦車':'战车','正義':'正义','隠者':'隐者','運命':'命运','剛毅':'刚毅','刑死者':'倒悬者','死神':'死神','節制':'节制','悪魔':'恶魔','塔':'塔','星':'星','月':'月','太陽':'太阳','審判':'审判','世界':'世界'}

def main():
    rows=[]
    for n,(status,note) in TUTORIALS.items():
        p=ROOT/f'export_base/tutorial/t{n:03d}.ctpk.00.png'
        rows.append(dict(source=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),visual_status=status,note=note,edited=False))
    sheets=[]
    for source,phrases in SHEETS.items():
        p=ROOT/'export_base'/source
        sheets.append(dict(source=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),phrases=phrases,
                           edited=False,coverage='Visible labels only; sprite rectangles, alternate states and transparency still need review.'))
    codes=[]
    # Discovery only: short strings may have unrelated matches. No replacement.
    for source in ['exefs/code.bin','update/exefs/code.bin']:
        raw=(ROOT/source).read_bytes(); labels=[]
        for jp,cn in ARCANA.items():
            needle=b'\0'+jp.encode('cp932')+b'\0'; positions=[]; pos=raw.find(needle)
            while pos>=0:
                positions.append(pos+1); pos=raw.find(needle,pos+1)
            labels.append(dict(original=jp,proposed_translation=cn,exact_nul_bounded_candidates=positions,status='needs_reference_and_overlap_review'))
        codes.append(dict(source=source,sha256=hashlib.sha256(raw).hexdigest(),labels=labels))
    write(ROOT/'translation/visual_457.review.json',dict(tutorials=rows,sheets=sheets,arcana_code_candidates=codes,
       packaged=False,notes=['All 46 exported tutorial images visually inspected, not all game tutorials proven exported.',
       'No images modified. English labels need a consistent policy; no_text_observed is not a global exemption.',
       'Arcana program strings now confirmed in both versions; sprite metadata alone does not prove visible card labels.',
       'Proposed phrases need size and terminology checks before editing assets.']))
    from collections import Counter
    print('Tutorials',dict(Counter(r['visual_status'] for r in rows)),'UI sheets',len(sheets))
    print('Arcana candidate counts',[(f['source'],sum(bool(r['exact_nul_bounded_candidates']) for r in f['labels'])) for f in codes])

if __name__=='__main__':main()
