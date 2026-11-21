"""When the document's function has no literals, follow the operation name instead.

All five functions in the two blocks decompile to state machines with zero inline strings, so the host cannot be
reached from the document side. The operation name, though, is a string of its own, and anything that references it
— a step table, a log call, a dispatch switch — is a different function that may well carry the host.

Usage: python analysis/operation_name_xrefs.py <OperationName>
"""
import io
import os
import re
import subprocess
import sys

NAME = sys.argv[1] if len(sys.argv) > 1 else 'CartLineItemSet'
TEMP = os.environ.get('TEMP', '.')


def run(*args):
    return subprocess.run([sys.executable] + list(args), capture_output=True, text=True).stdout


listing = run('analysis/ida.py', 'str', NAME, '--limit', '6')
print(listing.strip()[:600])
print()

addresses = re.findall(r'(0x14[0-9A-Fa-f]{8})', listing)
seen = set()
for chars_va in addresses:
    value = int(chars_va, 16)
    for form, label in ((value - 12, 'header'), (value, 'chars')):
        sites = run('analysis/disp32_scan_any.py', hex(form))
        for site in re.findall(r'VA (0x[0-9A-Fa-f]{9})', sites):
            if site in seen:
                continue
            seen.add(site)
            info = run('analysis/site_to_func.py', site)
            function = re.search(r'func (0x[0-9A-Fa-f]+)', info)
            print('%s  site %s (%s form) -> %s' % (NAME, site, label,
                                                   function.group(1) if function else 'no function'))
            if not function:
                continue
            start = int(function.group(1), 16)
            path = os.path.join(TEMP, 'r1355_name_%x.c' % start)
            run('analysis/dump_dec.py', hex(start), path)
            if not os.path.exists(path):
                continue
            text = io.open(path, encoding='utf-8', errors='replace').read()
            offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', text)))
            decoded = run('analysis/names_at.py', *['0x' + o for o in offsets])
            strings = [line.split("'", 2)[1] for line in decoded.splitlines() if ' str ' in line and "'" in line]
            hosts = [s for s in strings if 'http' in s or s.endswith('graphql.json')]
            print('    %d literals; hosts=%s' % (len(strings), hosts[:2]))
            if strings:
                print('    %s' % ' | '.join(strings[:10]))
