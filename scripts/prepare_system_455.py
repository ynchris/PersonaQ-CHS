"""Review system dialogs in both executables; generate isolated patched copies.

Only exact, NUL-terminated visible tails following the known dialog prefix
are replaced. No pointer, prefix, source executable or installed game is edited.
"""
import hashlib
import re
from compile_translation import ROOT, read, write
from raw_text_codec import encode_display, decode_display

PREFIX = bytes.fromhex('f205fffff141')
T = {
'クリアデータを保存しますか？\n':'要保存通关存档吗？\n',
'クリアデータを保存せず、\nタイトル画面に戻ります。\nよろしいですか？\n':'不保存通关存档，\n返回标题画面。\n确定吗？\n',
'既にセーブされたデータがあります。\n上書きしてよろしいですか？ \n':'已有存档。\n确定要覆盖吗？\n',
'セーブ中です。\n':'正在保存。\n',
'セーブが終了しました。\n':'保存完成。\n',
'セーブが終了しましたが、\n地図データの保存に失敗しました。\n':'存档保存完成，\n但地图数据保存失败。\n',
'セーブが終了しました。\nセーブデータを初期化したので\n早めのセーブをお勧めします。\n':'保存完成。\n存档数据已初始化，\n建议尽早保存。\n',
'セーブが終了しましたが、\n地図データの保存に失敗しました。\nセーブデータを初期化したので\n早めのセーブをお勧めします。\n':'存档保存完成，但地图数据保存失败。\n存档数据已初始化，\n建议尽早保存。\n',
'セーブに失敗しました。\n':'保存失败。\n',
'ロードします。\nよろしいですか？\n':'要读取存档吗？\n',
'ロード中です。\n':'正在读取。\n',
'ロードが終了しました。\n':'读取完成。\n',
'ロードが終了しましたが、\nＳＤカードを認識できなかった為、\n地図データが読み込めませんでした。\n':'存档读取完成，\n但未能识别SD卡，\n无法读取地图数据。\n',
'ロードが終了しましたが、\nデータが見つからなかった為、\n地図データが読み込めませんでした。\n':'存档读取完成，\n但未找到地图数据，\n无法读取地图。\n',
'ロードが終了しました。\nセーブデータを初期化したので\n早めのセーブをお勧めします。\n':'读取完成。\n存档数据已初始化，\n建议尽早保存。\n',
'ロードに失敗しました。\n':'读取失败。\n',
'ＳＤカードに保存されている\n全ての追加データを消去します。\nよろしいですか？\n':'将删除SD卡上保存的\n全部追加数据。\n确定吗？\n',
'本当によろしいですか？\n':'真的确定吗？\n',
'消去中です。\n':'正在删除。\n',
'消去が終了しました。\n':'删除完成。\n',
'消去に失敗しました。\n':'删除失败。\n',
'クリアデータを引き継ぎますか？\n':'要继承通关存档吗？\n',
'クリアデータを引き継がずに、\nゲームを始めてよろしいですか？\n':'不继承通关存档，\n直接开始游戏吗？\n',
'引き継ぎするデータを選んでください。\nクリアしたことのあるデータであれば\n進行中のデータであっても\n引き継ぐことができます。\n':'请选择要继承的存档。\n只要该存档曾经通关，\n即使当前尚未通关，\n也可以继承。\n',
'クリアデータではありません。\n':'这不是通关存档。\n',
'クリアデータからペルソナ全書、\n主人公と仲間たちのステータス、\n所持金やアイテムなど、\n一部のデータを引き継ぎます。\n　\nよろしいですか？\n':'将继承通关存档中的人格面具全书、\n主角与同伴的能力、\n金钱和道具等部分数据。\n\n确定吗？\n',
'クリアデータから地図を引き継ぎます。\n　\nよろしいですか？\n':'将继承通关存档中的地图。\n\n确定吗？\n',
'中断データは削除されます。\nよろしいですか？\n':'将删除中断存档。\n确定吗？\n',
'中断セーブを行います。\nよろしいですか？\n':'要进行中断保存吗？\n',
'中断データをセーブしています。\n':'正在保存中断存档。\n',
'中断セーブが終了しました。\nタイトル画面に戻ります。\n':'中断保存完成。\n即将返回标题画面。\n',
'中断セーブが終了しましたが、\n地図データの保存に失敗しました。\nタイトル画面に戻りますか？\n':'中断保存完成，\n但地图数据保存失败。\n要返回标题画面吗？\n',
'中断セーブに失敗しました。\n':'中断保存失败。\n',
'中断データから再開すると、\n中断データは破棄されます。\n':'读取中断存档继续游戏后，\n该中断存档将被删除。\n',
'中断データをロードしています。\n':'正在读取中断存档。\n',
'中断データをロードしました。\n':'中断存档读取完成。\n',
'中断データのロードに失敗しました。\n':'中断存档读取失败。\n',
'データが破損しています。\n':'数据已损坏。\n',
'ＳＤカードに書き込んでいます。\n':'正在写入SD卡。\n',
'ＳＤカードが差し込まれていません。\n':'未插入SD卡。\n',
'ＳＤカードの空き容量が足りません。\n':'SD卡剩余空间不足。\n',
'ＳＤカードの写真がいっぱいなので\n保存できません。\n':'SD卡照片数量已满，\n无法保存。\n',
'ＳＤカードを認識できませんでした。\n':'无法识别SD卡。\n',
'すれちがい通信のデータを確認しています。\n':'正在检查擦肩通信数据。\n',
'更新内容を破棄して編集を終了します。\nよろしいですか？\n':'要放弃更改并结束编辑吗？\n',
'ゲームコインが足りません。\n':'游戏金币不足。\n',
'この名前でよろしいですか？\n':'确定使用这个名字吗？\n',
'地図データを上書きしますか？\n':'要覆盖地图数据吗？\n',
'これでよろしいですか？\n':'这样可以吗？\n',
'不適切な内容です。\nもう一度、入力してください。\n':'内容不合适。\n请重新输入。\n',
'数字は５文字までしか入力できません。\nもう一度、入力してください。\n':'最多只能输入5个数字。\n请重新输入。\n',
'このスロットにセーブすると、\nセーブデータがＳＤカードに保存されます。\nご注意ください。\n':'请注意：在此栏位保存时，\n存档将保存至SD卡。\n',
'ここではＳＤカードに保存されている\nセーブデータをロードできます。\n':'可在此读取保存在SD卡上的存档。\n',
'更新データの確認と受信を行います。\nよろしいですか？\n':'要检查并接收更新数据吗？\n',
'更新しました。\n再起動します。\n':'更新完成。\n即将重新启动。\n',
'更新データは最新です。\n':'已是最新版本。\n',
'ペルソナＱでは地図データを\nＳＤカードに保存します。\n　\nＳＤカードが差し込まれていない場合、\n地図データを保存できません。\n':'《女神异闻录Q》的地图数据\n保存在SD卡中。\n\n未插入SD卡时，\n无法保存地图数据。\n',
'セーブデータを初期化しています。\n':'正在初始化存档数据。\n',
'ファイルの破損を検出したため\nセーブデータを初期化しました。\n':'检测到文件损坏，\n已初始化存档数据。\n',
'ファイルの破損を検出したため\nセーブデータを初期化しています。\n':'检测到文件损坏，\n正在初始化存档数据。\n',
'ファイルの破損を検出したため\n追加データを初期化しました。\n':'检测到文件损坏，\n已初始化追加数据。\n',
'ファイルの破損を検出したため\n該当する追加データを作り直します。\n':'检测到文件损坏，\n将重新创建相应的追加数据。\n',
'ファイルの復旧に失敗しました。\nＳＤカードに保存された追加データが\n破損しています。\n　\n「コンフィグ」のデータ削除から\n追加データを初期化してください。\n':'文件修复失败。\nSD卡中保存的追加数据已损坏。\n\n请在“设置”的“删除数据”中\n初始化追加数据。\n',
'ファイルの破損を検出したため\n該当する追加データを削除しました。\n':'检测到文件损坏，\n已删除相应的追加数据。\n',
'ＳＤカードが書き込み禁止になっています。\n':'SD卡已被写保护。\n',
'追加データを新規に作成しています。\n':'正在创建追加数据。\n',
'追加データを新規に作成しました。\n':'追加数据创建完成。\n',
'ＳＤカードを認識できませんでした。\n電源を切って差し直してください。\n':'无法识别SD卡。\n请关闭电源后重新插入。\n',
}

