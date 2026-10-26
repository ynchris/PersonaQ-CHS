"""Resolve exported nested BIN/ARC/GSD names and preserve non-text bytes."""
import struct
from collections import defaultdict
from check_roundtrip import parse_members
from repack_bf_text import replace_text


def resolve(rows, selector):
    names = [name for name, _ in rows]
    if selector in names:
        if names.count(selector) != 1:
            copies = [data for name, data in rows if name == selector]
            # gcs.bin stores the same question BMD twice. Only byte-identical
            # BMD duplicates are safe to read/write as one exported document.
            if not selector.lower().endswith('.bmd') or any(data != copies[0] for data in copies):
                raise ValueError(f'Ambiguous duplicate container member: {selector}')
        return selector, None
    candidates = [name for name in names
                  if name.lower().endswith(('.bin', '.arc', '.gsd'))
                  and selector.startswith(name + '_')]
    if len(candidates) != 1:
        raise ValueError(f'Missing or ambiguous nested text member: {selector}')
    name = candidates[0]
    return name, selector[len(name) + 1:]


def extract_nested(data, selector):
    rows = parse_members(data, allow_padding=True)
    name, child = resolve(rows, selector)
    payload = dict(rows)[name]
    return payload if child is None else extract_nested(payload, child)


def replace_nested(original, rebuilt, changes):
    """Replace selected BMDs/BF text sections, never rebuilt sibling resources."""
    before = parse_members(original, allow_padding=True)
    after = parse_members(rebuilt, allow_padding=True)
    selected = defaultdict(set)
    for selector in changes:
        name, child = resolve(before, selector)
        if resolve(after, selector) != (name, child):
            raise ValueError('Rebuilt nested member resolution changed')
        if sum(n == name for n, _ in before) != sum(n == name for n, _ in after):
            raise ValueError('Rebuilt selected member count changed')
        selected[name].add(child)
    replacements = dict(after)
    result, pos, preserved = bytearray(original[:4]), 4, 0
    for name, old in before:
        new = old
        if name in selected:
            children = selected[name]
            if None in children:
                if children != {None}:
                    raise ValueError('Cannot replace both a container and its children')
                if name.lower().endswith('.bf'):
                    new, kept = replace_text(old, replacements[name])
                    preserved += kept
                elif name.lower().endswith('.bmd'):
                    new = replacements[name]
                else:
                    raise ValueError(f'Refusing non-text replacement: {name}')
            else:
                new, kept = replace_nested(old, replacements[name], children)
                preserved += kept
        else:
            preserved += 1
        result += original[pos:pos+32] + struct.pack('<I', len(new)) + new
        pos += 36 + len(old)
    # Preserve zero/header-copy alignment tails outside the final GSD member.
    result += original[pos:]
    actual = parse_members(result, allow_padding=True)
    assert [n for n, _ in before] == [n for n, _ in actual]
    assert all(a == b for a, b in zip(before, actual) if a[0] not in selected)
    return bytes(result), preserved
