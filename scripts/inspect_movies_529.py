"""Read-only movie sampling; write frames and diagnostic sheets, never game files."""
import json,subprocess,sys
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
FF=ROOT.parent/'tools/ffmpeg_runtime/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
out=ROOT/'translation/movie_inspection_529';out.mkdir(exist_ok=True)
full='--full' in sys.argv
if full:out=out/'full';out.mkdir(exist_ok=True)
rows=[]
for p in sorted((ROOT/'data/movie').glob('*.usm')):
    target=out/(p.stem+'_%02d.png')
    cmd=[str(FF),'-hide_banner','-loglevel','warning','-y','-i',str(p),'-vf','fps=1/8' if full else 'fps=1/3','-frames:v','80' if full else '4',str(target)]
    r=subprocess.run(cmd,capture_output=True,text=True,timeout=45)
    frames=list(out.glob(p.stem+'_*.png'))
    rows.append(dict(source=p.relative_to(ROOT).as_posix(),returncode=r.returncode,log=r.stderr[-2000:],frames=[q.relative_to(ROOT).as_posix() for q in frames]))
    print(p.name,'frames',len(frames),'return',r.returncode,flush=True)
    if full and frames:
        sheet=Image.new('RGB',(800,((len(frames)+3)//4)*135),'#222222');sd=ImageDraw.Draw(sheet)
        for i,q in enumerate(frames):
            im=Image.open(q).convert('RGB');im.thumbnail((200,120));x=i%4*200;y=i//4*135
            sheet.paste(im,(x,y));sd.text((x,y+120),q.stem,fill='white')
        sheet.save(out/(p.stem+'_sheet.png'))
canvas=Image.new('RGB',(800,len(rows)*135),'#222222');d=ImageDraw.Draw(canvas)
for y,row in enumerate(rows):
    for x,rel in enumerate(row['frames'][:4]):
        im=Image.open(ROOT/rel).convert('RGB');im.thumbnail((200,120));canvas.paste(im,(x*200,y*135))
    d.text((0,y*135+120),Path(row['source']).name,fill='white')
canvas.save(out/'movie_samples.png')
(out/'report.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
