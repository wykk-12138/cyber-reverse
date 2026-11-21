"""Apply R1355's probe to two more operations: follow the name, read the handler.

R1355 found that when a document's own function is a bare state machine, the operation name's referencer is the
function that reacts to the reply — and that function carries the vocabulary a document cannot. This runs the same
probe for CreditCard (2867 characters) and placeOrderWithPaypal (843).

Usage: python analysis/name_then_handler.py CreditCard placeOrderWithPaypal
"""
import io
import json
import os
import re
import subprocess
import sys

NAMES = sys.argv[1:] or ['CreditCard', 'placeOrderWithPaypal']
TEMP = os.environ.get('TEMP', '.')


def run(*args):
    return subprocess.run([sys.executable] + list(args), capture_output=True, text=True).stdout


for name in NAMES:
    listing = run('analysis/ida.py', 'str', name, '--limit', '8')
    print('=== %s' % name)
    try:
        payload = json.loads(listing)
    except json.JSONDecodeError:
        print('   could not parse the listing')
        continue

    for match in payload.get('matches', [])[:6]:
        text = match.get('string', '')
        address = int(match['addr'], 16)
        short = text[:60].replace('\n', ' ').replace('\r', '')
        print('   %s  %4d chars  %s' % (match['addr'], len(text), short))

        # A document is long and starts with mutation/query; the name itself is short.
        if len(text) > 100 or text.startswith(('mutation', 'query')):
            continue

        for form, label in ((address - 12, 'header'), (address, 'chars')):
            sites = run('analysis/disp32_scan_any.py', hex(form))
            for site in re.findall(r'VA (0x[0-9A-Fa-f]{9})', sites):
                info = run('analysis/site_to_func.py', site)
                function = re.search(r'func (0x[0-9A-Fa-f]+)', info)
                if not function:
                    continue
                start = int(function.group(1), 16)
                path = os.path.join(TEMP, 'r1356_%x.c' % start)
                run('analysis/dump_dec.py', hex(start), path)
                if not os.path.exists(path):
                    continue
                code = io.open(path, encoding='utf-8', errors='replace').read()
                offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', code)))
                decoded = run('analysis/names_at.py', *['0x' + o for o in offsets])
                strings = [line.split("'", 2)[1] for line in decoded.splitlines()
                           if ' str ' in line and "'" in line]
                hosts = [s for s in strings if 'http' in s or s.endswith('graphql.json')]
                print('      %s form -> %#x (%s)  hosts=%s' % (label, start, site, hosts[:2]))
                for value in strings[:14]:
                    print('         %s' % value[:100])
    print()
