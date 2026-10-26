"""School-walk event titles, with reserved entries preserved byte-for-byte."""
import hashlib
import sys
from compile_translation import ROOT,read,write
from q2_name_banks import parse,build_bank

SOURCE='attraction/schwalkname.tbl'
DRAFT=ROOT/'translation/schoolwalk_names.review.json'
TEXT={1:'关于他们的能力（１）',2:'关于他们的能力（２）',3:'关于他们的能力（３）',4:'该怎么称呼彼此？',5:'为什么是联谊咖啡厅？',6:'导航能力的不同',7:'所谓联谊啊……',8:'揭开小熊的秘密！',9:'想来点意外走光',10:'月高男生里喜欢谁？',11:'感觉到了守卫的气息',12:'我们也想参加女装比赛',21:'结婚是什么',22:'那首诗是谁写的？',23:'鬼屋就免了！',24:'这也太吓人了吧！',25:'在意那只蜘蛛',26:'揭开荒垣的秘密！',27:'伊织顺平时间筹备中',28:'向往社团活动',29:'与现实八十神高中的共通点',30:'伊织顺平时间到了',31:'废弃医院真的不行！',32:'女生亲手做饭是都市传说',33:'２年后会变成什么样？',34:'玲，做得很好',35:'又感觉到了守卫的气息',41:'正经的迷宫真无聊',42:'担心由加莉',43:'建造这所学校的是……',44:'为什么要举办祭典？',45:'想要眼镜！',46:'女生聚会热闹非凡',47:'房间主人的必要性',48:'想鼓起勇气的由加莉',49:'那场忍耐比赛我没输！',50:'女生的友情坚不可摧',51:'两个男人反省了',52:'回去后要做什么？',53:'最后的守卫',61:'一定要救出玲！',62:'恢复力量的善',63:'为何是钟楼？为何是蜘蛛？',64:'袖手旁观的住民们',65:'大家为我做的',66:'气氛好沉重……',67:'登上塔顶吧！',68:'想快一点，却不能着急',69:'真田与荒垣的无情对决',70:'桐条学姐，太依赖别人了',71:'顺平，你真帅',72:'想吃叶隐拉面！',73:'迷宫与文化祭节目的关联',74:'天田鼓起勇气',75:'即使回到原来的地方',76:'请多关照，新搭档！',77:'钟楼实在太难熬了',78:'我们还在成长中',79:'聚会暂且延期',80:'庆功宴可不会输',81:'善的决心',107:'在意天田的完二',108:'阳介是王子？',109:'怎么钻进电视里？',110:'小熊ＶＳ虎狼丸第２回合',112:'八高男生的恋爱情况',113:'被美鹤打动的直斗',122:'这就是联谊必胜法',124:'这也太吓人了吧',127:'只有狗能看见的东西',129:'本来能做得更好……',131:'厕所带来的心理阴影',132:'吐槽对决的结果',142:'听不懂完二的话',144:'为什么在举办祭典？',145:'大家一起去祭典吧！',146:'埃癸斯的叫醒服务',147:'不愿回想的桑拿',148:'真田和千枝的共通点',149:'试着当老师',150:'２年前反而更先进？',151:'发现绝佳的研究材料！',152:'哪边的伤害更高？',165:'谁都不是独自活着',169:'因为是个笨蛋嘛！',170:'想和你一起改变',172:'小熊ＶＳ虎狼丸最终章',175:'这一定也是命运',176:'伙伴让我改变',177:'心怀新的羁绊',201:'来吧，以物易物对决！',202:'联谊咖啡厅的奇怪之处',203:'开始代人搭讪了',204:'阻止女生们失控',205:'放学后的恶灵俱乐部药剂室',206:'礼物大作战',207:'稻羽乡土展的短褂',208:'传达吧，这份心意',209:'紧急特别授课',210:'一日老师体验',211:'善凝视的原因',212:'目标是羔羊人偶',213:'得到羔羊人偶的人',214:'与西奥多逛文化祭',215:'与玛丽逛文化祭',216:'护航步步升级'}

def prepare():
    assert not DRAFT.exists()
    TEXT[9]='想露一点出来'
    data=(ROOT/'data'/SOURCE).read_bytes()
    names=[c[:-1].decode('cp932') for c in parse(data,217)]
    by_original={names[i]:t for i,t in TEXT.items()}
    rows=[];retained=[]
    for i,name in enumerate(names):
        if 'バッファ' in name or 'ダミー' in name:retained.append(dict(index=i,original=name));continue
        assert name in by_original,(i,name)
        rows.append(dict(index=i,original=name,translation=by_original[name]))
    write(DRAFT,dict(source=SOURCE,source_sha256=hashlib.sha256(data).hexdigest(),count=217,rows=rows,retained=retained,runtime_tested=False))
    print('School-walk titles:',len(rows),'retained:',len(retained))

def load():
    draft=read(DRAFT);data=(ROOT/'data'/SOURCE).read_bytes()
    assert hashlib.sha256(data).hexdigest()==draft['source_sha256']
    chunks=parse(data,217);seen=set()
    for r in draft['rows']:
        i=r['index'];assert i not in seen and chunks[i][:-1].decode('cp932')==r['original'];seen.add(i)
        assert 'バッファ' not in r['original'] and 'ダミー' not in r['original']
    assert seen|{r['index'] for r in draft['retained']}==set(range(217))
    from terminology_459 import apply as apply_terminology
    for row in draft['rows']:
        row['translation']=apply_terminology('schoolwalk',row['index'],row['translation'])
    return draft

def build():
    draft=load();enc=ROOT/'translation/font_encoding.hex.json'
    result=build_bank((ROOT/'data'/SOURCE).read_bytes(),217,draft['rows'],read(enc))
    target=ROOT/'full_work/schoolwalk_payload'/SOURCE
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(result)
    write(ROOT/'translation/schoolwalk_build.generated.json',dict(source=SOURCE,source_sha256=draft['source_sha256'],draft_sha256=hashlib.sha256(DRAFT.read_bytes()).hexdigest(),encoding_sha256=hashlib.sha256(enc.read_bytes()).hexdigest(),sha256=hashlib.sha256(result).hexdigest(),rows=len(draft['rows']),roundtrip_verified=True,unselected_bytes_preserved=True,runtime_tested=False))
    print('School-walk bank roundtrip verified:',len(draft['rows']))

if __name__=='__main__':prepare() if sys.argv[1:]==['prepare'] else build()
