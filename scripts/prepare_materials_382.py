"""Material descriptions with exact-original Q2 enemy-name reuse, not fuzzy prose reuse."""
import hashlib
import re
import unicodedata
from collections import Counter
from compile_translation import ROOT, read, write, LEADING, TRAILING, TOKEN
from scan_latest_q2_myth import LATEST

DESCRIPTIONS = {
194:'３个头连在一起的阴影的一部分。',195:'用大量宝石装饰的王冠。',196:'散发强大魔力的眼睛。',
197:'手持拐杖的老人形阴影的一部分。',198:'雅致的紫色短褂。',199:'设计简洁的棕色拐杖。',
200:'手持拐杖的老人形阴影的一部分。',201:'洋溢着青春气息的绿色短褂。',
203:'悬挂在圆盘上的阴影的一部分。',204:'束缚阴影身体的枷锁。',205:'封存着魔力的尖刺。',
206:'黑色骰子形阴影的一部分。',207:'决定投掷者命运的骰子点数。',
209:'白色骰子形阴影的一部分。',210:'几乎保持原形的骰子块。',211:'决定投掷者宿命的骰子点数。',
212:'带有狮子脸的车轮形阴影的一部分。',213:'支撑巨大车轮的坚固车轴。',214:'缠绕着风的蓬松尾巴。',
215:'带有狮子脸的车轮形阴影的一部分。',216:'支撑巨大车轮的极其坚固的车轴。',217:'清爽的青白色鬃毛。',
218:'腹部是一张脸的阴影的一部分。',219:'仿佛能砸碎一切的巨大铁锤。',221:'金色身体的阴影的一部分。',
239:'从Ｆ．Ｏ．Ｅ身上得到的黑色兜裆布。\n不知本来就是黑色，还是被弄脏了。',
240:'牛头人身的阴影的一部分。',241:'连接颈枷与手枷的锁链。',242:'被冰封的雄伟犄角。',
243:'展开术符的阴影的一部分。',244:'散发高贵气息的纯白披风。',245:'辅助施展高深魔术的法杖。',
246:'形似山巅城堡的阴影的一部分。',247:'被破坏的城墙碎片。',248:'身体各处炮台的炮管部分。',
249:'骑马骑士形阴影的一部分。',250:'为驾驭马匹而制作的特制缰绳。',251:'拥有贯穿坚硬铠甲威力的骑枪。',
252:'双臂为剑的阴影的一部分。',253:'带有３条黑色腿的车轮。',254:'阴影手臂部位的剑刃碎片。',
255:'双臂为骑枪的阴影的一部分。',256:'带有３条白色腿的车轮。',257:'发出耀眼光芒的齿轮。',
258:'拥有银色装甲的战车型阴影的一部分。',259:'耐久力很高的炮塔。',260:'受黑暗力量影响而漆黑的车轮。',
261:'骑着黑色木马的阴影的一部分。',262:'束缚６只手的枷锁。',263:'连接各个枷锁的锁链。',
264:'骑着白色木马的阴影的一部分。',265:'束缚６只手的枷锁。'}

def main():
    target=ROOT/'translation/batches/382_materials_q2_enemy_names.generated.json'
    assert not target.exists(), 'Refusing to overwrite batch'
    source='export_base/init/datmaterialhelp.bmd.json'
    current={r['key']:r for r in read(ROOT/'translation/catalog.working.json')}
    doc=read(ROOT/source)
    reference=LATEST/'battle/table/enemynametable.tbl.json'
    refs=read(reference)
    rows,audit=[],[]
    for mi,description in DESCRIPTIONS.items():
        key=f'{source}:{mi}:0'
        assert not current[key].get('translation'), key
        original=doc['texts'][mi]['lines'][0]
        stripped=TRAILING.sub('',LEADING.sub('',original)).strip()
        matches=[]
        if '\n討伐：' in stripped:
            enemy=stripped.split('\n討伐：')[1]
            matches=[r for r in refs if r['original']==enemy and r.get('translation')]
            variants={r['translation'] for r in matches}
            assert len(variants)==1,(mi,enemy,variants)
            value=description+'\n讨伐：'+next(iter(variants))+'\n'
        else:
            assert mi==239
            value=description+'\n'
        assert not re.search(r'[\u3041-\u3096\u30a1-\u30fa{}]',value)
        nums=lambda s:Counter(re.findall(r'\d+',unicodedata.normalize('NFKC',TOKEN.sub('',s))))
        assert nums(value)==nums(original),mi
        assert len(value.splitlines())==len(stripped.splitlines()),mi
        assert max(map(len,value.splitlines()))<=max(map(len,stripped.splitlines())),mi
        rows.append([mi,0,doc['texts'][mi]['id'],value])
        audit.append({'key':key,'original':stripped,'final_body':value,
                      'description_method':'translated_from_PQ1',
                      'enemy_name_references':[{k:r.get(k) for k in ['key','original','translation','stage']} for r in matches]})
    write(target,{'status':'draft','sources':{source:rows},
                  'source_hashes':{source:hashlib.sha256((ROOT/source).read_bytes()).hexdigest()},
                  'review_notes':['素材194—265中52条未译有效说明，跳过ID占位和已译条目。',
                                  '描述依据一代原文直译；51条讨伐对象按同日文敌名复用二代，1条FOE兜裆布无敌名。',
                                  '只复用名称，不把整段说明冒充二代复用；未验证游戏内出现与布局。']})
    write(ROOT/'translation/382_materials_q2_enemy_names.audit.generated.json',{
        'reference':str(reference.relative_to(ROOT.parent)),
        'reference_sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),
        'reference_commit':'15ca3ffda260133bfb090fc8a5b5ea896553f37c','entries':audit,'runtime_tested':False})
    print(f'Prepared {len(rows)} material descriptions; {sum(bool(r["enemy_name_references"]) for r in audit)} exact enemy-name reuse rows.')

if __name__=='__main__':
    main()
