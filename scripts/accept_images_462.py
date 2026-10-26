"""Register two visually inspected resources; no CPK or game packaging."""
import shutil
from compile_translation import ROOT,read,write
from reuse_menu_image_460 import sha

def main():
    files=[]
    for name in ['image_blocks_461.generated.json','image_gamecoin_462.generated.json']:
        d=read(ROOT/'translation'/name)
        original=ROOT/'data'/d['source']; trial=ROOT/d['output']
        assert sha(original)==d['source_sha256'] and sha(trial)==d['sha256']
        dest=ROOT/'full_work/reviewed_images_462'/d['source']
        dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists():assert sha(dest)==sha(trial),'Refuse to overwrite different reviewed asset'
        else:shutil.copy2(trial,dest)
        files.append(dict(source=d['source'],source_sha256=d['source_sha256'],output=dest.relative_to(ROOT).as_posix(),
                          sha256=sha(dest),blocks=d['blocks'],build_report=name,
                          visual_review='passed: Chinese label legible, button/icon and other graphics preserved',
                          runtime_tested=False))
    write(ROOT/'translation/images_462.accepted.json',dict(files=files,packaged=False,
          notes=['Only these two bitmap resources accepted offline. Original game and saves unchanged.',
                 'Small ETC1A4 errors inside edited blocks remain; all other bytes and decoded pixels preserved.',
                 'Earlier reports record pre-review status; this manifest records subsequent visual acceptance.',
                 'Final assembler does not yet consume this manifest; it must be explicitly integrated after remaining fixes.']))
    print('Accepted offline:',[f['source'] for f in files])

if __name__=='__main__':main()
