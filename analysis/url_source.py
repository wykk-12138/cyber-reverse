"""Where does a host-less sender get its URL? Read the code that builds the request.

Five of the six unattributed senders sit in one address range — 0x140E55xxx to 0x140E5Axxx — which suggests one
family whose URL arrives as a parameter or from a shared config rather than as a literal in each function.

This dumps getCart's pseudocode and prints the region around the request construction, so the source of the URL is
visible rather than guessed.
"""

import io
import os
import re
import subprocess
import sys

FUNCTIONS = {
    'getCart': 0x140E55F90,
    'createMyPayment': 0x140E55A00,
    'initiateCheckout': 0x140E563C0,
}
TEMP = os.environ.get('TEMP', '.')

for label, address in FUNCTIONS.items():
    path = os.path.join(TEMP, 'r1353_%s.c' % label)
    subprocess.run([sys.executable, 'analysis/dump_dec.py', hex(address), path],
                   capture_output=True, text=True)
    text = io.open(path, encoding='utf-8', errors='replace').read()
    lines = text.splitlines()
    print('=== %s  %#x  (%d lines)' % (label, address, len(lines)))

    # The signature line and the first few lines show how arguments are used.
    for line in lines[:6]:
        print('   ' + line.strip()[:150])

    # Any string-building or URL-shaped argument usage.
    interesting = [l.strip() for l in lines
                   if re.search(r'(a\d|v\d+)\s*\+|strcat|sub_141DC7|Uri|url|Url|host|Host', l)]
    for line in interesting[:8]:
        print('    | ' + line[:150])
    print()
