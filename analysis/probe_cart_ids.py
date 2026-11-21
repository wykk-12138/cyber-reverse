"""Three cart-id extractors the image has and the replica does not: what do they read?

GetCartId, GetCartCsrf and GetCartItemId are store-family async names in the tail (analysis/async_tail.py). They are
worth decompiling before deciding anything: if they parse a cart response the replica already receives, the behaviour
is recoverable, and the step becomes a real one rather than a name.

Usage: python analysis/probe_cart_ids.py
"""
import io
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

NAMES = ['GetCartId', 'GetCartCsrf', 'GetCartItemId']
TEMP = os.environ.get('TEMP', '.')


def run(*args):
    return subprocess.run([sys.executable] + list(args), capture_output=True, text=True).stdout


for name in NAMES:
    listing = run('analysis/ida.py', 'str', name, '--limit', '5')
    print('=== %s' % name)
    try:
        payload = json.loads(listing)
    except json.JSONDecodeError:
        print('    listing unreadable')
        continue

    for match in payload.get('matches', [])[:3]:
        text = match.get('string', '')
        if len(text) > 80:
            continue
        address = int(match['addr'], 16)
        for form, label in ((address - 12, 'header'), (address, 'chars')):
            sites = run('analysis/disp32_scan_any.py', hex(form))
            for site in re.findall(r'VA (0x[0-9A-Fa-f]{9})', sites)[:1]:
                info = run('analysis/site_to_func.py', site)
                function = re.search(r'func (0x[0-9A-Fa-f]+)', info)
                if not function:
                    continue
                start = int(function.group(1), 16)
                path = os.path.join(TEMP, 'r1366_%s.c' % name)
                run('analysis/dump_dec.py', hex(start), path)
                if not os.path.exists(path):
                    continue
                code = io.open(path, encoding='utf-8', errors='replace').read()
                offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', code)))
                decoded = run('analysis/names_at.py', *['0x' + o for o in offsets])
                strings = [line.split("'", 2)[1] for line in decoded.splitlines()
                           if ' str ' in line and "'" in line]
                print('    %s -> %#x  %d lines, literals: %s' % (label, start, len(code.splitlines()),
                                                                 ' | '.join(s[:40] for s in strings[:10])))
                break
    print()
