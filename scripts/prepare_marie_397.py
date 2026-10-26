"""Marie incapacitation, low HP, petrification and poison."""
import hashlib
from collections import defaultdict
from compile_translation import ROOT,read,write,TOKEN
from prepare_margaret_393 import IDS
TEXT={
54:['哇！？副队长被打倒了！\n等等……谁能救救他？喂！','咦？副队长被打倒了！\n恢复呢？治疗呢？救救他啊！','哇！阳介被打倒了啊！\n恢复呢？救救他啊！','哇！千枝被打倒了！\n等等，谁能帮她恢复一下？','啊！雪子被打倒了！\n谁能治好她？救救她啊！','呃！完二被打倒了啊！\n快救救他！没法恢复吗？','哇！直斗被打倒了！！\n等等，恢复呢？谁能治好她？','哇！小熊被打倒了！\n不动了……还翻白眼……跟尸体一样……','咦！？由加莉被打倒了！\n谁、谁快救救她啊！','啊！顺平被打倒了啊！\n恢、恢复呢？不复活他吗？','咦！？真田被打倒了啊！\n快、快治好他啊！治不了吗？','哇！？美鹤被打倒了！？\n等等……谁能治好她？快治啊！','啊！埃癸斯被打倒了！？\n怎、怎么办？要救她吧？','哇！乾被打倒了啊！\n不、不复活他，或者恢复一下吗？','哇！狗狗被打倒了！\n快救它啊！用恢复什么的！','哇！荒垣被打倒了！\n谁、谁能恢复或者复活他？','哇！？善和玲被打倒了！\n复、复活呢？恢复呢？谁能帮忙？','哇！？善被打倒了！！\n等等，快治好他啊！谁来帮忙！','哇！？你被打倒了！？\n等等，谁快帮他恢复一下啊！','等等，队长被打倒了！？\n谁、谁快复活、恢复或者治疗啊！'],
55:['副队长没什么体力了。\n帮他恢复一下吧？','哇，副队长伤痕累累……\n谁快帮他恢复一下啊！','阳介是不是很不妙？\n都伤痕累累了。','千枝的体力没问题吗？\n少得也太离谱了……','雪子的体力太少了。\n恢复一下吧。','完二受伤太重了。\n那样没问题吗？','直斗的体力太少了。\n帮她恢复一下啊。','咦！？小熊摇摇晃晃的。\n体力是不是很危险？','等等……由加莉，没事吧？\n体力很危险啊……','顺平都站不稳了。\n不管他没问题吗？','真田的体力太少了。\n太离谱了。','美鹤……没事吧？\n体力也太少了……','埃癸斯的体力太少了。\n已经很危险了。','等等，乾的体力快见底了！\n已经站在死亡边缘了。','谁快治治狗狗啊！','荒垣没事吧？\n体力……好少。','善和玲的体力很危险。\n喂，快恢复一下啊。','善的体力很少。\n……太危险了。','等等！你受伤太重了。\n快恢复啊！','哇！？队长，\n伤得很重啊！快恢复！'],
56:['咦！？\n副队长变成石头了……','等等，副队长变成石头了！？\n这个……能治好吗？','等等……\n阳介变成石头了……','呜哇……\n千枝保持着架势变成石头了……','咦！？\n雪子变成石头了！？','哇！？\n完二变成石头了……','哇！？\n直斗变成石头了……','咦！？那边的摆件……\n难道是小熊？','哇！由加莉变成石头了……\n还能这样？','咦！？顺平变成石头了……\n这能治好吗？','咦！？\n真田变成石头了？','哇！？\n美鹤变成石头了！？','哇！？埃癸斯，\n变成石头了！？','等等……\n乾变成石头了……','咦！？狗狗变成石头了……\n不是摆件吧？','呜哇……\n荒垣被变成石头了……','哇！？善和玲，\n变成石头了……','哇！？\n善变成石头了……','哇！？\n你变成石头了！？','哇！\n队长变成石头了！？'],
57:['副队长中毒了。\n还是治好比较好吧？','副队长中毒了。\n放着不管不危险吗？','阳介没事吧？\n你中毒了吧？','千枝中毒了。\n不解毒吗？','雪子中毒了。\n治不好吗？','完二中毒了。\n还是先治好比较好吧？','直斗中毒了。\n没事吧？','啊……小熊中毒了……','由加莉中毒了。\n这个，治不好吗？','啊……顺平中毒了。\n这没问题吗？','真田中毒了。\n还是治好比较好吧？','美鹤中毒了。\n喂，治不好吗？','埃癸斯中毒了……\n……对机器人也有效的毒啊……','乾中毒了。\n治不好吗？','狗狗中毒了。\n等等，不管它也太可怜了。','荒垣中毒了。\n喂，治不好吗？','善和玲两个人都中毒了。\n不能解毒吗？','善中毒了……\n喂，治不好吗？','你中毒了吧？\n不解毒吗？','队长中毒了。\n快解毒啊。']}

def main():
    TEXT[54][IDS.index(8)]='哇！小熊被打倒了！\n不动了…还翻白眼…跟尸体一样…'
    TEXT[56][IDS.index(16)]='咦！？狗狗变石头…\n不是摆件吧？'
    TEXT[57][IDS.index(14)]='埃癸斯中毒了……\n…连机器人也会中毒啊…'
    path=ROOT/'translation/batches/397_marie_statuses_a.generated.json';assert not path.exists()
    catalog={r['key']:r for r in read(ROOT/'translation/catalog.working.json')};sources=defaultdict(list)
    for m,values in TEXT.items():
        assert len(values)==20
        source=f'export_dlc/0008/battle/support/bsv124.bvp_({m:03}).BMD.json';doc=read(ROOT/source)
        for i,body in zip(IDS,values):
            row=catalog[f'{source}:{i}:0'];assert not row.get('translation');body+='\n'
            a=TOKEN.sub('',row['original']).splitlines();b=body.splitlines()
            assert len(b)<=len(a) and max(map(len,b))<=max(map(len,a)),(m,i,max(map(len,b)),max(map(len,a)))
            sources[source].append([i,0,doc['texts'][i]['id'],body])
    write(path,dict(status='draft',sources=dict(sources),source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},review_notes=['玛丽054—057有效80页；保留昵称、狗狗称呼和石化调侃。','5/13占位保留，未宣称石化游戏内触发；尚未运行测试。']))
    print('Marie status pages:',sum(map(len,sources.values())))

if __name__=='__main__':main()
