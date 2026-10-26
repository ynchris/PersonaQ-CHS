"""Reviewed compact wording for the remaining widest static event lines."""
from compile_translation import ROOT,read,write,TOKEN
from audit_layout_metrics import font_width_functions,measure

CHANGES={
'export_base/event/e000/e010_070.bf.json:1:0':[
('＞作为文化祭的活动场地，这里未免太宽敞了……','＞作为文化祭场地，这里也太宽敞了……')],
'export_base/event/e700/e723_215.bf.json:10:0':[
('＞配电盘旁贴着一张告示，\n　上面写着','＞配电盘旁贴着一张告示，\n　写着'),
('……！\n','\n　……！\n')],
'export_base/event/e800/e823_040.bf.json:6:3':[
('代表“东”','对应东'),('代表“南”','对应南'),('代表“西”','对应西'),('代表“北”','对应北')],
}

def main():
    audit=ROOT/'translation/layout_454.review.json';assert not audit.exists()
    path=ROOT/'translation/text_corrections.review.json';prior=read(path);existing={r['key'] for r in prior['rows']}
    catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')};widths=font_width_functions();rows=[]
    for key,changes in CHANGES.items():
        assert key not in existing
        row=catalog[key];before=row['translation'];after=before
        for old,new in changes:
            assert after.count(old)==1,(key,old)
            after=after.replace(old,new)
        assert TOKEN.findall(before)==TOKEN.findall(after)
        assert len(TOKEN.sub('',after).splitlines())<=len(TOKEN.sub('',row['original']).splitlines())
        assert all(measure(after,f[1])['max_width']<measure(before,f[1])['max_width'] for f in widths.values())
        rows.append(dict(key=key,original=row['original'],before=before,after=after,reason='454手工精简高宽度对白；保留含义、颜色及原行数上限，运行未验证'))
    write(audit,dict(rows=rows,runtime_tested=False));prior['rows'].extend(rows);write(path,prior)
    print('Reviewed compact event lines:',len(rows))

if __name__=='__main__':main()
