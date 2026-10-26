"""Preview the revised decoded textures; no game-resource mutation."""
from PIL import Image
from compile_translation import ROOT,read

def main():
    data=read(ROOT/'translation/images_464.generated.json')
    folder=ROOT/'translation/previews_465';folder.mkdir(exist_ok=True)
    for item in data['files']:
        image=Image.open(ROOT/item['preview'])
        name=item['source'].split('/')[-1].replace('.ctpk','.png')
        # Fiction uses the original 400x240 game canvas; tutorial previews
        # crop only unused atlas padding, not the illustration itself.
        crop=(0,0,400,240) if name=='fiction.png' else (0,0,296,184)
        image.crop(crop).resize(((crop[2]-crop[0])*2,(crop[3]-crop[1])*2),Image.Resampling.NEAREST).save(folder/name)
    print(folder)

if __name__=='__main__':main()