def main():
    mapping = read(ROOT/'translation/font_encoding.hex.json')
    old = read(ROOT/'translation/code_ui_build.generated.json')
    files = []
    for existing in old['files']:
        source = ROOT/existing['source']
        raw = source.read_bytes()
        baseline = (ROOT/existing['output']).read_bytes()
        assert hashlib.sha256(baseline).hexdigest() == existing['sha256']
        out = bytearray(baseline)
        rows, pending, found, allowed = [], [], set(), set()
        for m in re.finditer(re.escape(PREFIX), raw):
            pos = m.end(); end = raw.index(0, pos)
            data = raw[pos:end]
            try: jp = data.decode('cp932')
            except UnicodeDecodeError:
                pending.append(dict(offset=pos,original_hex=data.hex(),reason='embedded_controls_or_nontext'))
                continue
            if jp not in T:
                pending.append(dict(offset=pos,original=jp,reason='not_yet_reviewed'))
                continue
            cn = T[jp]; encoded = encode_display(cn, mapping)
            assert len(encoded) <= len(data), (jp, cn)
            assert decode_display(encoded,mapping) == cn
            assert baseline[pos:end] == data
            assert not allowed.intersection(range(pos,end))
            allowed.update(range(pos,end))
            out[pos:end] = encoded.ljust(len(data),b'\0')
            assert out[m.start():pos] == PREFIX and out[end] == 0
            rows.append(dict(offset=pos,capacity_bytes=len(data),original=jp,translation=cn))
            found.add(jp)
        assert found == set(T), set(T)-found
        assert len(out) == len(raw)
        assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(baseline,out)))
        dest = ROOT/'full_work/system_455'/existing['scope']/'code.bin'
        dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(out)
        files.append(dict(scope=existing['scope'],source=existing['source'],source_sha256=hashlib.sha256(raw).hexdigest(),
                          baseline=existing['output'],baseline_sha256=existing['sha256'],output=dest.relative_to(ROOT).as_posix(),
                          sha256=hashlib.sha256(out).hexdigest(),rows=rows,pending=pending))
    write(ROOT/'translation/system_455.review.json',dict(files=files,encoding_sha256=hashlib.sha256((ROOT/'translation/font_encoding.hex.json').read_bytes()).hexdigest(),
          runtime_tested=False,packaged=False,notes='Isolated copies only. Prefixes, addresses, byte length and bytes outside reviewed text preserved. Pending rows are NOT translated.'))
    print([(f['scope'],len(f['rows']),len(f['pending'])) for f in files])

if __name__=='__main__': main()
