"""R1368: two corrections and whatever the handlers say.

R1358 concluded getShippingMethods had no standalone operation-name string. It does — 0x14703FA94 — and the earlier
search simply returned eight PascalCase closure names first and stopped. CreditCard's is at 0x146BA9704. That is a
reminder worth keeping: a limited search that returns only near-matches is not evidence of absence.

This reads the handlers both names point at, looking for a host or a path.
"""
import io
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

HANDLERS = {
    'getShippingMethods/a': 0x140B5F730,
    'getShippingMethods/b': 0x140B62BC0,
    'CreditCard/a': 0x140AAE300,
    'CreditCard/b': 0x140B29DA7,
}
TEMP = os.environ.get('TEMP', '.')


def run(*args):
    return subprocess.run([sys.executable] + list(args), capture_output=True, text=True).stdout


for label, address in HANDLERS.items():
    path = os.path.join(TEMP, 'r1368_%s.c' % label.replace('/', '_'))
    run('analysis/dump_dec.py', hex(address), path)
    if not os.path.exists(path):
        print('%-24s %#x  no pseudocode' % (label, address))
        continue
    text = io.open(path, encoding='utf-8', errors='replace').read()
    offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', text)))
    decoded = run('analysis/names_at.py', *['0x' + o for o in offsets])
    strings = [line.split("'", 2)[1] for line in decoded.splitlines() if ' str ' in line and "'" in line]
    hosts = [s for s in strings if 'http' in s or s.endswith('graphql') or s == 'api/graphql']
    print('%-24s %#x  %3d literals  hosts=%s' % (label, address, len(strings), hosts[:3]))
    print('     %s' % ' | '.join(s[:44] for s in strings[:12]))
