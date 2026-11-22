"""R1376: the image does carry one Saucony url — who uses it, and what paths do they build?

SauconyFlow's refusal says "no literal in the image spells a Saucony API path". That was a conclusion from an earlier
round, and this round's job is to test it rather than inherit it: https://www.saucony.com is at 0x147099D1C and has four
referencers, so their literal tables are the place a path would appear.
"""
import io
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

CHARS = 0x147099D1C
TEMP = os.environ.get('TEMP', '.')


def run(*args):
    return subprocess.run([sys.executable] + list(args), capture_output=True, text=True).stdout


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


print('host string: %r' % read_string(CHARS))

sites = run('analysis/disp32_scan_any.py', hex(CHARS - 12))
found = sorted(set(re.findall(r'VA (0x[0-9A-Fa-f]{9})', sites)))
print('sites: %d' % len(found))

seen = set()
for site in found:
    mapped = run('analysis/site_to_func.py', site)
    function = re.search(r'func (0x[0-9A-Fa-f]+)', mapped)
    if not function:
        continue
    start = int(function.group(1), 16)
    if start in seen:
        continue
    seen.add(start)

    path = os.path.join(TEMP, 'r1376_%x.c' % start)
    run('analysis/dump_dec.py', hex(start), path)
    if not os.path.exists(path):
        continue
    code = io.open(path, encoding='utf-8', errors='replace').read()
    offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', code)))
    decoded = run('analysis/names_at.py', *['0x' + o for o in offsets])
    strings = [line.split("'", 2)[1] for line in decoded.splitlines()
               if ' str ' in line and "'" in line]
    carries = 'https://www.saucony.com' in strings
    print()
    print('%#x  %d literals  carries-host=%s' % (start, len(strings), carries))
    for value in strings[:20]:
        print('    %s' % value[:80])
