"""Review exact PQ1 strings in both code versions; never mutate executables."""
import hashlib,re,sys
from compile_translation import ROOT,read,write
from prepare_tables_449 import T as TABLE
T={k:v for k,v in TABLE.items() if k not in {'の数','はい','いいえ','やめる'}}
T.update({'%s属性の武器で遠隔攻撃をする':'用%s属性武器进行远程攻击','%s属性の武器で近接攻撃をする':'用%s属性武器进行近战攻击','どのデータをロードしますか？':'要读取哪个存档？','どれにセーブしますか？':'要保存到哪里？','買えるものがありません':'没有可购买的物品','素材を全部売る':'出售全部素材','依頼の確認をします':'查看委托','所持アイテム数':'持有道具数','装備できるペルソナがいません':'没有可装备的人格面具','サブペルソナ所持数':'副人格面具持有数','ペルソナ登録率':'人格面具登录率','思いだしたいスキルを選んでください':'请选择要回忆的技能','このアイテムを捨てますか？':'要丢弃这件道具吗？','装備できる防具がありません':'没有可装备的防具','装備できるものがありません':'没有可装备的物品','サブペルソナを装備していません':'未装备副人格面具','預けた数':'寄存数','これ以上アイテムを所持できません':'无法携带更多道具','捨てるアイテムを選んでください':'请选择要丢弃的道具','アイテム預かり枠':'道具寄存栏位','これ以上ペルソナを所持できません':'无法持有更多人格面具','消滅させるペルソナを選んでください':'请选择要消除的人格面具','ベルベットルームの住人たち':'天鹅绒房间的住民们','%sの脚':'%s的脚','シャドウの群れ':'阴影群','難易度をお選びください':'请选择难度','玲に分け与えていた能力':'分给玲的能力','よろしくおねがいします':'请多关照','隊列を変更する':'改变队列','所持しているアイテムを使用する':'使用持有的道具','リーダースキルを使用する':'使用队长技能','アイギスのリミッターを解除する':'解除埃癸斯的限制器','敵の攻撃に備えて防御する':'防御以应对敌人的攻击','戦闘からの離脱を試みる':'尝试脱离战斗','迷宮深部から再開する':'从迷宫深处继续','最終到達階から始める':'从最深到达层开始','入り口から始める':'从入口开始','ブロックマーク':'方块标记','星マーク':'星形标记','はてなマーク':'问号标记','丸マーク':'圆形标记','びっくりマーク':'叹号标记','スタート地点':'起点','パワースポット':'能量点','イベント':'事件','下り階段':'下行楼梯','上り階段':'上行楼梯','メモ':'备注','抜け道':'捷径','ギミック壁':'机关墙','閉じた扉':'关闭的门','ヤソガミコウコウ':'八十神高中','ごーこんきっさ ゴールイン':'联谊咖啡厅 终点','不思議の国のアナタ 最終章':'不可思议之国的你 最终章','時計塔 最終階':'钟楼 顶层','稲羽郷土展 最終夜':'稻羽乡土展 最终夜','放課後悪霊クラブ 最終怪':'放学后恶灵俱乐部 最终怪',
'聡明そうな少女 ':'聪慧的少女 ','明るい少年':'开朗的少年','落ち着いた少年':'沉稳的少年','イヤフォンの少年':'戴耳机的少年','半ズボンの少年':'穿短裤的少年','アイギス':'埃癸斯','髪の長い少女':'长发少女','勝ち気そうな少女':'好强的少女','活発そうな少女':'活泼的少女','聡明そうな少女':'聪慧的少女','伊織':'伊织','伊織 順平':'伊织 顺平','白鐘':'白钟','白鐘 直斗':'白钟 直斗','真田 明彦':'真田 明彦','荒垣 真次郎':'荒垣 真次郎','天城 雪子':'天城 雪子','クマ':'小熊','里中 千枝':'里中 千枝','コロマル':'虎狼丸','天田 乾':'天田 乾','久慈川 りせ':'久慈川 理世','山岸 風花':'山岸 风花','桐条 美鶴':'桐条 美鹤','善と玲':'善与玲','岳羽 ゆかり':'岳羽 由加莉','花村 陽介':'花村 阳介','巽 完二':'巽 完二','テオドア':'迪奥多','エリザベス':'伊丽莎白','マリー':'玛丽','マーガレット':'玛格丽特','堂島 菜々子':'堂岛 菜菜子','マガツイザナギ':'祸津伊邪那岐','タナトス':'塔纳托斯','カグヤ':'辉夜','オルフェウス・改':'俄耳甫斯・改'})
SHORT={'はい':'是','いいえ':'否','やめる':'取消','戻る':'返回','外す':'卸下'}
# Single-character matches also occur inside machine instructions and numeric data.
# Only these independently inspected rodata offsets may be changed.
ATTRIBUTES=[('斬','斩',0x3d8cfd,0x3e975f),('雷撃','雷击',0x3d8d00,0x3e9762),('氷結','冰结',0x3d8d0a,0x3e976c),('疾風','疾风',0x3d8d0f,0x3e9771),('壊','坏',0x3d8dad,0x3e980f),('矢印','箭头',0x3d9f91,0x3eaa60),('気','气',0x3d9978,0x3ea40e),('氷','冰',0x3d997f,0x3ea415),('運','运',0x3d9982,0x3ea418),('痺','痹',0x3d9997,0x3ea42d),('頭','头',0x3d999a,0x3ea430),('闇','暗',0x3d99a0,0x3ea436),('呪','咒',0x3d99b2,0x3ea448)]
T.update(SHORT);T['オルフェウス・改']='俄耳甫斯·改'
for n in '１２３４５６７８９':T[f'時計塔 {n}階']=f'钟楼 {n}层'
for n in '１２３':T[f'不思議の国のアナタ 第{n}章']=f'不可思议之国的你 第{n}章'
for n in '１２３４':T[f'ごーこんきっさ {n}次会']=f'联谊咖啡厅 第{n}场'
for n in '一二三四':T[f'稲羽郷土展 第{n}夜']=f'稻羽乡土展 第{n}夜'
for jp,cn in [('壱','一'),('弐','二'),('参','三'),('四','四')]:T[f'放課後悪霊クラブ {jp}ノ怪']=f'放学后恶灵俱乐部 第{cn}怪'

