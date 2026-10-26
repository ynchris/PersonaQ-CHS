"""Translate the complete remaining poem viewer, preserving timed control runs."""
import hashlib,re
from collections import defaultdict
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING

# Exact text segments between timing commands. Whitespace is retained separately.
PAIRS='''「キミにトラベル」|「向你启程」
「ティータイム・ファンタジー」|「茶会幻想」
「孤独な闘争者」|「孤独的斗士」
「続・|「续·
「Ｄｅａｒ|「亲爱的
Ｍｙ　Ｔｅａｃｈｅｒ」|老师」
「ＰＡＮＤＯＲＡ」|「潘多拉」
あと何秒かな？|还要几秒呢？
うつくしや|真美啊
おとめ座で眠りにつくの|在室女座安然入睡
お出ましだ！|登场了！
お祭りの|祭典上
その口で喚ぶがいい！|就亲口呼唤吧！
それが彼女の傷ついた翼の名！|那是她受伤羽翼的名字！
それは咆哮となり|它将化作咆哮
たったひとつの|那唯一的
だけど|可是
どこにあるの？|在哪里呢？
なんだろう？|是什么来着？
ひとり、またひとりと|一个，又一个
ひとりぽっちの解放者|孤身一人的解放者
まぶたをそっと閉じて|轻轻合上双眼
やがて漆黒の彼方から|终将从漆黑的彼方
アタシがアタシじゃないみたい|我仿佛已不再是自己
アタシの魔法|我的魔法
アタシは解放者|我是解放者
オアシスでブランチを|在绿洲享用早午餐
ガラスのクツは持っていて|请拿好那双水晶鞋
キットキミハ|你一定会
キミとのキョリの方程式|与你之间距离的方程式
キミのイニシャルを描きました|写下了你姓名的首字母
キミの分だけスパイシーでした|唯独你的那杯辛香四溢
キミを振り向かせるリモコン|能让你回头看我的遥控器
キミ行きの|通往你的
サバンナで待ち合わせたら|相约在大草原碰面
タカナルコドウ・・・|怦然的心跳……
デザートには|以一支
世界を覆い尽くしているのに|明明已将世界尽数淹没
今すぐ誓ってよ|现在就许下誓言吧
今日にＡＤＩＯＳ・・・|向今天道一声再见……
仮面の嗤いの中で|与面具后的嘲笑中
偽善のセカイでもがきつつ|在伪善的世界里挣扎
只管に無垢であらんとする|一心想要保持纯洁
夕陽を見ると|每当望着夕阳
夢物語はもうおしまい|这场美梦便已结束
孤独な闘争者の|孤独的斗士
孤高の闘争者の|孤高的斗士
寄ってらっしゃい　見てらっしゃい！|快过来呀　快来看呀！
審判の刻が訪れる|迎来审判的时刻
小さな裸足は傷だらけ|赤裸的小脚遍布伤痕
彼女の名を知っているかい？|你可知道她的名字？
彼女は偽の優しさと|她是否会在虚假的温柔
彼女は飛び立つ！|她将展翅飞翔！
掲げた灯火を受け継ぐ者が|继承她高举灯火的人们
教えてほしいな|希望你能教教我
月と星が出逢ったら|当月亮与星星相遇
汚れた大地を震わすだろう！|令污秽的大地为之震颤！
溢れそうだよ|就快满溢而出
無垢なる笑みを浮かべてる！|却仍绽放着纯真的笑容！
砂糖菓子みたいに|如同糖果一般的
祝福のトロイメライが鳴り響く|祝福的梦幻曲随之奏响
立ち上がる|挺身而出
絶望のうちに息絶えるのだろうか|在绝望之中断绝气息
聞こえない？|听不见吗？
自由|自由
虚栄を砕き|粉碎虚荣
虚飾で塗り固めて|用虚饰层层涂抹
虚飾で満足してる！|竟满足于这份虚饰！
虚飾のココロを|那颗虚饰的心
裸足でキミにチェックイン|赤着脚入住你的心里
遠くへ！|飞向远方！
開けてあげるわ　パンドラの箱を！|让我来打开吧　潘多拉的魔盒！
鳥籠の中の少女に　注目！|看呀　鸟笼之中的少女！
（Here comes the judgement time）|（审判时刻已然来临）
１２時の鐘が鳴り響いたら|当１２点的钟声响起
３，|３，
Ｂｌｏｏｄ|血色的
Ｂｌｏｏｄ　Ｂｌａｃｋ|血色的　黑
Ｂｌｏｏｄ　Ｂｌａｃｋ　Ｒｏｓｅｓ・・・|血色的　黑蔷薇……
Ｊｅｔ’ａｉｍｅ・・・|我爱你……
Ｌａｄｉｅｓ＆Ｇｅｎｔｌｅｍｅｎ！|女士们、先生们！
Ｐｌｅａｓｅ，|拜托，
Ｒｏｓｅｓ，|蔷薇，
ＳＩ|真
Ｎ|
ＪＩ|实
ＴＵ・・・|……
Ｔｅａｃｈ　Ｍｅ・・・|请教教我……
Ｗｈｉｔｅ|白
Ｗｈｉｔｅ　Ｒｏｓｅｓ，|白蔷薇，
ああうつくしや|啊，多么美
おふたりさん|你们二位
きら星のしっぽをユビワにして|用闪耀星辰的尾巴做成戒指
そう、|没错，
その名は|她名为
どうしてなの？|为什么呢？
キミがセンセイだったら|如果你是老师
キミに落ちるまで|才会彻底爱上你
コイニオチルヨ・・・|坠入爱河……
ゴッツァンデス・・・|多谢款待……
ソノイノチ、|你的性命，
テオドア|西奥多
ドウシテ？|为什么呢？
ヒトイキにキミを飲み干したら|若将你一口饮尽
ホントに教えてほしいのは|真正想请你告诉我的
ホントウってやつを|何谓真实
ミルクティーにシナモンで|用肉桂在奶茶上
モライウケル・・・|我收下了……
五月の風が運んでくれたの|五月的风捎来了
円舞を踊って|圆舞曲作甜点
切|车
否！|不！
嘆きの涙が|叹息的泪水
嘆きの詩を捧げよ！|献上哀叹的诗歌吧！
堕天使の詩」|堕天使之诗」
堕天使は煉獄に降り立った|堕天使降临于炼狱
悲しみの唄が|悲伤的歌声
教えてあげるわ|让我来教你吧
新世界|新世界
林檎飴|苹果糖
果てなき高みへ！|飞向无尽的高处！
泣きたくなるよ|就忍不住想哭
温かいのに|明明都很温暖
湯気が沁みるのは・・・|热气熏得眼眶发酸……
無慈悲な嘘にまみれて|浑身沾满无情的谎言
片翼を引きずり|拖着一侧羽翼
現れくるのは|将出现的是
符|票
終焉を統べる彼女の名を|统御终焉的她的名字
羽根のベッドにＩＮしたら|钻进羽毛床里
胸の|胸中的
花火に溶ける|融入烟花中
見えない？|看不见吗？
誰のせいなの？|究竟该怪谁？
通じるカナ・・・|能奏效吗……
銀河エアラインが迎えに来たら|银河航空前来迎接时
！|！
１・・・|１……
２，|２，
Ｂｌａｃｋ|黑
ＤＯＫＩ×２と|心跳×２与
Ｒｏｓｅｓ・・・|蔷薇……
Ｔｈａｎｋ　Ｙｏｕ・・・|谢谢大家……
ＹＥＳ，Ｓｉｒ・・・|是，老师……
さあさあ|来呀来呀'''
SEG=dict(line.split('|',1) for line in PAIRS.splitlines())
CAMP={
 (0,0):'＞要感受哪种激情呢……\n',(1,0):'＞现在什么也感受不到……\n',
 (2,0):'“潘多拉”',(2,1):'“亲爱的老师”',(2,2):'“孤独的斗士”',(2,3):'“续·堕天使之诗”',
 (3,0):'“向你启程”',(3,1):'“茶会幻想”',(3,2):'“西奥多的得意之句”',(3,3):'“西奥多的倾力之句”',
 (4,0):'“黑暗与蔷薇”　真田明彦',(4,1):'“黑暗与蔷薇”　里中千枝',
 (4,2):'“黑暗与蔷薇”　天城雪子',(4,3):'“黑暗与蔷薇”　白钟直斗',
 **{(i,j):text for i in (2,3,4) for j,text in ((8,'下页'),(9,'返回'))}}

