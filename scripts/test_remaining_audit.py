import hashlib,unittest
from audit_remaining_text import classify,classify_row,PROTOTYPE_SOURCES
from compile_translation import ROOT,read,TOKEN

class RemainingAuditTests(unittest.TestCase):
    def test_reviewed_test_labels(self):
        for t in ['テストクエスト０４\n受領','テストミッション０５','校内散策テスト01','ＨＰ７５％リザーブ','大蜘蛛戦\n残ＨＰ５０％ありません','エリザベス４連戦４戦目ゼウスＡ\n終了台詞','クエスト４９の概要です。\nダミーメッセージです。']:
            self.assertEqual(classify(t)[0],'explicit_development_note')
        for t in ['テストクエストを達成した！','大蜘蛛戦が始まる！','ＨＰ７５％回復','今はやめておく','ここでタイトルに戻りますか？']:
            self.assertEqual(classify(t)[0],'needs_review')
    def test_temporary_labels(self):
        for text in ['（仮メッセージ）\n戦闘が行われた。勝利した。','クエスト詳細70','戦闘開始リザーブ０','ダミー会話よ。']:
            self.assertEqual(classify(text)[0],'explicit_development_note')
        self.assertEqual(classify('仮面を外した。')[0],'needs_review')
    def test_prototype_script_evidence_and_duplicate(self):
        docs=[read(ROOT/s) for s in sorted(PROTOTYPE_SOURCES)]
        self.assertEqual(docs[0],docs[1])
        self.assertEqual(len(docs[0]['texts']),38)
        plain=lambda i:TOKEN.sub('', ''.join(docs[0]['texts'][i]['lines']))
        for i,marker in [(0,'※これはダミーです'),(3,'※これはダミーです'),(5,'モデル描画テスト'),(21,'宝箱が実装されていない'),(28,'今回は戦闘には入りません'),(37,'αでは')]:
            self.assertIn(marker,plain(i))
        rows=read(ROOT/'translation/remaining_audit.generated.json')['rows']
        selected=[r for r in rows if r['source'] in PROTOTYPE_SOURCES]
        self.assertFalse(any(r['category']=='needs_review' for r in selected))
        self.assertEqual(classify_row(dict(source='other',message_index=1,original='あ！逃げだした！'))[0],'needs_review')
    def test_event_context_is_scoped(self):
        self.assertEqual(classify('＞一枚絵イベントです。')[0],'explicit_development_note')
        self.assertEqual(classify('＞一枚絵のイベントです。')[0],'explicit_development_note')
        self.assertEqual(classify('＞特殊イベントです。続けますか？')[0],'needs_review')
        for source,plain in [('export_base/event/e700/e722_900.bf.json','やる'),('export_base/event/e100/e100_010.bf.json','Ａ')]:
            self.assertEqual(classify_row(dict(source=source,original=plain))[0],'explicit_development_note')
            self.assertEqual(classify_row(dict(source='another_scene',original=plain))[0],'needs_review')
    def test_conservative_rules(self):
        self.assertEqual(classify('ダミーだよ\n')[0],'explicit_placeholder')
        self.assertEqual(classify('スキルID_0x00A\nスキルヘルプ文章２行目\n')[0],'explicit_placeholder')
        self.assertEqual(classify('なし\n')[0],'none_label_review')
        self.assertEqual(classify('ダミーの敵が現れた！')[0],'needs_review')
        self.assertEqual(classify('コミュの力が増した！')[0],'needs_review')
        for text in ['補助スキル“ブランク”を\n習得できるスキルカード。\n','電撃スキル“リザーブ”を\n習得できるスキルカード。\n','リザーブ“アイテム”を\n習得できるスキルカード。\n']:
            self.assertEqual(classify(text)[0],'explicit_placeholder')
        for text in ['補助スキル“メディア”を\n習得できるスキルカード。\n','リザーブについて説明します。','補助スキル“（再生の竪琴）”を\n習得できるスキルカード。\n']:
            self.assertEqual(classify(text)[0],'needs_review')
    def test_inventory_complete_and_nonmutating(self):
        p=ROOT/'translation/catalog.working.json';a=read(ROOT/'translation/remaining_audit.generated.json');rs=read(p)
        self.assertEqual(a['catalog_sha256'],hashlib.sha256(p.read_bytes()).hexdigest())
        expected={r['key'] for r in rs if not r.get('translation')}
        self.assertEqual({r['key'] for r in a['rows']},expected)
        self.assertEqual(len(a['rows']),len(expected));self.assertEqual(sum(a['categories'].values()),len(expected))
    def test_numbered_placeholders_are_exact(self):
        for text in ['ダミー３８\n','ダミー１０８の１\nダミー１０８の２\n','ＢＬＡＮＫ\n','選択肢１\n選択肢２\n選択肢３\n選択肢４\n','クエスト４８\n説明文\n']:
            self.assertEqual(classify(text)[0],'explicit_placeholder')
        for text in ['ダミー３８を倒した！','クエスト４８\n敵を倒す','選択肢１を選んでください。']:
            self.assertEqual(classify(text)[0],'needs_review')
        a=read(ROOT/'translation/remaining_audit.generated.json')
        rows=[r for r in a['rows'] if r['source']=='export_base/event/gcs.bin_gconSelectQuestionMessage.bmd.json']
        self.assertTrue(rows)
        self.assertTrue(all(r['category']=='explicit_placeholder' for r in rows))
    def test_skill_card_review_boundary(self):
        a=read(ROOT/'translation/remaining_audit.generated.json')
        rows=[r for r in a['rows'] if r['source']=='export_base/init/datskillcardhelp.bmd.json']
        self.assertEqual(len(rows),261)
        self.assertEqual(sum(r['category']=='explicit_placeholder' for r in rows),261)
        self.assertEqual(sum(r['category']=='needs_review' for r in rows),0)
        original=read(ROOT/'export_base/init/datskillcardhelp.bmd.json')
        catalog={r['message_index']:r for r in read(ROOT/'translation/catalog.working.json') if r['source']=='export_base/init/datskillcardhelp.bmd.json'}
        for i in [141,148,173,294,296,300,360,373,374,384,394,404,407,409,411,414,416,418,426,428,430,432,435,596]:
            self.assertEqual(classify(original['texts'][i]['lines'][0])[0],'needs_review')
            self.assertTrue(catalog[i]['translation'])

if __name__=='__main__':unittest.main()
