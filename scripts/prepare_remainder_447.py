import hashlib
from collections import defaultdict
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING
from audit_remaining_text import classify_row
T={
'１通常':'１普通','２スライド':'２滑动','３○ワイプ':'３○擦除',
'＞定型文。通り抜けますか？\n':'＞通用提示。要穿过去吗？\n',
'フロア導入イベント見ない':'不看楼层开场事件','フロア導入イベント見る':'观看楼层开场事件',
'ペルソナ「ピクシー」「コロポックル」が\n心の中に芽生えた気がした。\n':'感觉人格面具“皮克希”和“克鲁波克鲁”\n在心中萌芽了。\n',
'今はやめておく':'暂时算了','動けない！\n':'动不了！\n','なし\n':'无\n',
'素材枠ID_0x778　１ページ目\n討伐：雨見の壷\n':'素材栏ID_0x778　第１页\n讨伐：雨见之壶\n',
'＞セーブデータをロードしました。\n':'＞已读取存档。\n','＞扉に鍵がかかっている。\n':'＞门锁着。\n','＞扉の鍵を開けた。\n':'＞打开了门锁。\n',
'＞扉の先に大型のシャドウの\n　気配を感じる…\n':'＞感觉到门后有\n　大型阴影的气息…\n',
'＞ともかく、\n　これで鍵を取ることができた。\n':'＞总之，\n　这样就拿到钥匙了。\n',
'＞南京錠の掛かっていた扉に\n　行ってみよう…\n':'＞去那扇挂着锁的门\n　看看吧…\n',
'スキップする':'跳过','スキップしない':'不跳过','先に進む':'继续前进',
'＞この先に張り詰めた空気を感じる…\n':'＞感觉前方的气氛十分紧张…\n',
'＞校内の様子が変わっている…\n':'＞校内的景象变了…\n','＞時計塔のせいだろうか…\n':'＞是钟楼的缘故吗…\n',
'ボス戦をスキップしますか？\n':'要跳过首领战吗？\n','する':'跳过','しない':'不跳过',
'ボス戦をスキップし、タウンに戻ります。\n':'将跳过首领战，返回城镇。\n',
}
for n in '１２３':T[f'＞ご褒美アイテム{n}を手に入れた。\n']=f'＞获得了奖励道具{n}。\n'
for n in ['４５','４６','４７','４８','４９']:
    T[f'“クエスト{n}”\n']=f'“委托{n}”\n'
    T[f'“クエスト{n}”を\n受領していただき\nありがとうございます。\n']=f'感谢您\n接受\n“委托{n}”。\n'
    T[f'“クエスト{n}”を\nご報告いただき\nありがとうございます。\n']=f'感谢您\n报告\n“委托{n}”。\n'
    T[f'“クエスト{n}”を\n破棄いたします。\n']=f'将放弃\n“委托{n}”。\n'

def main():
    p=ROOT/'translation/batches/447_remaining_messages.generated.json';assert not p.exists()
    sources=defaultdict(list);hashes={};audit=[]
    for r in read(ROOT/'translation/catalog.working.json'):
        if r.get('translation') or classify_row(r)[0] not in {'needs_review','none_label_review'}:continue
        old=r['original'];plain=TOKEN.sub('',old);assert plain in T,(r['key'],plain)
        pre=LEADING.match(old).group();suf=TRAILING.search(old).group()
        assert not TOKEN.search(old[len(pre):len(old)-len(suf)])
        body=T[plain];full=pre+body+suf
        a=plain.splitlines();b=body.splitlines();assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),r['key']
        s=r['source'];i=r['message_index'];j=r['line_index'];d=read(ROOT/s)
        sources[s].append([i,j,d['texts'][i]['id'],body]);hashes[s]=hashlib.sha256((ROOT/s).read_bytes()).hexdigest()
        audit.append(dict(key=r['key'],original=plain,translation=body))
    assert len(audit)==147,len(audit)
    write(p,dict(status='draft',sources=dict(sources),source_hashes=hashes,review_notes=['补齐余下110条迷宫/任务/事件提示和37条附加效果“无”。同文同译，不因旧作/调试附近而自动排除未标注文本。','保留原始测试性质的通用提示/奖励道具编号/素材栏ID，不编造实际道具；原文所含数字全部保留。','不包含明确开发说明、占位、空白和纯标点；所有这些仍保留在总目录及审计清单中。'],translation_audit=audit))
    print('Pages:',len(audit))
if __name__=='__main__':main()
