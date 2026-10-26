import hashlib
from compile_translation import ROOT,read,write,TOKEN,LEADING,TRAILING

TEXT={434:'战斗开始时，有中等概率\n获得隐身斗篷的效果。\n',
690:'驱魔护符：降低遇敌率。\n',691:'招魔符：提高遇敌率。\n',
694:'悬浮凉鞋：免疫地板伤害。\n',700:'驱魔铃：大幅降低遇敌率。\n',
701:'集魔之笛：大幅提高遇敌率。\n',1205:'加快刻命齿轮引发的\n死亡倒计时。\n'}

def main():
    target=ROOT/'translation/batches/427_skillhelp_effects.generated.json';assert not target.exists()
    s='export_base/init/datskillhelp.bmd.json';doc=read(ROOT/s)
    catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')};rows=[]
    for i,body in TEXT.items():
        r=catalog[f'{s}:{i}:0'];assert not r.get('translation');old=r['original']
        full=LEADING.match(old).group()+body+TRAILING.search(old).group()
        assert TOKEN.findall(full)==TOKEN.findall(old)
        a=TOKEN.sub('',old).splitlines();b=TOKEN.sub('',full).splitlines()
        assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),(i,a,b)
        rows.append([i,0,doc['texts'][i]['id'],body])
    write(target,dict(status='draft',sources={s:rows},source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest()},review_notes=['补译7条有明确效果描述的技能帮助，不改动内部执行标签和dummy。','沿用本地已审术语：隐身斗篷、驱魔护符、招魔符、悬浮凉鞋、驱魔铃、集魔之笛、刻命齿轮；不是7条Q2整句复用。','保留中概率、遇敌率增减及大幅程度。未验证运行时可达性。']))
    print('Skill effect help pages:',len(rows))

if __name__=='__main__':main()
