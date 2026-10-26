"""Reviewed support and accessory descriptions: text integrity, not runtime QA."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path
from compile_translation import LEADING, TRAILING, TOKEN

ROOT = Path(__file__).resolve().parent

def read(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8-sig'))

class SupportAccessoryTests(unittest.TestCase):
    def test_reviewed_batches(self):
        for filename,count in [('353_skill_support_and_boss_effects.json',51),('354_accessory_stats_and_resistances.json',85),('355_accessory_tail_and_armor.json',{'export_base/init/dataccessoryhelp.bmd.json':20,'export_base/init/datarmorhelp.bmd.json':55}),('356_armor_clothes_and_aigis.json',65),('357_armor_koromaru_and_zen.json',53),('358_weapon_swords_and_knives.json',60),('359_weapon_footwear_fans_and_shields.json',60)]:
            batch=read('translation/batches/'+filename)
            for source,rows in batch['sources'].items():
                self.assertEqual(hashlib.sha256((ROOT/source).read_bytes()).hexdigest(),batch['source_hashes'][source])
                old=read(source)
                compiled=read('translation/compiled/'+source)
                expected_count=count[source] if isinstance(count,dict) else count
                self.assertEqual(len(rows),expected_count)
                self.assertEqual(len({(r[0],r[1]) for r in rows}),expected_count)
                for mi,li,mid,body in rows:
                    with self.subTest(batch=filename,index=mi):
                        original=old['texts'][mi]['lines'][li]
                        self.assertEqual(old['texts'][mi]['id'],mid)
                        value=LEADING.match(original).group()+body+TRAILING.search(original).group()
                        self.assertEqual(compiled['texts'][mi]['lines'][li],value)
                        self.assertEqual(TOKEN.findall(original),TOKEN.findall(value))
                        numbers=lambda s: re.findall(r'\d+',unicodedata.normalize('NFKC',TOKEN.sub('',s)))
                        self.assertEqual(numbers(original),numbers(value))
                        self.assertLessEqual(max(map(len,body.splitlines())),max(map(len,TOKEN.sub('',original).splitlines())))
                        self.assertNotRegex(original,'ID_|ブランク|文章未定')

    def test_support_conditions(self):
        doc=read('translation/compiled/export_base/init/datskillhelp.bmd.json')
        text=lambda i: doc['texts'][i]['lines'][0]
        for i in [1013,1014]:
            self.assertIn('２倍以上',text(i))
            self.assertIn('仅１次',text(i))
            self.assertIn('３回合',text(i))
        for i,phrase in [(1007,'５回合'),(1083,'低概率'),(1084,'中等概率'),(1085,'高概率'),(1188,'魔封、力封与速封'),(1200,'即将降至０'),(1207,'强化与弱化'),(1208,'仅在使用当回合')]:
            self.assertIn(phrase,text(i))

    def test_accessory_distinctions(self):
        doc=read('translation/compiled/export_base/init/dataccessoryhelp.bmd.json')
        text=lambda i: doc['texts'][i]['lines'][0]
        self.assertIn('２０％',text(1))
        self.assertNotIn('％',text(6))
        self.assertIn('更不容易',text(51))
        self.assertIn('无效',text(53))
        self.assertIn('ＨＰ１存活',text(162))
        self.assertIn('ＨＰ完全恢复',text(163))
        for i in [164,165]:
            self.assertIn('１／２',text(i))
        for i in range(166,176):
            self.assertIn('交换',text(i))

    def test_accessory_tail_and_armor(self):
        doc=read('translation/compiled/export_base/init/dataccessoryhelp.bmd.json')
        original=read('export_base/init/dataccessoryhelp.bmd.json')
        text=lambda i: doc['texts'][i]['lines'][0]
        for i in range(179,188):
            self.assertIn('中等概率',text(i))
        self.assertIn('万能属性以外',text(188))
        self.assertIn('最大值',text(190))
        self.assertIn('减半',text(192))
        self.assertIn('２倍',text(192))
        for i in [255]:
            self.assertEqual(text(i),original['texts'][i]['lines'][0])
        for i,s in [(196,'神圣加护'),(197,'专心致志'),(198,'蓄力'),(199,'龙之咆哮')]:
            self.assertIn(s,text(i))
        armor=read('translation/compiled/export_base/init/datarmorhelp.bmd.json')
        self.assertIn('３Ａ',armor['texts'][4]['lines'][0])
        self.assertIn('减半',armor['texts'][15]['lines'][0])
        self.assertIn('２倍',armor['texts'][15]['lines'][0])

    def test_armor_serials_and_effects(self):
        armor=read('translation/compiled/export_base/init/datarmorhelp.bmd.json')
        original=read('export_base/init/datarmorhelp.bmd.json')
        text=lambda i: armor['texts'][i]['lines'][0]
        for i,n in [(114,'壹'),(115,'叁'),(116,'四'),(118,'七'),(119,'八'),(120,'九'),(122,'零'),(127,'贰'),(129,'五'),(130,'六'),(133,'十')]:
            self.assertIn('编号是'+n,text(i))
        for i in [137,182,233]:
            self.assertIn('减半',text(i))
            self.assertIn('２倍',text(i))
        self.assertIn('埃癸斯',text(136))
        self.assertIn('虎狼丸',text(181))
        self.assertIn('供善使用',text(232))
        self.assertIn('对应属性',text(139))
        self.assertIn('一定程度',text(183))
        self.assertEqual(text(255),original['texts'][255]['lines'][0])

    def test_weapon_effects(self):
        doc=read('translation/compiled/export_base/init/datweaponhelp.bmd.json')
        text=lambda i: doc['texts'][i]['lines'][0]
        for i in [30,90,152,200]:
            self.assertIn('减半',text(i))
            self.assertIn('２倍',text(i))
        for i,phrase in [(31,'麻痹毒'),(32,'毒药'),(88,'封印'),(89,'催眠孢子'),(91,'按钮')]:
            self.assertIn(phrase,text(i))
        self.assertNotIn('长柄',text(15))
        for i,phrase in [(92,'电击'),(151,'麻痹'),(153,'混乱'),(154,'注毒'),(202,'剧毒鳞粉')]:
            self.assertIn(phrase,text(i))
        self.assertIn('也许',text(129))

if __name__ == '__main__':
    unittest.main()
