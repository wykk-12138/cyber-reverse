"""Full literal list for the two senders this round will implement."""

import os
import re
import subprocess
import sys

TARGETS = {
    'fetchProduct': 0x140B57020,
    'setCustomerEmail': 0x140B58920,
}

TEMP = os.environ.get('TEMP', '.')


def run(args):
    return subprocess.run([sys.executable] + args, capture_output=True, text=True).stdout


for name, address in TARGETS.items():
    path = os.path.join(TEMP, 'r1339t_%x.c' % address)
    run(['analysis/dump_dec.py', hex(address), path])
    text = open(path, encoding='utf-8', errors='replace').read()
    offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', text)))
    print('=== %s  %#x  %d literal offsets' % (name, address, len(offsets)))
    for line in run(['analysis/names_at.py'] + ['0x' + offset for offset in offsets]).splitlines():
        match = re.search(r'^0x([0-9A-F]+)\s+str .*len=(\d+)\s+(.*)$', line.strip())
        if not match:
            continue
        length = int(match.group(2))
        preview = match.group(3)
        print('   %#x  len=%-6d %s' % (int(match.group(1), 16), length, preview[:80]))
    print()
