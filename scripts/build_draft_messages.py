"""Build current draft BMDs, preserve sibling assets, and verify decoded output."""
import copy
import hashlib
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path
from build_sample import run, DOTNET, HELPER
from compile_translation import read, write, TOKEN
from repack_bf_text import replace_text
from repack_bvp_text import replace_members
from nested_text_members import replace_nested
from bmd_bytes import read_document
from raw_text_codec import validate, encode_message
from message_snapshot import scope_snapshot

ROOT=Path(__file__).resolve().parent

def literal_bytes(line):
    parts=[]
    for part in re.split('('+TOKEN.pattern+')',line):
        if TOKEN.fullmatch(part):
            parts.append(part)
        else:
            for ch in part:
                raw=ch.encode('cp932')
                if len(raw)==2:
                    assert raw[0]<0xf0, f'Control-range lead byte: {ch!r}'
                    parts.append('{'+raw.hex(' ').upper()+'}')
                else:
                    parts.append(ch)
    return ''.join(parts)

def main(scope='base'):
    assert scope=='base' or scope in {'0005','0006','0007','0008','0009'}
    input_snapshot=scope_snapshot(scope)
    prefix='export_base' if scope=='base' else 'export_dlc/'+scope
    data_root=ROOT/'data' if scope=='base' else ROOT/'dlc'/('content_'+scope)/'data'
    rows=[r for r in read(ROOT/'translation/catalog.working.json') if r['status']=='draft_control_checked' and r['source'].startswith(prefix+'/')]
    assert rows, 'No drafts in selected scope'
    encoding_path=ROOT/'translation/font_encoding.hex.json'
    encoding=read(encoding_path)
    validate(encoding)
    docs={}
    groups=defaultdict(set)
    expected={}
    for r in rows:
        source=r['source']
        if source not in docs:
            docs[source]=copy.deepcopy(read(ROOT/'translation/compiled'/source))
        docs[source]['texts'][r['message_index']]['lines'][r['line_index']]=r['translation']
    stage=ROOT/'full_work/messages' if scope=='base' else ROOT/'full_work/dlc_messages'/scope
    for source,doc in docs.items():
        rel=Path(source).relative_to(prefix)
        exported=rel.name.removesuffix('.json')
        match=re.match(r'^(.*?\.(?:bin|arc|gsd|bvp))_(.+)$',exported)
        container,member=(match[1],match[2]) if match else (exported,None)
        if member is not None and not member.lower().endswith(('.bmd','.bf')):
            raise ValueError(f'Unsupported nested format: {source}')
        groups[(rel.parent.as_posix(),container)].add(member)
        incoming_doc=copy.deepcopy(doc)
        original_doc=read(ROOT/source)
        binary=read_document(data_root/rel.parent/container,member)
        assert len(binary['texts'])==len(doc['texts'])
        assert len(binary['speakers'])==len(doc['speakers'])
        for r in rows:
            if r['source']==source:
                mi,li=r['message_index'],r['line_index']
                assert binary['texts'][mi]['id']==doc['texts'][mi]['id']
                binary['texts'][mi]['lines'][li]=encode_message(r['translation'],encoding)
        for i,name in enumerate(doc['speakers']):
            if name!=original_doc['speakers'][i]:
                binary['speakers'][i]=encode_message(name,encoding)
        # Preserve every untranslated byte, including codes that a text decoder
        # cannot round-trip. Feed literal bytes to the helper, bypassing .NET CP932.
        def literal(raw):
            return '{'+raw.hex(' ').upper()+'}' if raw else ''
        for i,message in enumerate(incoming_doc['texts']):
            assert len(message['lines'])==len(binary['texts'][i]['lines'])
            message['lines']=[literal(raw) for raw in binary['texts'][i]['lines']]
        incoming_doc['speakers']=[literal(raw) for raw in binary['speakers']]
        write(stage/'json'/rel,incoming_doc)
        expected[rel.as_posix()]=(binary,rel.parent/container,member)
        incoming=stage/'input'/rel.parent/container
        incoming.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(data_root/rel.parent/container,incoming)
    run([DOTNET,HELPER,'import','-i',stage/'input','-j',stage/'json','-o',stage/'rebuilt'])
    report=[]
    for (parent,container),changed in groups.items():
        original=data_root/parent/container
        rebuilt=stage/'rebuilt'/parent/container
        output=stage/'payload'/parent/container
        output.parent.mkdir(parents=True,exist_ok=True)
        if changed=={None}:
            if container.endswith('.bf'):
                data,preserved=replace_text(original.read_bytes(),rebuilt.read_bytes())
                output.write_bytes(data)
            else:
                shutil.copy2(rebuilt,output)
                preserved=0
        elif container.endswith('.bvp'):
            data,preserved=replace_members(original.read_bytes(),rebuilt.read_bytes(),changed)
            output.write_bytes(data)
        else:
            data,preserved=replace_nested(original.read_bytes(),rebuilt.read_bytes(),changed)
            output.write_bytes(data)
        report.append({'file':f'{parent}/{container}','preserved_members':preserved,'sha256':hashlib.sha256(output.read_bytes()).hexdigest()})
    for rel,(binary,container,member) in expected.items():
        actual=read_document(stage/'payload'/container,member)
        assert actual==binary,f'Byte-level roundtrip mismatch: {rel}'
    report_name='message_build.generated.json' if scope=='base' else 'dlc_'+scope+'_message_build.generated.json'
    assert scope_snapshot(scope)==input_snapshot, 'Translation inputs changed during build'
    write(ROOT/'translation'/report_name,{'scope':scope,'translation_input_sha256':input_snapshot,'draft_lines':len(rows),'documents':len(docs),'files':report,'roundtrip_verified':True,'byte_level_verified':True,'encoding_sha256':hashlib.sha256(encoding_path.read_bytes()).hexdigest(),'runtime_tested':False})
    print(f'Verified {len(rows)} draft lines across {len(docs)} documents; runtime not tested.')

if __name__=='__main__':
    main(sys.argv[1] if len(sys.argv)>1 else 'base')
