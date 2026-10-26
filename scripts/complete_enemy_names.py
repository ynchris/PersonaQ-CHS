"""Complete the enemy name category, retaining blank slots and provenance."""
import hashlib
from compile_translation import ROOT,read,write,TOKEN
from q2_name_banks import DRAFT

EXTRA=ROOT/'translation/enemy_names_completion.review.json'
LOCAL={'おとなしいナース':'文静的护士','世話好きなナース':'热心的护士','凍氷脚':'冻冰脚','堕落の塔':'堕落之塔','太刀風脚':'刀风脚','捕らえる者':'捕获者','時計仕掛けの神':'钟表机关之神','狂炎脚':'狂炎脚','玲を宿す蜘蛛':'寄宿着玲的蜘蛛','紫電雷脚':'紫电雷脚','黒ウサギ':'黑兔'}

def main():
    assert not EXTRA.exists()
    group=read(DRAFT)['groups'][0]
    assert group['source']=='battle/table/enemynametable.tbl'
    materials=[r for r in read(ROOT/'translation/catalog.working.json') if r['source']=='export_base/init/datmaterialhelp.bmd.json' and r.get('translation')]
    rows=[]
    for r in group['excluded']:
        name=r['original']
        if name=='ｂｌａｎｋ' or r['reason']=='placeholder_or_internal':continue
        matches=[x for x in materials if '討伐：'+name+'\n' in x['original']]
        if matches:
            values={TOKEN.sub('',x['translation']).strip().split('讨伐：')[-1] for x in matches}
            assert len(values)==1
            value=values.pop();origin=[x['key'] for x in matches]
        else:value=LOCAL[name];origin=[]
        rows.append(dict(index=r['index'],original=name,translation=value,local_catalog_references=origin,references=[]))
    write(EXTRA,dict(source=group['source'],source_sha256=group['source_sha256'],rows=rows,runtime_tested=False))
    print('Completed enemy slots:',len(rows),'unique names:',len({r['original'] for r in rows}))

if __name__=='__main__':main()
