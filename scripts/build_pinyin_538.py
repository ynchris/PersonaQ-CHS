"""Build PQ1 native dictionary candidates, not game archives or executables.

Uses the same Rime single-character readings / frequency approach as PQ2.
Storage bytes must come from PQ1's frozen font map, NOT PQ2 CP932 characters.
"""
import hashlib
import json
import re
import struct
from itertools import product
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REF = ROOT.parent / 'references/PersonaQ2ChsLocalization'
OUT = ROOT / 'translation/ime_538'


def build():
    mapping = json.loads((ROOT/'translation/font_encoding.hex.json').read_text(encoding='utf-8'))
    variants = json.loads((REF/'files/zh_hans_2_kanji.json').read_text(encoding='utf-8'))
    readings = defaultdict(list)
    luna = REF/'pinyin_ime/sources/rime-luna-pinyin/luna_pinyin.dict.yaml'
    essay = REF/'pinyin_ime/sources/rime-essay/essay.txt'
    in_entries = False
    for line in luna.read_text(encoding='utf-8').splitlines():
        if line == '...':
            in_entries = True
            continue
        f = line.split('\t')
        if in_entries and len(f) >= 2 and len(f[0]) == 1 and re.fullmatch('[a-z]+', f[1]):
            probability = float(f[2][:-1])/100 if len(f) >= 3 and f[2].endswith('%') else 1
            readings[f[0]].append((f[1], probability))
    frequency = {}
    for line in essay.read_text(encoding='utf-8').splitlines():
        f = line.rsplit('\t', 1)
        if len(f) == 2 and len(f[0]) == 1 and f[1].isdigit():
            frequency[f[0]] = int(f[1])
    ranked = defaultdict(dict)
    missing = []
    for char, encoded in mapping.items():
        if not ('\u3400' <= char <= '\u9fff'):
            continue
        variant = variants.get(char, char)
        # Rime is a traditional dictionary: e.g. its ancient character 汉 is
        # read nv, whereas simplified 汉 must inherit modern 漢 (han).
        found = readings.get(variant) or readings.get(char)
        if not found:
            missing.append(char)
            continue
        raw = bytes.fromhex(encoded)
        assert len(raw) == 2 and not any(c in raw for c in [0, 10, 13])
        for key, probability in found:
            score = max(frequency.get(char, 0), frequency.get(variant, 0))*probability
            ranked[key][char] = max(ranked[key].get(char, 0), score)
    # Native PQ1 reserves two of its 80 slots for input and case variant.
    candidates = {k: sorted(v, key=lambda c: (-v[c], c))[:78] for k, v in sorted(ranked.items())}
    entries = {}
    for key, chars in candidates.items():
        for letters in product(*[(c.upper(), c) for c in key]):
            spelling = ''.join(letters)
            full = ''.join(chr(ord(c)+0xFEE0) for c in spelling).encode('cp932')
            entries[full] = chars
    data = bytearray()
    index = bytearray()
    for initial in sorted({k[:2] for k in entries}):
        index += initial + b'\0\0' + struct.pack('<I', len(data))
        for key in sorted(k for k in entries if k[:2] == initial):
            data += b'\x81\x97' + key + b'\r\n'
            for char in entries[key]:
                data += bytes.fromhex(mapping[char]) + b'\r\n'
    index += b'\0'*4 + struct.pack('<I', len(data)) + b'\0'*8
    # Size-bounded native parser: an extra NUL is read as an empty candidate.
    OUT.mkdir(exist_ok=True)
    (OUT/'pinyin_idx.tbl').write_bytes(index)
    (OUT/'pinyin_dat.txt').write_bytes(data)
    (OUT/'candidates.json').write_text(json.dumps(candidates, ensure_ascii=False, indent=2), encoding='utf-8')
    report = dict(status='native_dictionary_experiment_not_installed', readings=len(candidates),
                  candidate_links=sum(map(len,candidates.values())), missing_reading_characters=missing,
                  unique_characters=len(set(''.join(''.join(v) for v in candidates.values()))),
                  max_candidates=78, font_map_sha256=hashlib.sha256((ROOT/'translation/font_encoding.hex.json').read_bytes()).hexdigest(),
                  sources={str(p.relative_to(REF)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [luna,essay]},
                  dictionaries={name:hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in ['pinyin_idx.tbl','pinyin_dat.txt']},
                  game_archives_modified=False, executable_modified=False, runtime_verified=False)
    (OUT/'build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print({k:report[k] for k in ['readings','candidate_links','unique_characters']})
    print('Unmapped readings:', ''.join(missing))
    for k in ['ni','hao','zhong','lv','nv']:
        print(k, ''.join(candidates.get(k,[])[:12]))


if __name__ == '__main__':
    build()
