"""R1374b: the AO checkout URLs are full strings, so their senders can be read the R1373 way.

    https://checkout.ao.com/v2/app/contact    0x14705D114
    https://checkout.ao.com/v2/app/delivery   0x14705D17C
    https://checkout.ao.com/v2/app/payment    0x14705D1E4

For each: scan both address forms, map sites to functions, and decode the function's literal table. If a function
carries the URL, its other literals are the body's field names — which is exactly what the open list calls "the three
AO bodies".
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

TARGETS = {
    'contact': 0x14705D114,
    'delivery': 0x14705D17C,
    'payment': 0x14705D1E4,
}
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


for name, chars_va in TARGETS.items():
    url = read_string(chars_va)
    print('=== %s  %#x  %r' % (name, chars_va, url))

    for form, tag in ((chars_va - 12, 'header'), (chars_va, 'chars')):
        sites = run('analysis/disp32_scan_any.py', hex(form))
        found = re.findall(r'VA (0x[0-9A-Fa-f]{9})', sites)
        for site in found[:4]:
            mapped = run('analysis/site_to_func.py', site)
            function = re.search(r'func (0x[0-9A-Fa-f]+)', mapped)
            if not function:
                continue
            start = int(function.group(1), 16)
            path = os.path.join(TEMP, 'r1374b_%x.c' % start)
            run('analysis/dump_dec.py', hex(start), path)
            if not os.path.exists(path):
                continue
            code = io.open(path, encoding='utf-8', errors='replace').read()
            offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', code)))
            decoded = run('analysis/names_at.py', *['0x' + o for o in offsets])
            strings = [line.split("'", 2)[1] for line in decoded.splitlines()
                       if ' str ' in line and "'" in line]
            carries = url in strings
            print('    %s %#x -> %#x  %d literals  carries=%s' % (tag, form, start, len(strings), carries))
            if carries:
                print('        %s' % ' | '.join(s[:34] for s in strings[:20]))
    print()
