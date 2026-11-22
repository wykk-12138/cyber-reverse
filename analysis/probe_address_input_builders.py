"""R1378: find the function that actually builds an AddressInput, using the literal-table rule.

R1372 established the four field names but had to withdraw the claim that three of them were referenced, because a
disp32 hit is not a reference until the function's own literal table contains the name. This applies that rule to all
four names: scan both address forms, map every site to a function, decode that function's literals, and report only the
sites whose function really carries the name.
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

NAMES = {
    'recipientName': 0x147149A94,
    'addressLine1': 0x146F6EC6C,
    'addressLine2': 0x146F6EC9C,
    'locality': 0x146FC9846,
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


confirmed = {}
for name, chars_va in NAMES.items():
    print('=== %s  chars_va %#x  text %r' % (name, chars_va, read_string(chars_va)))

    for form, tag in ((chars_va - 12, 'header'), (chars_va, 'chars')):
        sites = run('analysis/disp32_scan_any.py', hex(form))
        found = sorted(set(re.findall(r'VA (0x[0-9A-Fa-f]{9})', sites)))
        for site in found:
            if int(site, 16) < 0x140000000:
                continue
            mapped = run('analysis/site_to_func.py', site)
            function = re.search(r'func (0x[0-9A-Fa-f]+)', mapped)
            if not function:
                continue
            start = int(function.group(1), 16)
            path = os.path.join(TEMP, 'r1378_%x.c' % start)
            run('analysis/dump_dec.py', hex(start), path)
            if not os.path.exists(path):
                continue
            code = io.open(path, encoding='utf-8', errors='replace').read()
            offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', code)))
            decoded = run('analysis/names_at.py', *['0x' + o for o in offsets])
            strings = [line.split("'", 2)[1] for line in decoded.splitlines()
                       if ' str ' in line and "'" in line]
            if name in strings:
                confirmed.setdefault(start, []).append(name)
                print('    CONFIRMED %s %#x -> %#x  %d literals' % (tag, form, start, len(strings)))
    print()

print('functions whose literal table carries at least two address names:')
for start, names in sorted(confirmed.items()):
    if len(set(names)) >= 2:
        print('    %#x  %s' % (start, sorted(set(names))))
