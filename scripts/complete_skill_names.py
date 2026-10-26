"""Complete display names in PQ1's primary skill bank, not legacy banks."""
import re
from compile_translation import ROOT,read,write
from q2_name_banks import DRAFT
from equipment_names import load_drafts
from q2_item_names import load as item_names

EXTRA=ROOT/'translation/skill_names_completion.review.json'
LOCAL={
'ＡＴＴＡＣＫ':'攻击','ティアドロップ':'泪滴','クイックオーダー':'快速指令','エネミーソナー':'敌人声呐',
'覇者の心得':'霸者心得','観察眼':'观察眼','大自然の恵み':'大自然的恩惠','斬耐性':'斩击耐性','壊耐性':'坏击耐性','追撃':'追击',
'軟膏薬':'软膏','ヒールゼリー':'治疗果冻','ソウルフード':'灵魂食粮','救急キット':'急救套件','クロズディジェム':'克洛兹迪宝石','パトラジェム':'帕特拉宝石',
'ブレイバント':'勇气药','ストナード':'坚硬药','耐斬ミスト':'抗斩喷雾','耐壊ミスト':'抗坏喷雾','耐突ミスト':'抗突喷雾',
'ファイアオイル':'火焰油','フリーズオイル':'冰冻油','サンダーオイル':'雷电油','ウインドオイル':'疾风油',
'灼熱の勾玉':'灼热勾玉','零度の勾玉':'零度勾玉','天雷の勾玉':'天雷勾玉','暴風の勾玉':'暴风勾玉',
'毒の香':'毒之香','麻痺の香':'麻痹之香','睡眠の香':'睡眠之香','呪いの香':'诅咒之香','混乱の香':'混乱之香',
'魔散の護符':'驱魔护符','魔寄せの札':'招魔符','ホバーサンダル':'悬浮凉鞋','ソーマゼリー':'苏摩果冻','暁のお守り':'拂晓护符','退魔の鈴':'驱魔铃',
'単体盲目':'单体失明','全体盲目':'全体失明',
}
# Explicit implementation-only slots identified by the corresponding help text
# or their bookkeeping name; no display-completion claim for these entries.
INTERNAL={148,173,373,374,538,564,565,1083,1084,1085,1086,1087,1088}
def marker(name):return bool(re.fullmatch(r'.*(開始|最後|最期)',name))

def main():
    assert not EXTRA.exists()
    group=next(g for g in read(DRAFT)['groups'] if g['source']=='battle/table/skillnametable.tbl')
    index={};origin={}
    for r in read(ROOT/'translation/catalog.working.json'):
        if r['source']=='export_base/init/datskillcardhelp.bmd.json' and r.get('translation'):
            a=re.search('“(.*?)”',r['original']);b=re.search('[“「](.*?)[”」]',r['translation'])
            if a and b:
                assert a[1] not in index or index[a[1]]==b[1]
                index[a[1]]=b[1];origin[a[1]]=r['key']
    names=load_drafts()[2]
    for i,t in item_names().items():
        if names[i] not in index:index[names[i]]=t;origin[names[i]]=f'itemtbl:{i}'
    rows=[];excluded=[]
    for r in group['excluded']:
        name=r['original'];i=r['index']
        if r['reason']=='placeholder_or_internal' or marker(name) or i in INTERNAL:
            excluded.append({**r,'reason':'placeholder_or_internal'});continue
        value=index.get(name,LOCAL.get(name))
        assert value is not None,(i,name)
        rows.append(dict(index=i,original=name,translation=value,local_reference=origin.get(name),references=[]))
    write(EXTRA,dict(source=group['source'],source_sha256=group['source_sha256'],rows=rows,excluded=excluded,runtime_tested=False))
    print('New skill slots:',len(rows),'unique names:',len({r['original'] for r in rows}),'retained internal slots:',len(excluded))

if __name__=='__main__':main()
