"""R1370: the two approveMemberPayment dialects — what distinguishes their senders?

The documents are 5407 and 5620 characters at 0x1470E9FA4 and 0x1470EC9FC, and which one a run picks was never
established. A dialect is usually chosen by data, so the discriminator should be visible as a difference in what each
sender names or declares: one might take a member id, the other an email, one might carry a guest flag. This reads
both senders' literals and both documents' declared variables, and prints the difference rather than either side alone.
"""
import io
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

DOCUMENTS = {'short(5407)': 0x1470E9FA4, 'long(5620)': 0x1470EC9FC}
TEMP = os.environ.get('TEMP', '.')
sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402


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


info = {}
for label, address in DOCUMENTS.items():
    text = read_string(address)
    declared = sorted(set(re.findall(r'\$(\w+)\s*:', text)))
    fields = sorted(set(re.findall(r'^\s{0,6}(\w+)\s*$', text, re.M)))
    info[label] = {'text': text, 'declared': declared, 'fields': set(f for f in fields if len(f) > 3)}
    print('%-12s %d chars  declares %s' % (label, len(text), declared))

short, long_ = info['short(5407)'], info['long(5620)']
print()
print('fields only in the short document: %s' % sorted(short['fields'] - long_['fields'])[:12])
print('fields only in the long document : %s' % sorted(long_['fields'] - short['fields'])[:12])

for label, address in DOCUMENTS.items():
    for form, tag in ((address - 12, 'header'), (address, 'chars')):
        sites = run('analysis/disp32_scan_any.py', hex(form))
        found = re.findall(r'VA (0x[0-9A-Fa-f]{9})', sites)
        for site in found[:2]:
            mapped = run('analysis/site_to_func.py', site)
            function = re.search(r'func (0x[0-9A-Fa-f]+)', mapped)
            if not function:
                continue
            start = int(function.group(1), 16)
            path = os.path.join(TEMP, 'r1370.c')
            run('analysis/dump_dec.py', hex(start), path)
            code = io.open(path, encoding='utf-8', errors='replace').read()
            offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', code)))
            decoded = run('analysis/names_at.py', *['0x' + o for o in offsets])
            strings = [line.split("'", 2)[1] for line in decoded.splitlines()
                       if ' str ' in line and "'" in line]
            print()
            print('%s %s -> %#x  %d literals' % (label, tag, start, len(strings)))
            print('   %s' % ' | '.join(s[:34] for s in strings[:18]))
