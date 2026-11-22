"""R1373: who sends /cartApi/checkout? The path is a literal; the sender should reference it.

R1372's rule applies here: a disp32 hit is not a reference until the function's literal table contains the name. So this
finds the string, scans both address forms, maps every site to its function, and decodes each function's literal set —
if a hit's function does not carry the path in its literals, the hit is noise.

Usage: python analysis/probe_cart_api_checkout.py
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

TARGET = '/cartApi/checkout'
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


listing = json.loads(run('analysis/ida.py', 'str', TARGET, '--limit', '20'))
matches = [m for m in listing.get('matches', []) if m.get('string') == TARGET]
print('exact matches for %r: %d' % (TARGET, len(matches)))
if not matches:
    raise SystemExit('no exact string')

chars_va = int(matches[0]['addr'], 16)
print('chars_va %#x  text %r' % (chars_va, read_string(chars_va)))

for form, tag in ((chars_va - 12, 'header'), (chars_va, 'chars')):
    sites = run('analysis/disp32_scan_any.py', hex(form))
    found = [s for s in re.findall(r'VA (0x[0-9A-Fa-f]{9})', sites)]
    print()
    print('%s %#x -> %d site(s)' % (tag, form, len(found)))
    for site in found[:6]:
        mapped = run('analysis/site_to_func.py', site)
        function = re.search(r'func (0x[0-9A-Fa-f]+)', mapped)
        if not function:
            print('   %s  (no function)' % site)
            continue
        start = int(function.group(1), 16)
        path = os.path.join(TEMP, 'r1373_%x.c' % start)
        run('analysis/dump_dec.py', hex(start), path)
        if not os.path.exists(path):
            print('   %s -> %#x  no pseudocode' % (site, start))
            continue
        code = io.open(path, encoding='utf-8', errors='replace').read()
        offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', code)))
        decoded = run('analysis/names_at.py', *['0x' + o for o in offsets])
        strings = [line.split("'", 2)[1] for line in decoded.splitlines()
                   if ' str ' in line and "'" in line]
        carries = TARGET in strings
        print('   %s -> %#x  %d literals  carries-the-path=%s' % (site, start, len(strings), carries))
        if carries:
            print('        %s' % ' | '.join(s[:32] for s in strings[:18]))
