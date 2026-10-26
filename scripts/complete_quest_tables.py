"""Finish quest titles and usable facility help, retaining legacy/debug rows."""
from compile_translation import ROOT,read,write
from raw_text_codec import encode_display

QUEST={1:'击败扑克牌士兵',2:'帮忙参加以物易物对决',3:'取得箭的样品',4:'抓住偷食物的贼',5:'查明传闻的真假',10:'小试身手的时间到了',11:'我也想玩',12:'来吧，与阴影过招',13:'解开音乐教室之谜',15:'救救我的胃！',18:'取得邪眼',19:'创造獬豸',20:'帮我拿泻药',21:'一试身手的时间到了',22:'想传达秘密留言',23:'请为我们护航',24:'虎狼丸的散步时间',25:'问问善想要什么！',26:'分享祭典的气氛',27:'给善做项圈吧！',28:'装满阴影的宝箱',30:'征集寻宝参与者',31:'取得毛茸茸的尾巴',32:'帮忙上课',33:'热身的时间到了',34:'请回收试制的箭',35:'帮我取回回忆',36:'ＴＨＥ　智慧较量',37:'善纠结的原因',39:'打开那个宝箱的人是你',40:'终幕的时间到了',41:'取得荣华的碎片',42:'让我感受不羁之力',43:'击败收割者',44:'打倒最强者们',45:'击败爱之天使',46:'击败陈旧的人偶',47:'击败祭典男'}
HELP={'ペルソナ全書閲覧':'查看人格面具全书','ペルソナ全書登録':'登记人格面具全书','１枚目を選んでください':'请选择第１张','２枚目を選んでください':'请选择第２张','３枚目を選んでください':'请选择第３张','１枚目のイケニエを選んでください':'请选择第１张祭品','スキルカード抽出':'抽取技能卡','ペルソナ合体やペルソナ全書の確認ができます':'可进行人格面具合体或查看全书','メンバーを回復する事ができます':'可为队员恢复状态','文化祭へ遊びに行く事ができます':'可前往文化祭游玩','迷宮探索へと出発します':'出发探索迷宫','メンバーの回復や依頼を受ける事ができます':'可为队员恢复状态或接受委托','校内で仲間たちと過ごす事ができます':'可在校园内与伙伴共度时光','迷宮探索に向かいます':'前往探索迷宫','不思議の国のアナタの探索へ向かいます':'前往探索不可思议之国的你','ごーこんきっさの探索へ向かいます':'前往探索联谊咖啡厅','放課後悪霊クラブの探索へ向かいます':'前往探索放学后的恶灵俱乐部','稲羽郷土展の探索へ向かいます':'前往探索稻羽乡土展','時計塔の探索へ向かいます':'前往探索钟楼'}

def main():
    QUEST[4]='抓住偷食物的小偷'
    target=ROOT/'translation/quest_facility_completion.review.json'
    assert not target.exists()
    rows=[];mapping=read(ROOT/'translation/font_encoding.hex.json')
    for r in read(ROOT/'translation/tables.catalog.working.json'):
        if r.get('translation'):continue
        value=QUEST.get(r['row']) if r['member_name']=='qstQuestNameText.qtd' else HELP.get(r['original']) if r['source']=='init/fcltable.bin' else None
        if value is None:continue
        assert len(encode_display(value,mapping))<r['capacity_bytes'],r['key']
        rows.append({**r,'translation':value,'status':'draft_table_reviewed'})
    write(target,{'entries':rows,'runtime_tested':False})
    print('Quest and facility rows:',len(rows))

if __name__=='__main__':main()