def main():
    p=ROOT/'translation/code_ui_450.review.json';assert not p.exists() or '--refresh' in sys.argv;files=[]
    for source in ['exefs/code.bin','update/exefs/code.bin']:
        raw=(ROOT/source).read_bytes();rows=[]
        for jp,cn in T.items():
            needle=jp.encode('cp932')+b'\0';pos=raw.find(needle)
            while pos>=0:
                # Long embedded strings in text code are accepted only at word alignment;
                # packed rodata strings have a preceding terminator.
                if (pos and raw[pos-1]==0) or (pos%4==0 and (len(needle)>=13 or jp in SHORT)):
                    rows.append(dict(offset=pos,capacity_bytes=len(needle)-1,original=jp,translation=cn))
                pos=raw.find(needle,pos+len(needle))
        for jp,cn,base,update in ATTRIBUTES:
            pos=base if source=='exefs/code.bin' else update
            needle=jp.encode('cp932')
            assert raw[pos-1:pos+len(needle)+1]==b'\0'+needle+b'\0'
            rows.append(dict(offset=pos,capacity_bytes=len(needle),original=jp,translation=cn))
        rows.sort(key=lambda r:r['offset'])
        for a,b in zip(rows,rows[1:]):assert a['offset']+a['capacity_bytes']<b['offset'],(a,b)
        files.append(dict(source=source,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),rows=rows))
    write(p,dict(files=files,review_notes=['分别在PQ1本体与更新code.bin定位已审阅菜单、角色、地图和战斗字符串；不套用Q2地址、不修改原文件。','限原字符串容量，不移动数据、不改变代码指令或指针；一般字符串要求NUL边界，较长UI串及已审阅SHORT允许字对齐；单字属性仅用逐版确认的固定地址，禁止全局替换。','仍需检查字节容量、实际显示字体及运行时兼容；不包含输入法字表、随机姓名字库、QR库诊断和无法确认的机器码候选。']))
    print([(f['source'],len(f['rows'])) for f in files])
if __name__=='__main__':main()