def main():
    target=ROOT/'translation/batches/413_poem_viewer.generated.json';assert not target.exists()
    sources=defaultdict(list)
    for r in read(ROOT/'translation/catalog.working.json'):
        if r.get('translation'):continue
        s=r['source'];i=r['message_index'];j=r['line_index'];old=r['original']
        if s=='export_base/camp/cmppoem.bf.json':
            if (i,j) not in CAMP:continue
            body=CAMP[i,j]
        elif s=='export_base/event/msg_POEM.bmd.json':
            if not TOKEN.sub('',old).strip():continue
            parts=re.split('('+TOKEN.pattern+')',old)
            for n in range(0,len(parts),2):
                raw=parts[n];key=raw.strip()
                if not key:continue
                assert key in SEG,(i,j,repr(key))
                parts[n]=raw[:len(raw)-len(raw.lstrip())]+SEG[key]+raw[len(raw.rstrip()):]
            body=TRAILING.sub('',LEADING.sub('',''.join(parts)))
        else:continue
        full=LEADING.match(old).group()+body+TRAILING.search(old).group()
        assert TOKEN.findall(full)==TOKEN.findall(old)
        a=TOKEN.sub('',old).splitlines();b=TOKEN.sub('',full).splitlines()
        assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),(i,j,a,b)
        mid=read(ROOT/s)['texts'][i]['id'];sources[s].append([i,j,mid,body])
    total=sum(map(len,sources.values()));assert total==81,total
    write(target,dict(status='draft',sources=dict(sources),source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},review_notes=['补齐诗歌鉴赏菜单20页及正文61页；保留12个问号选项与5页纯空白。','按原始时序控制码间的文字段翻译，保留逐字、换行和空白；激情/黑暗与蔷薇沿用既有剧情译法。','暂无游戏内朗读同步与排版验证；菜单是否启用需实测。']))
    print('Poem viewer pages:',total)

if __name__=='__main__':main()
