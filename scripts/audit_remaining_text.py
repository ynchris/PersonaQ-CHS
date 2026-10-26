"""Read-only catalog classification; never changes coverage or translations."""
import re,hashlib
from collections import Counter
from compile_translation import ROOT,read,write,TOKEN

PROTOTYPE_SOURCES={
    'export_base/dungeon/script/dungeon35f.gsd_dungeon35f.bf.json',
    'export_base/dungeon/pack/field/f04_05.arc_dungeon35f.gsd_dungeon35f.bf.json',
}

def classify(text):
    plain=TOKEN.sub('',text).strip()
    if re.fullmatch(r'(?:テストクエスト[０-９0-9]+(?:\s*(?:受領|報告))?|テストミッション[０-９0-9]+|校内散策テスト[0-9]+|TEST (?:NONE|NEWGAME|GAMEOVER)|テスト|運命の相手テスト)',plain):return 'explicit_development_note','Exact numbered test quest/mission or test label'
    if re.fullmatch(r'(?:＞BTLMSGID_RESULT[0-9]+|(?:武器|防具|アクセサリー|消耗品|貴重品)枠最後|未使用|私はだみ～よ|会話ダミー)',plain):return 'explicit_placeholder','Exact internal ID, bank boundary or unused/dummy label'
    if re.fullmatch(r'(?:ＨＰ[０-９]+％リザーブ|戦闘終了リザーブ|(?:[１-４]ページ目\s*)?牧師戦開始台詞はありません|(?:ドクター＆ナース|大蜘蛛)戦開始台詞\s*ありません|(?:デカウサギ|大蜘蛛)戦\s*残ＨＰ[０-９]+％ありません|(?:デカウサギ|大蜘蛛|クロノス)戦終了台詞\s*ありません)',plain):return 'explicit_development_note','Exact missing/reserved boss dialogue slot'
    if re.fullmatch(r'(?:(?:マーガレット戦|エリザベス４連戦[１-４]戦目(?:ゼウス[ＡＢ])?)\s*(?:開始台詞その[３４]|終了台詞)|終了台詞)',plain):return 'explicit_development_note','Exact boss dialogue staging label, not actual spoken line'
    if plain in {'ディバイドガードメッセージ','オーバーガードメッセージ','新規入荷MSG','＞新規入荷メッセージ','＞入店時挨拶','マーガレット用入店時挨拶。','テオドア用入店時挨拶。','ヒーロータイプの説明','挨拶１。','挨拶２。','ジュース使用前確認MSG（仮）','事故率ＵＰ時のメッセージ（仮）','＞仮メッセージです。','＞マーガレットのスキルリセット演出','ここでスタッフロールが入ります。','ここでクリアーデータセーブが入ります。','ここでタイトルに戻ります。'}:return 'explicit_development_note','Reviewed exact event/message staging placeholder'
    if any(m in plain for m in ['ダミーメッセージ','ダミー会話です','これがでたらバグです','未実装','仮実装','【仮チュートリアル】','（テスト用）','キャラセリフテスト','スクリプトモーションテスト','デバッグモード']):return 'explicit_development_note','Explicit dummy, prototype, unimplemented or debug marker'
    if re.fullmatch(r'Ｅ[０-９]+＿[０-９]+\s*仮イベント',plain):return 'explicit_development_note','Exact temporary event ID'
    if plain in {'＞スキルを全て覚えたダミーMSG。','保健室用会話です。\n施設用スクリプトで実行しています。','サブペを装備していない時の警告文。\nサブペルソナの準備をしてください。','追撃・久慈川りせ\nダミー枠','追撃・山岸風花\nダミー枠','＞そう言えば、依頼にあった\n　（アイテム仮）を入手している…','（特殊イベントです）\n＞蝶が蜘蛛の巣から脱出し、\n　元気に羽ばたいていく。'}:return 'explicit_development_note','Reviewed exact dummy, temporary item or staging instruction'
    if re.fullmatch(r'(?:ダミー会話(?:よ|でございます)。|クエスト詳細[0-9０-９]+|(?:ダンジョン|フィールド)テスト|戦闘開始リザーブ[0-9０-９]+|(?:デカウサギ|クロノス)戦開始台詞\s*ありません)',plain):return 'explicit_development_note','Exact dummy/test/reserve label'
    if plain.startswith(('（仮メッセージ）','仮テキストです。','α２用テキスト。')) or plain=='α２ではここから先には進行できません。':return 'explicit_development_note','Explicit temporary or alpha-build text'
    if re.fullmatch(r'＞(?:アニメ|一枚絵の?|特別演出の|特殊)イベントです。',plain):return 'explicit_development_note','Exact event staging placeholder'
    if plain=='＞スタッフロールが入ります。\n　※仮イベント':return 'explicit_development_note','Explicit temporary credits event'
    if not plain:return 'empty', 'No visible text'
    if not re.search(r'[\w\u3040-\u9fff]',plain):return 'punctuation_only','No words; keep unchanged pending context'
    if re.fullmatch(r'ダミー[０-９0-9]+',plain):return 'explicit_placeholder','Numbered dummy label only'
    if re.fullmatch(r'ダミー([０-９0-9]+)の１\nダミー\1の２',plain):return 'explicit_placeholder','Matching numbered dummy option pair'
    if plain=='ＢＬＡＮＫ' or re.fullmatch(r'(?:ＢＬＡＮＫ)?選択肢１\n(?:ＢＬＡＮＫ)?選択肢２\n(?:ＢＬＡＮＫ)?選択肢３\n(?:ＢＬＡＮＫ)?選択肢４',plain):return 'explicit_placeholder','Blank or four generic numbered option labels'
    if re.fullmatch(r'クエスト[０-９0-9]+\s*説明文',plain):return 'explicit_placeholder','Quest number and generic description label only'
    if re.fullmatch(r'(?:武器|防具|アクセサリー|消耗品|貴重品)ID_0x[0-9A-Fa-f]+',plain):return 'explicit_placeholder','Item ID label only'
    if re.fullmatch(r'(?:ブランク(?:\s*[１２]ページ目)?\s*)+',plain):return 'explicit_placeholder','Blank page labels only'
    if re.fullmatch(r'素材枠ID_0x([0-9A-Fa-f]+)\s*１ページ目\s*素材枠ID_0x\1\s*２ページ目',plain):return 'explicit_placeholder','Matching material ID page labels'
    if re.fullmatch(r'(?:ダミーだよ|ダミー|ダミ－|ダミーのまま入れ込む|ダミー・(?:りせ|風花)用入れ込む|リザーブ|ＲＥＳＥＲＶＥ(?:\s*神話)?|ブランク|欠番)',plain):return 'explicit_placeholder','Exact placeholder label'
    if re.fullmatch(r'スキルID_0x[0-9A-Fa-f]+\s*スキルヘルプ文章２行目',plain):return 'explicit_placeholder','Skill ID and placeholder second-line label'
    if re.fullmatch(r'(?:[^\n“”]+スキル“(?:ブランク|リザーブ)”|リザーブ“[^\n“”]+”)を\s*習得できるスキルカード。',plain):return 'explicit_placeholder','Exact skill-card template with explicit blank or reserve label; reachability not inferred'
    markers=['スキルヘルプ文章不要','スキルヘルプ文章未定','仕様カットされた','カットセリフ','デバッグ用','テストテキスト','イベントは仮','このイベントは仮','イベント予定','テストです','実装されていない','モデル描画テスト']
    for marker in markers:
        if marker in plain:return 'explicit_development_note',marker
    if plain=='なし':return 'none_label_review','May be visible None or reserved entry; do not infer'
    return 'needs_review','Not enough evidence to exclude; may include legacy or valid text'

