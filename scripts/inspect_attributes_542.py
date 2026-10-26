from PIL import Image
from compile_translation import ROOT,read
out=ROOT/'translation/previews_542';out.mkdir(exist_ok=True)
im=Image.open(ROOT/'translation/feedback_541/decoded/camp_c_main.spr3.tex1.ctpk.00.png').convert('RGBA')
crop=im.crop((0,236,160,256));bg=Image.new('RGBA',crop.size,'#555555');bg.alpha_composite(crop)
bg.resize((960,120),Image.Resampling.NEAREST).save(out/'original_attributes.png')
mask=im.crop((1,238,156,255)).getchannel('A')
active=[x for x in range(mask.width) if mask.crop((x,0,x+1,mask.height)).getextrema()[1]>0]
runs=[]
for x in active:
    if not runs or x>runs[-1][-1]+1:runs.append([x+1,x+1])
    else:runs[-1][-1]=x+1
print('runs',runs)
for r in read(ROOT/'translation/feedback_541/camp_sprite_records.json'):
    b=r['box']
    if b[1]>=238 and b[3]<=256 and 0<b[2]<=160:print(r['index'],r['name'],b)
