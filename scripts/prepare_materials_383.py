"""Finish informative material descriptions in one batch; cache references once."""
import hashlib
import re
import unicodedata
from collections import Counter
from compile_translation import ROOT, read, write, TOKEN, LEADING, TRAILING
from scan_latest_q2_myth import LATEST
from persona_names import load_drafts

TEXT = {
267:'带有圆环的黑色骰子形阴影的一部分。',268:'连同圆环在内，几乎保持原形的块状物。',269:'烧得通红的骰子形阴影块。',
270:'带有圆环的红色骰子形阴影的一部分。',271:'连同圆环在内，几乎保持原形的块状物。',
273:'拥有红色装甲的战车型阴影的一部分。',274:'耐久力极高的炮塔。',276:'携带剑与平衡器的阴影的一部分。',277:'巨人持有的大剑碎片。',278:'剑身开有大洞的巨人之剑。',279:'金色身体的阴影的一部分。',
298:'破损的扑克牌数字牌。',301:'被油漆弄脏的扑克牌数字牌。',304:'充满安宁的宝珠。',307:'黏稠的污泥。',310:'装着淡淡回忆的宝珠。',313:'充满憧憬的宝珠。',316:'脏兮兮的小奶嘴。',319:'人偶穿过的可爱和服。',322:'人偶穿过的陈旧和服。',325:'带有清爽香气的待客酒。',328:'带有馥郁香气的待客酒。',331:'闪闪发光的男子汉结晶。',334:'仿佛能传递热气的面具。',337:'凡事都迅速行动的男子汉生存之道。',340:'如今什么也没有映出的蜘蛛眼睛。',343:'蜘蛛吐出的黏性丝线。',346:'无人能够逃脱的、终结时间的信号。',368:'多处磨损的童话书。',371:'有被撕去书页痕迹的福音书。',374:'断成两截的老式体温计。',377:'缝线开绽的小马甲。',386:'金光闪闪的独角仙形阴影的一部分。',389:'金光闪闪的国王形阴影的一部分。',392:'金光闪闪的大脸阴影的一部分。',395:'金光闪闪、腹部为脸的阴影的一部分。',
512:'十分粗长的\n〈ヤマタノオロチ〉之尾。',513:'长在〈ピクシー〉背上的\n小翅膀。',514:'强度极高的\n巨大甲壳。',515:'像燃烧的火焰一样鲜红的羽毛。',516:'〈ジャックランタン〉持有的\n设计简洁的灯笼。',517:'〈ジン〉曾栖身的魔灯的一部分。',518:'尖锐的纯白爪子。',519:'将构成〈キングフロスト〉身体的雪\n压成的雪球。',520:'〈サキュバス〉释放的\n能魅惑他人的信息素。',521:'长在〈ヌエ〉手脚上的爪子。',522:'〈スカディ〉爱用的弓的一部分。',523:'〈マタドール〉持有的\n十分锋利的刺剑。',524:'染上海洋般深蓝色的鳞片。',525:'光泽艳丽的漆黑长发。',526:'〈オニ〉持有的铁棒的一部分。',527:'为力量强大的〈ゼウス〉量身打造的\n蓝色铠甲碎片。',528:'〈セト〉身上尖爪的一部分。',529:'〈ヨシツネ〉持有的刀的一部分。',530:'〈マサカド〉持有的刀的一部分。',531:'〈アスラおう〉的神圣骨骸。',532:'〈ヴィシュヌ〉持有的刀的一部分。',533:'〈セイテンタイセイ〉诞生的灵岩。',534:'〈カルティケーヤ〉所骑孔雀的羽毛。',535:'〈キングー〉持有的石板的一部分。',536:'长在〈サタン〉背上的\n巨大翅膀。',538:'长在〈メタトロン〉背上的\n纯洁美丽的翅膀。',539:'将〈シヴァ〉的愤怒具现化的\n神秘能量体。',540:'〈ミカエル〉持有的剑的一部分。',541:'〈シュウ〉持有的弓的一部分。',542:'供奉〈アリラト〉的神圣黑石。',543:'〈スカアハ〉持有的魔枪的一部分。',544:'将〈ロキ〉的苦难具现化的\n神秘能量体。',545:'〈ベルゼブブ〉持有的法杖碎片。',654:'阴影掉落的身体的一部分。',
656:'绘有松软蛋糕的插图碎片。',657:'绘有弹嫩蘑菇的插图碎片。',658:'绘有热腾腾馅饼的插图碎片。',659:'看不出像海龟的插图碎片。',660:'绘有幻想生物的插图碎片。',661:'绘有困倦老鼠的插图碎片。',662:'绘有戴礼帽男子的插图碎片。',663:'被胡椒烟雾笼罩得雪白的插图碎片。',664:'绘有尖下巴女子的插图碎片。',
668:'凋零得不成样子的白色古典玫瑰。',669:'凋零得不成样子的白色蝴蝶兰。',670:'凋零得不成样子的白色朱顶红。',671:'从中间断落的白色蜡烛。',672:'扣环损坏的白色蕾丝项饰。',673:'扣环损坏的珍珠项链。',674:'裂成两半的珍珠冠。',675:'裂成两半的珍珠耳环。',676:'裂成两半的玻璃鞋。',677:'从中间撕裂的长头纱。',678:'从中间撕裂的白色披肩。',679:'破损得惨不忍睹的纯白婚纱。',
684:'似乎是数学笔记本。',685:'似乎是理科教科书。',686:'似乎是社会科资料集。',687:'被撕碎而无法辨认的课程表。',688:'被撕碎而无法辨认的名牌。',689:'被撕碎而无法辨认图案的校徽。',690:'尖端生锈的粗注射针。',691:'刀刃锈得厉害的手术刀。',692:'尖端锈得厉害的镊子。',693:'染成暗红色的绷带。',694:'结成暗红色块状的纱布。',695:'脏得无法辨认的某人的病历。',
700:'带有微苦香气的熏香。',701:'带有甜美香气的熏香。',702:'带有高雅香气的熏香。',703:'标题写着２６０号的乐谱的一部分。',704:'标题写着６５７号的乐谱的一部分。',705:'标题写着５８１号的乐谱的一部分。',706:'花朵硕大的白百合。',707:'纯洁无瑕的康乃馨。',708:'盛开得仿佛要满溢的白菊。',709:'儿童用的纯白腰带。',710:'纯白的细蜡烛。',711:'白瓷壶的碎片。',
716:'浑浊得无法使用的水晶碎片。',717:'脏得无法使用的水晶碎片。',718:'有裂纹而无法使用的水晶碎片。',719:'缺齿而无法使用的发条。',720:'闪着银光的发条。',721:'闪着金光的发条。',722:'像是钟摆，却不会摆动。',723:'像是钟表的音叉，却无法使用。',724:'像是钟表的螺丝，却已被压坏。',725:'没有东西能与之啮合的小齿轮。',726:'没有装分针的齿轮。',727:'再也不会转动的大齿轮。',
740:'据说会将映入其中之物的性质\n反转后映出的镜子。',753:'在各个迷宫中找到的物品：白玫瑰、\n心形标记、注射器、绞纹头巾。'}

