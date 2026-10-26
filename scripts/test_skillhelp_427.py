import unittest
import test_facility_423 as common
from compile_translation import ROOT,read
from reviewed_test_expectations import authored_translation

class SkillHelpTests(common.FacilityTutorialTests):
    batch_name='427_skillhelp_effects.generated.json'
    page_count=7
    def test_effects_and_preserved_rows(self):
        s='export_base/init/datskillhelp.bmd.json'
        old=read(ROOT/s);new=read(ROOT/'translation/compiled'/s)
        expected={434:'中等概率',690:'降低遇敌率',691:'提高遇敌率',694:'免疫地板伤害',700:'大幅降低遇敌率',701:'大幅提高遇敌率',1205:'死亡倒计时'}
        for i,phrase in expected.items():self.assertIn(phrase,new['texts'][i]['lines'][0])
        for i in (141,148,173,359,503,614,622,935,1212):
            self.assertEqual(old['texts'][i]['id'],new['texts'][i]['id'])
            self.assertEqual(old['texts'][i]['speaker'],new['texts'][i]['speaker'])
            self.assertEqual(len(old['texts'][i]['lines']),len(new['texts'][i]['lines']))
            for j,line in enumerate(old['texts'][i]['lines']):
                self.assertEqual(authored_translation(s,i,j,line),new['texts'][i]['lines'][j])

if __name__=='__main__':unittest.main()
