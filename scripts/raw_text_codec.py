"""Strict byte-addressed display and message codecs."""
import re
from compile_translation import TOKEN
from plan_raw_font import valid_pair


def validate(mapping):
    values = [bytes.fromhex(v) for v in mapping.values()]
    if len(set(values)) != len(values):
        raise ValueError('Duplicate glyph encoding')
    for raw in values:
        if not ((len(raw)==1 and 0x20<=raw[0]<0x80) or (len(raw)==2 and valid_pair(int.from_bytes(raw,'big')))):
            raise ValueError('Invalid display encoding')


def encode_display(text, mapping):
    result=bytearray()
    for char in text:
        if char in mapping:
            result+=bytes.fromhex(mapping[char])
        elif char in '\n\r\t' or 0x20<=ord(char)<0x80:
            result+=char.encode('ascii')
        else:
            raise ValueError(f'Unmapped character: {char!r}')
    return bytes(result)


def decode_display(raw, mapping):
    reverse={bytes.fromhex(v):k for k,v in mapping.items()}
    result=[]
    pos=0
    while pos<len(raw):
        length=2 if raw[pos]>=0x80 else 1
        code=raw[pos:pos+length]
        if code in reverse:
            result.append(reverse[code])
        elif length==1 and (code[0] in (9,10,13) or 0x20<=code[0]<0x80):
            result.append(code.decode('ascii'))
        else:
            raise ValueError(f'Unknown display code at {pos}: {code.hex()}')
        pos+=length
    return ''.join(result)


def literal_message(text, mapping):
    result=[]
    for part in re.split('('+TOKEN.pattern+')',text):
        if TOKEN.fullmatch(part):
            result.append(part)
        else:
            # Escape ASCII too: literal braces must not be reinterpreted as controls.
            for char in part:
                raw=encode_display(char,mapping)
                result.append('\n' if char=='\n' else '{'+raw.hex(' ').upper()+'}')
    return ''.join(result)


def encode_message(text, mapping):
    return b''.join(bytes.fromhex(part[1:-1]) if TOKEN.fullmatch(part) else encode_display(part,mapping)
                    for part in re.split('('+TOKEN.pattern+')',text))
