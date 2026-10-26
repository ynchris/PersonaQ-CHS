"""Separate current control-checked story drafts from the last packaged snapshot."""
from compile_translation import ROOT, read, write, TOKEN
import hashlib
from bmd_bytes import read_document
from raw_text_codec import encode_message

def main():
    rows=read(ROOT/'translation/catalog.working.json')
    current=read(ROOT/'translation/progress.generated.json')
    packaged=read(ROOT/'translation/packaged_set.generated.json')
    encoding_path=ROOT/'translation/font_encoding.hex.json'
    encoding=read(encoding_path) if encoding_path.exists() else None
    encoding_hash=hashlib.sha256(encoding_path.read_bytes()).hexdigest() if encoding else None
    result=[]
    for path in sorted((ROOT/'translation/story').glob('*.json')):
        draft=read(path)
        source=draft['source']
        assert hashlib.sha256((ROOT/source).read_bytes()).hexdigest()==draft['source_sha256'].lower()
        selected=[r for r in rows if r['source']==source and r['status']=='draft_control_checked']
        assert len(selected)==sum(map(len,draft['messages'].values()))
        for row in selected:
            assert TOKEN.findall(row['original'])==TOKEN.findall(row['translation'])
        binary_built=False
        binary_path=ROOT/'full_work/messages/payload'/source.removeprefix('export_base/').removesuffix('.json')
        if encoding and binary_path.exists():
            binary=read_document(binary_path)
            binary_built=all(binary['texts'][r['message_index']]['lines'][r['line_index']]==encode_message(r['translation'],encoding) for r in selected)
        result.append({'source':source,'draft_lines':len(selected),
                       'excluded_placeholders':draft.get('excluded_placeholder_indices',[]),
                       'source_hash_verified':True,'control_stream_verified':True,
                       'binary_built':binary_built,'runtime_tested':False})
    packaged_current=packaged['message_drafts']==current['translated_draft_lines'] and packaged.get('encoding_sha256')==encoding_hash
    route_pages = sum(len(scene['pages']) for p in (ROOT/'translation/route_drafts').glob('*.json') for scene in read(p)['scenes'].values())
    report={'status':'STORY_DRAFTS_PACKAGED_RUNTIME_UNTESTED' if packaged_current else 'STORY_DRAFTS_AHEAD_OF_PACKAGED_BUILD',
            'authored_route_difference_pages':route_pages,
            'new_story_lines':sum(r['draft_lines'] for r in result),
            'story_documents':len(result),'all_message_drafts':current['translated_draft_lines'],
            'last_packaged_message_drafts':packaged['message_drafts'],
            'font_capacity':read(ROOT/'translation/font_capacity_status.generated.json'),
            'scenes':result,'runtime_tested':False}
    write(ROOT/'translation/story_progress.generated.json',report)
    print(f'{report["new_story_lines"]} new story lines in {len(result)} scenes; latest packaged snapshot remains {packaged["message_drafts"]} messages.')

if __name__=='__main__':
    main()
