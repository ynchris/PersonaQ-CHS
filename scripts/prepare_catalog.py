"""Create a stable translation catalog from PersonaEditor message exports."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def main():
    entries = []
    for path in sorted(list((ROOT / 'export_base').rglob('*.json')) + list((ROOT / 'export_dlc').rglob('*.json'))):
        data = json.loads(path.read_text(encoding='utf-8-sig'))
        if not isinstance(data, dict) or 'texts' not in data:
            continue
        rel = path.relative_to(ROOT).as_posix()
        for index, message in enumerate(data['texts']):
            for line_index, original in enumerate(message['lines']):
                entries.append(dict(key=f'{rel}:{index}:{line_index}', source=rel,
                    message_index=index, message_id=message['id'], line_index=line_index,
                    speaker=message.get('speaker', ''), original=original,
                    translation='', status='untranslated'))
    out = ROOT / 'translation'
    out.mkdir(exist_ok=True)
    target = out / 'catalog.generated.json'
    target.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'{len(entries)} message lines in {target}')
    print('Generated catalog only; translation edits belong in separate files.')

if __name__ == '__main__':
    main()