def classify_row(row):
    category,reason=classify(row['original'])
    if category!='needs_review':return category,reason
    if row['source'] in {'export_base/event/e900/e999_001.bf.json','export_base/event/e900/e999_003.bf.json'}:
        return 'explicit_development_note','Reviewed story-start debug menu or BGM/COMSE playback test script; source explicitly states test/debug purpose'
    if row['source'].endswith('dungeon41f.gsd_dungeon41f.bf.json') and row['message_index']==2:
        return 'explicit_development_note','WAIT menu immediately following explicit script-motion test prompt'
    if row['source'].endswith('dungeon21f.gsd_dungeon21f.bf.json') and row['message_index']==5:
        return 'explicit_development_note','Continuation of explicit temporary FOE implementation explanation'
    if row['source'] in PROTOTYPE_SOURCES and 0<=row['message_index']<=37:
        return 'explicit_development_note','Reviewed prototype script: dummy scene, model tests, temporary events, unimplemented combat/chests and alpha quest flags; not proof of runtime unreachability'
    plain=TOKEN.sub('',row['original']).strip()
    if row['source']=='export_base/event/e700/e722_900.bf.json' and plain in {'＞選択部屋テスト用やる？','やる','やらない','＞いままでの選択は…'}:
        return 'explicit_development_note','Choice-room test prompt/options/status; same script explicitly labels debug partner results'
    if row['source']=='export_base/event/e100/e100_010.bf.json' and (plain in {'Ａ','Ｂ','Ｂ（再読み込み）'} or ('順平のモーション' in plain and 'Ａ⇒Ｂ⇒Ｂ（再読み込み）⇒Ａ' in plain)):
        return 'explicit_development_note','Junpei animation/voice reload test labels and instructions in this source only'
    return category,reason

def main():
    path=ROOT/'translation/catalog.working.json';catalog=read(path);rows=[]
    for r in catalog:
        if r.get('translation'):continue
        category,reason=classify_row(r)
        rows.append(dict(key=r['key'],source=r['source'],message_index=r['message_index'],line_index=r['line_index'],speaker=r.get('speaker'),original=r['original'],category=category,reason=reason))
    counts=dict(Counter(r['category'] for r in rows));sources=Counter(r['source'] for r in rows if r['category']=='needs_review')
    result=dict(catalog_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),total_catalog=len(catalog),translated=sum(bool(r.get('translation')) for r in catalog),remaining=len(rows),categories=counts,review_sources=dict(sources.most_common()),policy='Audit only. No rows removed, translated, or declared unreachable. Legacy detection requires further evidence.',rows=rows)
    write(ROOT/'translation/remaining_audit.generated.json',result)
    print('Remaining:',len(rows),'Categories:',counts)
    print('Largest review queues:',sources.most_common(8))

if __name__=='__main__':main()
