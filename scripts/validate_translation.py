import json
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
sys.stdout.reconfigure(encoding='utf-8')
source = json.loads((root/'test_json/difficultyselect.bin_difficultyselect.bmd.json').read_text(encoding='utf-8'))
translated = json.loads((root/'translation/difficultyselect.zh-Hans.json').read_text(encoding='utf-8'))
assert len(source['texts']) == len(translated['messages'])
missing = set()
count = 0
pattern = r'\{[0-9A-F ]+\}'
for message, lines in zip(source['texts'], translated['messages']):
    assert len(message['lines']) == len(lines)
    for old, new in zip(message['lines'], lines):
        assert re.findall(pattern, old) == re.findall(pattern, new)
        count += 1
        for char in re.sub(pattern, '', new):
            try:
                char.encode('cp932')
            except UnicodeEncodeError:
                missing.add(char)
print(f'Control sequences preserved in all {count} lines')
print('Characters requiring mapping:', ''.join(sorted(missing)))