LOCAL_ENEMIES={'トランプの兵隊さん':'扑克牌士兵','バラを塗る兵隊さん':'涂玫瑰的士兵','愛の天使':'爱之天使','情欲の獣':'情欲之兽','恋の使者':'恋之使者','ロマンスの生き神様':'浪漫活神仙','かわいいあかちゃん':'可爱的小宝宝','可憐なお人形さん':'可爱的人偶','古ぼけたお人形さん':'陈旧的人偶','小若衆':'小若众','組頭':'组头','したたり野郎':'滴汗男','おまつり野郎':'祭典男','あしばや野郎':'快脚男','見張る者':'监视者','捕える者':'捕捉者','刈り取る者':'收割者','ハートの女王様':'红心女王','慈悲深い聖職者':'慈悲的圣职者','優しいドクター':'温柔的医生','おともだち':'小伙伴'}
LOCATIONS={'不思議の国のアナタ':'不可思议国度的你','ごーこんきっさ':'联谊咖啡厅','放課後悪霊クラブ':'放学后恶灵俱乐部','稲羽郷土展':'稻羽乡土展','時計塔':'钟塔','壱ノ怪':'第一怪','弐ノ怪':'第二怪','参ノ怪':'第三怪','四ノ怪':'第四怪','次会':'次会','階':'层'}

