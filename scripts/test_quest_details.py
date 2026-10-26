import hashlib
import json
import re
import unittest
from pathlib import Path
from compile_translation import LEADING, TRAILING, TOKEN

ROOT=Path(__file__).resolve().parent
def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

class QuestDetailTests(unittest.TestCase):
    def test_stage_coverage_and_controls(self):
        b=read(ROOT/'translation/batches/347_quest_details_01_to_21.json')
        self.assertEqual(sum(map(len,b['sources'].values())),156)
        for s,rows in b['sources'].items():
            self.assertEqual(hashlib.sha256((ROOT/s).read_bytes()).hexdigest(),b['source_hashes'][s])
            old=read(ROOT/s);new=read(ROOT/'translation/compiled'/s)
            self.assertEqual([r[0] for r in rows],list(range(3,81)))
            for i,j,mid,body in rows:
                src=old['texts'][i]['lines'][j];dst=new['texts'][i]['lines'][j]
                self.assertEqual(old['texts'][i]['id'],mid)
                self.assertEqual(dst,LEADING.match(src).group()+body+TRAILING.search(src).group())
                self.assertEqual(TOKEN.findall(src),TOKEN.findall(dst))
                self.assertEqual(src.count('\n'),dst.count('\n'))
                self.assertEqual(re.findall(r'\d+',TOKEN.sub('',src)),re.findall(r'\d+',TOKEN.sub('',dst)))
            for i,m in enumerate(old['texts']):
                if i<3 or i>=178:
                    self.assertEqual(m,new['texts'][i])

    def test_remaining_stages_and_puzzle(self):
        b=read(ROOT/'translation/batches/348_quest_details_22_to_47.json')
        self.assertEqual(sum(map(len,b['sources'].values())),194)
        for s,rows in b['sources'].items():
            self.assertEqual(hashlib.sha256((ROOT/s).read_bytes()).hexdigest(),b['source_hashes'][s])
            old=read(ROOT/s);new=read(ROOT/'translation/compiled'/s)
            self.assertEqual([r[0] for r in rows],list(range(81,178)))
            for i,j,mid,body in rows:
                src=old['texts'][i]['lines'][j];dst=new['texts'][i]['lines'][j]
                self.assertEqual(old['texts'][i]['id'],mid)
                self.assertEqual(dst,LEADING.match(src).group()+body+TRAILING.search(src).group())
                self.assertEqual(TOKEN.findall(src),TOKEN.findall(dst))
                self.assertEqual(src.count('\n'),dst.count('\n'))
                self.assertEqual(re.findall(r'\d+',TOKEN.sub('',src)),re.findall(r'\d+',TOKEN.sub('',dst)))
            r={i:v for i,j,mid,v in rows}
            for i,words in {81:['３３２４２×'],98:['完二和顺平','加入队伍'],102:['魔封'],113:['圣火','风','北'],118:['疾风'],132:['光或暗'],135:['“う”属于Ａ','“え”属于Ｂ','“す”属于Ａ','“し”属于Ｂ','“ひ”属于Ａ','“び”属于Ｂ'],140:['８','西北'],151:['离开','融化'],160:['只带上']}.items():
                for word in words:
                    self.assertIn(word,r[i])
        a,c=list(b['sources'].values())
        self.assertEqual([x[0] for x,y in zip(a,c) if x[3]!=y[3]],[121,122,123])

    def test_route_and_mechanical_conditions(self):
        b=read(ROOT/'translation/batches/347_quest_details_01_to_21.json')
        a,c=list(b['sources'].values())
        self.assertEqual([x[0] for x,y in zip(a,c) if x[3]!=y[3]],[32,40,41,42])
        r={i:v for i,j,mid,v in a}
        for i,words in {10:['埃癸斯','加入队伍'],19:['由加莉','加入队伍'],23:['速封'],34:['小熊','方向','距离'],44:['３','休息'],47:['雪子','加入队伍'],68:['诅咒'],75:['真田','加入队伍']}.items():
            for word in words:
                self.assertIn(word,r[i])

if __name__=='__main__':
    unittest.main()
