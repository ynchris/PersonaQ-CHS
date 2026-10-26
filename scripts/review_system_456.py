"""Complete the discovered dialog family as text-only review; do not build code."""
import hashlib
import re
from compile_translation import ROOT, read, write
from raw_text_codec import encode_message
from audit_ui_456 import text_with_controls

# Order bound to an immutable SHA-256 snapshot; never apply to a new list by index.
SNAPSHOT='b4b3d44d93428650bb1bba2717464a742b258ac74a7a2cd1878ad520541c8c79'
CN=[
'在新游戏中继承此处保存的存档，\n即可保留部分通关时的数据，\n从头开始游戏。\n\n读取此处保存的存档，\n则可保留通关时的状态，\n回到通关前继续游戏。\n',
'存档读取完成，\n但未能识别SD卡，无法读取地图。\n\n存档数据已初始化，\n建议尽早保存。\n',
'存档读取完成，\n但未找到地图数据，无法读取地图。\n\n存档数据已初始化，\n建议尽早保存。\n',
'将删除全部存档。\n确定吗？\n\n{F2 01 03 01}SD卡中的追加数据\n不会被删除。{F2 01 01 01}\n',
'　\n　\n　\n　\n{F2 01 02 01}{F2 44 01 01}{F2 01 01 01}　\n要从这里继续游戏吗？\n',
'中断存档读取完成，\n但未能识别SD卡，\n无法读取地图数据。\n要继续吗？\n',
'中断存档读取完成，\n但未找到地图数据，\n无法读取地图。\n要继续吗？\n',
'中断存档读取完成。\n存档数据已初始化，\n建议尽早保存。\n',
'中断存档读取完成，\n但未能识别SD卡，无法读取地图。\n\n存档数据已初始化，\n建议尽早保存。\n',
'中断存档读取完成，\n但未找到地图数据，无法读取地图。\n\n存档数据已初始化，\n建议尽早保存。\n',
'注册擦肩通信后，\n即可与擦肩而过的玩家\n交换擦肩手册。\n\n要在Nintendo 3DS主机上\n注册《女神异闻录Q》的\n擦肩通信吗？\n',
'已在Nintendo 3DS主机上注册\n《女神异闻录Q》的擦肩通信。\n',
'即使结束游戏，\n擦肩通信也会自动进行。\n\n若要停止，请在HOME菜单选择\n“主机设置”，进入“数据管理”中的\n“擦肩通信管理”进行设置。\n',
'《女神异闻录Q》的擦肩通信\n已经注册。\n\n若要停止，请在HOME菜单选择\n“主机设置”，进入“数据管理”中的\n“擦肩通信管理”进行设置。\n',
'Nintendo 3DS主机的\n擦肩通信注册数量已达上限。\n\n请在“主机设置”的“擦肩通信管理”中\n停用其他软件的擦肩通信。\n',
'使用擦肩通信前，\n需要同意最新的使用条款。\n\n请在主机设置中依次选择\n“互联网设置” > “其他信息” >\n“确认使用条款”，并同意最新条款。\n',
'由于家长限制了\n“与其他用户进行擦肩通信”，\n无法使用擦肩通信。\n',
'将自己的擦肩手册二维码\n导出至SD卡。\n\n要导出至SD卡吗？\n',
'二维码图片已导出。\n{F2 44 01 01}　\n',
'擦肩手册的内容已更新。\n\n要将更改应用到擦肩通信吗？\n',
'将使用{F2 44 01 01}枚游戏金币。\n确定吗？\n\n{F2 01 03 01}即使不保存就结束游戏，\n已使用的游戏金币也不会退还。{F2 01 01 01}\n',
'主角的名字可能会向\n通信对象公开。\n\n请勿包含令人不快、侵犯他人权利\n或涉及个人隐私等内容。\n',
'他的名字可能会向\n通信对象公开。\n\n请勿包含令人不快、侵犯他人权利\n或涉及个人隐私等内容。\n',
'请勿传播或公开令人不快、\n侵犯他人权利的文字，\n或自己与他人的隐私信息。\n',
'留言可能会向通信对象公开。\n\n请勿包含令人不快、侵犯他人权利\n或涉及个人隐私等内容。\n',
'擦肩通信昵称可能会向\n通信对象公开。\n\n请勿包含令人不快、侵犯他人权利\n或涉及个人隐私等内容。\n',
'正在检查追加内容。\n',
'正在接收追加内容信息。\n',
'没有可购买的追加内容。\n',
'要删除追加内容吗？\n',
'删除完成。\n',
'追加内容中的副人格面具\n{F2 01 03 01}“{F2 44 01 01}”{F2 01 01 01}\n已加入人格面具全书。\n',
'导航设置已新增{F2 01 03 01}“{F2 44 01 01}”{F2 01 01 01}语音。\n',
'现在可以召唤追加内容中的\n副人格面具了。\n\n首次从全书召唤时免费。\n',
'现在可以设置导航语音了。\n\n按X键选择导航语音。\n',
'可在标题画面的\n{F2 01 03 01}追加内容{F2 01 01 01}中\n添加导航语音。\n',
]

def main():
    p=ROOT/'translation/system_455.review.json'
    assert hashlib.sha256(p.read_bytes()).hexdigest()==SNAPSHOT
    prior=read(p); mapping=read(ROOT/'translation/font_encoding.hex.json')
    pending=prior['files'][1]['pending']; assert len(pending)==len(CN)==36
    translations={}
    update=(ROOT/prior['files'][1]['source']).read_bytes()
    for row,cn in zip(pending,CN):
        start=row['offset']; data=update[start:update.index(0,start)]
        jp=text_with_controls(data)
        assert jp not in translations
        translations[jp]=cn
    inv=read(ROOT/'translation/system_inventory_456.generated.json')
    for f in inv['files']:
        raw=(ROOT/f['source']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==f['sha256']
        for r in f['rows']:
            if r['translation'] is None:r['translation']=translations[r['original']]
            controls=lambda s:re.findall(r'\{[0-9A-F ]+\}',s)
            assert controls(r['original'])==controls(r['translation'])
            encoded=encode_message(r['translation'],mapping)
            assert len(encoded)<=r['capacity_bytes'],(r['original'],len(encoded),r['capacity_bytes'])
            assert b'\0' not in encoded
            assert raw[r['offset']:r['offset']+r['capacity_bytes']].hex()==r['original_hex']
            r['status']='translated_capacity_and_controls_checked'
    inv.update(packaged=False,runtime_tested=False,encoding_sha256=hashlib.sha256((ROOT/'translation/font_encoding.hex.json').read_bytes()).hexdigest(),
               notes='Text review only. No executable written. Full discovered prefix family, not all system UI. Dynamic variables and line fit require runtime validation.')
    write(ROOT/'translation/system_456.review.json',inv)
    print('Reviewed dialogs:',[(f['source'],len(f['rows'])) for f in inv['files']])

if __name__=='__main__':main()
