from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parent
out=root/'translation/previews_493';out.mkdir(exist_ok=True)
paths=[root/'export_base/event/skip_btn.spr3.00.png',root.parent/'references/PersonaQ2ChsLocalization-latest-20260928/files/images/Graphic2D/Event/SkipButton/evtSkipButton.tpc_evtSkipButton_00.ctpk.00.png']
canvas=Image.new('RGB',(648,264),'white')
for i,p in enumerate(paths):
    im=Image.open(p).convert('RGBA').crop((105,9,186,42)).resize((648,264),Image.Resampling.NEAREST)
    im.save(out/f'icon_inspect_{i}.png')