TEXT[331]='闪耀的男子汉结晶。'
TEXT[337]='行事迅捷的男子汉生存之道。'
LOCATIONS.update({'不思議の国のアナタ':'不可思议之国的你','放課後悪霊クラブ':'放学后的恶灵俱乐部'})

def main():
    target=ROOT/'translation/batches/383_materials_completion.generated.json'
    assert not target.exists()
    source='export_base/init/datmaterialhelp.bmd.json'
    doc=read(ROOT/source)
    catalog=read(ROOT/'translation/catalog.working.json')
    remaining={r['message_index']:r for r in catalog if r['source']==source and not r.get('translation') and not re.search(r'ID_|ダミ|ブランク|リザーブ|枠最後',r['original'])}
    assert set(remaining)==set(TEXT),set(remaining)^set(TEXT)
    reference=LATEST/'battle/table/enemynametable.tbl.json'
    refs=read(reference)
    _,names,translations=load_drafts()
    persona={names[i]:t for i,t in translations.items()}
    rows,audit=[],[]
    overflow=[]
    for i,text in TEXT.items():
        old=remaining[i]['original']
        jp=TRAILING.sub('',LEADING.sub('',old)).strip()
        used=re.findall('〈(.*?)〉',text)
        for name in used:
            assert name in jp
            text=text.replace('〈'+name+'〉',persona[name])
        matched=[]
        enemy=None
        if '\n討伐：' in jp:
            enemy=jp.split('\n討伐：')[1]
            matched=[r for r in refs if r['original']==enemy and r.get('translation')]
            variants={r['translation'] for r in matched}
            assert len(variants)<=1
            translated=next(iter(variants)) if variants else LOCAL_ENEMIES[enemy]
            text+='\n讨伐：'+translated
        elif '\n採集：' in jp:
            place=jp.split('\n採集：')[1]
            for a,b in LOCATIONS.items():
                place=place.replace(a,b)
            if '放学后的恶灵俱乐部' in place:
                place=place.replace('　','')
            text+='\n采集：'+place
        assert not re.search(r'[\u3041-\u3096\u30a1-\u30fa{}]',text),(i,text)
        nums=lambda s:Counter(re.findall(r'\d+',unicodedata.normalize('NFKC',TOKEN.sub('',s))))
        assert nums(text)==nums(jp),i
        assert len(text.splitlines())==len(jp.splitlines()),i
        if max(map(len,text.splitlines()))>max(map(len,jp.splitlines())):
            overflow.append((i,max(map(len,jp.splitlines())),text))
        value=text+'\n'
        rows.append([i,0,doc['texts'][i]['id'],value])
        audit.append({'index':i,'original':jp,'final_body':value,'enemy_name':enemy,
                      'enemy_references':[{k:r.get(k) for k in ['key','original','translation','stage']} for r in matched],
                      'persona_name_reuse':{n:persona[n] for n in used}})
    assert not overflow,overflow
    write(target,{'status':'draft','sources':{source:rows},'source_hashes':{source:hashlib.sha256((ROOT/source).read_bytes()).hexdigest()},
                  'review_notes':['一批补齐剩余129条非ID/预留素材说明，描述按一代翻译，敌名尽量复用二代；没有同名参考的本地草稿单列。','人格面具专名沿用已审校名称表，不重复翻译；未做全量构建或运行测试。']})
    write(ROOT/'translation/383_materials_completion.audit.generated.json',{'reference':str(reference.relative_to(ROOT.parent)),'reference_sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),'persona_draft_sha256':hashlib.sha256((ROOT/'translation/persona_names.review.json').read_bytes()).hexdigest(),'entries':audit,'runtime_tested':False})
    print(f'Prepared {len(rows)} descriptions; Q2 enemy names {sum(bool(e["enemy_references"]) for e in audit)}; existing Persona names {sum(bool(e["persona_name_reuse"]) for e in audit)}.')

if __name__=='__main__':
    main()
