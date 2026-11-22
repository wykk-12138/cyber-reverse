"""R1374: the same method as R1373, applied to the surface endpoints.

For each candidate path: take the exact string, scan both address forms, map every site to its function, and decode that
function's literal table. A hit counts only if the function carries the path — R1372's rule.

This covers AO's three checkout bodies and the Saucony host, whose strings the image does carry
(https://www.saucony.com, SAUCONY-3DS, SauconyVariant).

Usage: python analysis/probe_surface_paths.py
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

TARGETS = [
    '/v2/app/contact', '/v2/app/delivery', '/v2/app/payment',
    'https://www.saucony.com', 'SAUCONY-3DS', 'SauconyVariant',
]
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


for target in TARGETS:
    listing = run('analysis/ida.py', 'str', target, '--limit', '20')
    try:
        matches = json.loads(listing).get('matches', [])
    except json.JSONDecodeError:
        print('%-26s listing unreadable' % target)
        continue

    exact = [m for m in matches if m.get('string') == target]
    print('=== %-26s exact=%d  total=%d' % (target, len(exact), len(matches)))
    if not exact:
        if matches:
            print('    near: %s' % ' | '.join(m['string'][:24] for m in matches[:4]))
        continue

    chars_va = int(exact[0]['addr'], 16)
    for form, tag in ((chars_va - 12, 'header'), (chars_va, 'chars')):
        sites = run('analysis/disp32_scan_any.py', hex(form))
        found = re.findall(r'VA (0x[0-9A-Fa-f]{9})', sites)
        for site in found[:4]:
            mapped = run('analysis/site_to_func.py', site)
            function = re.search(r'func (0x[0-9A-Fa-f]+)', mapped)
            if not function:
                continue
            start = int(function.group(1), 16)
            path = os.path.join(TEMP, 'r1374_%x.c' % start)
            run('analysis/dump_dec.py', hex(start), path)
            if not os.path.exists(path):
                continue
            code = io.open(path, encoding='utf-8', errors='replace').read()
            offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', code)))
            decoded = run('analysis/names_at.py', *['0x' + o for o in offsets])
            strings = [line.split("'", 2)[1] for line in decoded.splitlines()
                       if ' str ' in line and "'" in line]
            carries = target in strings
            print('    %s %#x -> %#x  %d literals  carries=%s' % (tag, form, start, len(strings), carries))
            if carries:
                print('        %s' % ' | '.join(s[:30] for s in strings[:16]))
    print()
