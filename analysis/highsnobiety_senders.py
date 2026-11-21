"""Every Highsnobiety sender, found by the one string they all use.

The store's API host — https://tm-api-eu.highsnobiety.com/ at 0x147089690 — appears in eight code sites. That is
the whole of the store's HTTP surface, which is a better starting point than walking senders one document at a
time: one reference list, eight functions, and each function's literals say what it sends and with which
variables.

Note the address: the references point at the *character* address, not at the object header twelve bytes
earlier. Scanning the header offset finds nothing here, which is the §2.7d rule in reverse — try both before
concluding a string is unreferenced.

Usage: python analysis/highsnobiety_senders.py
"""
import os
import re
import subprocess
import sys

SITES = [
    0x140B56B86, 0x140B56EDE, 0x140B573A4, 0x140B5777A,
    0x140B58466, 0x140B587E3, 0x140B58C1D, 0x140B59D31,
]

TEMP = os.environ.get('TEMP', '.')


def run(args):
    return subprocess.run([sys.executable] + args, capture_output=True, text=True).stdout


functions = []
for site in SITES:
    out = run(['analysis/site_to_func.py', hex(site)])
    match = re.search(r'func (0x[0-9A-Fa-f]+)\.\.(0x[0-9A-Fa-f]+) \(size (\d+)\)', out)
    if not match:
        print('%#x -> no function' % site)
        continue
    functions.append((int(match.group(1), 16), int(match.group(3))))

unique = sorted(set(functions))
print('distinct functions: %d' % len(unique))
print()

for address, size in unique:
    path = os.path.join(TEMP, 'r1339_%x.c' % address)
    run(['analysis/dump_dec.py', hex(address), path])
    text = open(path, encoding='utf-8', errors='replace').read()
    offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', text)))
    decoded = run(['analysis/names_at.py'] + ['0x' + offset for offset in offsets]).splitlines()
    strings = [line.split("'", 2)[1] for line in decoded if ' str ' in line and "'" in line]
    print('%#x (%d bytes, %d literals)' % (address, size, len(strings)))
    print('   ' + ' | '.join(strings[:14]))
    print()
