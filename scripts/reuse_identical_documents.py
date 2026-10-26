"""Reuse only explicitly selected byte-identical exported documents."""
from compile_translation import ROOT, read, write, LEADING, TRAILING

def main():
    pairs=[('export_base/camp/skladd.arc_msg_support_skill.bmd.json',
            'export_base/facility/msg_support_skill.bmd.json')]
    reference='export_dlc/0005/battle/support/bsv123.bvp_(051).BMD.json'
    pairs.extend((reference,target) for target in [
        'export_base/battle/support/bsv105.bvp_(051).BMD.json',
        'export_dlc/0006/battle/support/bsv121.bvp_(051).BMD.json',
        'export_dlc/0007/battle/support/bsv122.bvp_(051).BMD.json',
        'export_dlc/0008/battle/support/bsv124.bvp_(051).BMD.json',
        'export_dlc/0009/battle/support/bsv125.bvp_(051).BMD.json'])
    catalog=read(ROOT/'translation/catalog.working.json')
    sources={}
    for original,target in pairs:
        assert (ROOT/original).read_bytes()==(ROOT/target).read_bytes(), 'Sources are not identical'
        rows=[r for r in catalog if r['source']==original and r['status']=='draft_control_checked']
        assert rows
        sources[target]=[[r['message_index'],r['line_index'],r['message_id'],
                          TRAILING.sub('',LEADING.sub('',r['translation']))] for r in rows]
    write(ROOT/'translation/batches/019_identical_documents.generated.json',{
        'status':'draft','sources':sources,'provenance_pairs':pairs,
        'reuse_rule':'Original exported files must match byte-for-byte'})
    print(f'Reused {sum(map(len,sources.values()))} existing draft lines in {len(sources)} exact duplicate documents.')

if __name__=='__main__':
    main()
