"""Preview only: user approval is required before any texture encoding."""
from PIL import Image,ImageDraw,ImageFont
from compile_translation import ROOT,write

def main(folder_name='previews_466',numbers=(43,44),first_left=None):
    folder=ROOT/'translation'/folder_name;folder.mkdir(exist_ok=True)
    metrics=[]
    for n in numbers:
        original=Image.open(ROOT/f'export_base/tutorial/t{n:03d}.ctpk.00.png').convert('RGBA')
        # Retain the already reviewed drawing and top labels, without taking
        # pixels from a lossy re-export. Only the lower text panel is redrawn.
        previous=ROOT/f'full_work/images_464_8f186214/import/tutorial/t{n:03d}.ctpk.00.png'
        image=Image.open(previous).convert('RGBA')
        scale=4; y0=131 if n==43 else 112;bottom=168
        panel=Image.new('RGBA',(258*scale,(bottom-y0)*scale),'white')
        draw=ImageDraw.Draw(panel)
        font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',13*scale)
        def width(s):return draw.textlength(s,font=font)/scale
        def text(x,y,s,color):draw.text(((x-18)*scale,(y-y0)*scale),s,font=font,fill=color,anchor='lt')
        if n==43:
            left='方向键上下';right='前进／后退'
            total=width(left)+10+width(right)
            x=(294-total)/2 if first_left is None else first_left
            rx=x+width(left)+10
            text(x,133,left,'#0096f0');text(rx,133,right,'black')
            text(x,151,'方向键左右','#0096f0');text(rx,151,'转向','black')
        else:
            left='B键＋方向键上下';right='快速移动'
            total=width(left)+10+7+9+width(right)
            x=(294-total)/2;bx=x+width(left)+10;rx=bx+16
            text(x,114,left,'#0091e6');text(x,134,'B键＋L/R键','#0091e6')
            draw.line([((bx-18)*scale,7*scale),((bx+7-18)*scale,7*scale),((bx+7-18)*scale,32*scale),((bx-18)*scale,32*scale)],fill='black',width=4)
            text(rx,124,right,'black')
            green='B键＋摇杆'
            text(x,153,green,'#418c00');text(x+width(green)+10,153,'环视','black')
        image.paste(panel.resize((258,bottom-y0),Image.Resampling.LANCZOS),(18,y0))
        # Check that the console drawing and arrows above the caption were untouched.
        before=Image.open(previous).convert('RGBA')
        assert image.crop((0,0,512,y0)).tobytes()==before.crop((0,0,512,y0)).tobytes()
        image.save(folder/f't{n:03d}.ctpk.00.png')
        preview=image.crop((0,0,296,184)).resize((888,552),Image.Resampling.NEAREST)
        preview.save(folder/f't{n:03d}_preview.png')
        comparison=Image.new('RGB',(1184,368),'#202020')
        comparison.paste(original.crop((0,0,296,184)).resize((592,368),Image.Resampling.NEAREST),(0,0))
        comparison.paste(image.crop((0,0,296,184)).resize((592,368),Image.Resampling.NEAREST),(592,0))
        comparison.save(folder/f't{n:03d}_compare.png')
        metrics.append(dict(source=f'tutorial/t{n:03d}.ctpk',text_group_left=x,text_group_right=x+total,
                            text_group_center=x+total/2,font_pixels=13,font_weight='bold',console_scale_unchanged=True))
    write(folder/'review.json',dict(files=metrics,approval='pending',encoded=False,packaged=False,
          notes='Original on left, revised preview on right in *_compare.png. Do not run encoder before explicit user approval.'))

if __name__=='__main__':main()
