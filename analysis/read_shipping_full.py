"""R1369: read both getShippingMethods handlers in full, since the last look was truncated.

R1368's lesson was that a limited read is not an absence. The earlier probe printed the first 6 and 12 literals of
these two handlers; this prints all of them, and also the document itself, so the decision about a host rests on
everything the functions carry rather than on a prefix.
"""
import io
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

HANDLERS = {'a': 0x140B5F730, 'b': 0x140B62BC0}
DOCUMENT = 0x147146AB4
TEMP = os.environ.get('TEMP', '.')


def run(*args):
    return subprocess.run([sys.executable] + list(args), capture_output=True, text=True).stdout


print('document:')
sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402


def bytes_at(address, size):
    reply = call('get_bytes', {'regions': [{'addr': hex(address), 'size': size}]})
    if isinstance(reply, str):
        try:
            reply = json.loads(reply)
        except json.JSONDecodeError:
            reply = json.loads(reply.splitlines()[0])
    if isinstance(reply, dict):
        reply = reply.get('result', reply)
    region = reply[0] if isinstance(reply, list) else reply
    data = region['data']
    if isinstance(data, str):
        text = data[2:] if data.startswith('0x') else data
        return bytes(int(part, 16) for part in text.split())
    return bytes(data)


def read_string(chars_va):
    length = int.from_bytes(bytes_at(chars_va - 12, 12)[8:12], 'little')
    chunks, offset = [], 0
    while offset < length * 2:
        want = min(8192, length * 2 - offset)
        chunks.append(bytes_at(chars_va + offset, want))
        offset += want
    return b''.join(chunks).decode('utf-16-le', errors='replace')[:length]


text = read_string(DOCUMENT)
print(text)
print('declares: %s' % sorted(set(re.findall(r'\$(\w+)\s*:', text))))
print()

for label, address in HANDLERS.items():
    path = os.path.join(TEMP, 'r1369_%s.c' % label)
    run('analysis/dump_dec.py', hex(address), path)
    code = io.open(path, encoding='utf-8', errors='replace').read()
    offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', code)))
    decoded = run('analysis/names_at.py', *['0x' + o for o in offsets])
    strings = [line.split("'", 2)[1] for line in decoded.splitlines() if ' str ' in line and "'" in line]
    print('=== handler %s  %#x  %d lines  %d literals' % (label, address, len(code.splitlines()), len(strings)))
    for value in strings:
        print('    %s' % value[:120])
    print()
