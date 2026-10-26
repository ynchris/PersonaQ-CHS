from compile_translation import ROOT,read,write
TITLES=['想要天使雕像','想要恶魔雕像','屋顶的那个女孩','想要利兹线','想要梦幻美酒','希望能和喜欢的人顺利交往','修理桌子','交换书籍','想要陈旧钥匙','卡门的课外教学・１','想要煤炭','改造桌子','希望能变得讨厌零食','请帮忙喂猫','想要十字架','想要气派的角','请帮忙找妹妹','成为姐姐之路','想要针银矿','寻找小狗','想要驱魔面纱','想要硬皮靴','迷途！谜语学长！','想要灯具','还是很在意猫','想要朋友','想要时髦的盘子','离姐姐只差一步','心灵感应实验','想找回生活的意义','卡门的课外教学・２','想要水晶球','想要煤炭・２','你还记得书的内容吗','送给父亲的礼物','想改掉不善言辞的毛病','想要高速齿轮','告别姐姐的身份','想要演习弹','最后的心灵感应','想习惯和猫相处','寻找掉落的钱','屋顶的那个女孩・２','送给父亲的礼物・２','想要古老矿石','想要灯具・２','觉醒！谜语学长！','想一睹七里海岸鱼王','仍然很在意猫','逆袭！谜语学长！','卡门的课外教学・３','想要一束黄金锁链','学生的本分是学业','柏木老师的特别教学・１','请继承清扫部之魂','复活！谜语学长！','想要稻羽鳟鱼','想要２种玉米','想要鲛川鱼王','非稻羽产卷心菜不可','代理派发纸巾','想了解电影里出现的东西','请找来喜欢的衣服','想看看那件令人心动的衣服','寻找我家的孩子','再次寻找我家的孩子','想看可爱的拖鞋','想看带软软肉球的手套','柏木老师的特别教学・２']
OTHER={'合体予報':'合体预报','救援ログ確認':'查看救援记录','救援ログ詳細':'救援记录详情','２枚目のイケニエを選んでください':'请选择第２个祭品','ストックに無いコミュ入手済アルカナのペルソナ':'未持有但已建立对应社群的人格面具'}
def main():
    p=ROOT/'translation/table_tail_448.review.json';assert not p.exists();entries=[]
    cat=read(ROOT/'translation/tables.catalog.working.json')
    for row in cat:
        if row['translation']:continue
        text=None
        if row['source']=='init/cmptable.bin' and row['member_index']==29:text=TITLES[row['row']]
        elif row['source']=='init/cmptable.bin' and row['member_index']==30:text=row['original'].replace('のヘルプ','说明')
        elif row['original'] in OTHER:text=OTHER[row['original']]
        if text is not None:entries.append(dict(row,translation=text,status='draft_table_reviewed'))
    assert len(entries)==79
    write(p,dict(entries=entries,review_notes=['补齐69个旧作委托标题、5个难度说明标签和5个设施条目。原占位SAFTY拼写保留，不擅自扩写成真正难度帮助。','保留余下9条空白/明确dummy，不从总表删除。术语沿用已译任务说明，未验证遗留资源可达性。']))
if __name__=='__main__':main()
