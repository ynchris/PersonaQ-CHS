"""Only revise t043; keep user-approved t044 PNG unchanged."""
from preview_tutorials_466 import main
from compile_translation import ROOT,write
from reuse_menu_image_460 import sha

if __name__=='__main__':
    approved=ROOT/'translation/previews_466/t044.ctpk.00.png'
    digest=sha(approved)
    main(folder_name='previews_467',numbers=(43,),first_left=35)
    assert sha(approved)==digest
    write(ROOT/'translation/previews_467/approval_record.json',dict(
        approved_source='tutorial/t044.ctpk',approved_png=approved.relative_to(ROOT).as_posix(),sha256=digest,
        authority='User explicitly approved second image after previews_466.',
        pending_source='tutorial/t043.ctpk',pending_png='translation/previews_467/t043.ctpk.00.png',
        note='Blue 向 character centered approximately x54.5 below arrow tail; only lower text group moved left. No encoding performed.'))
