"""Decompile a function, pull out its frozen-string constants, and decode them in one step.

Why this and not the existing tools on their own: `ida.py dec` gives control flow with `&off_146xxxxxx`
operands, and `names_at.py` decodes those addresses, but stringing them by hand means transcribing hex
addresses between two commands for every function. This runs the two in sequence and prints the mapping.

Usage:
    python analysis/func_strings.py 0x141144C20 [--lines 400]

Reads only; never writes to the IDB.
"""
import json
import re
import subprocess
import sys


def run(args):
    out = subprocess.run([sys.executable, 'analysis/ida.py'] + args,
                         capture_output=True, text=True, encoding='utf-8', errors='replace')
    return json.JSONDecoder().raw_decode(out.stdout)[0]


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    addr = argv[0]
    lines = '400'
    if '--lines' in argv:
        lines = argv[argv.index('--lines') + 1]

    doc = run(['dec', addr, '--lines', lines])
    code = doc.get('code') or ''
    if not code.strip():
        print('no pseudocode for', addr)
        return 1

    consts = sorted(set(re.findall(r'off_([0-9A-Fa-f]{9,})', code)))
    print('function %s: %d lines, %d distinct frozen constants' % (addr, len(code.split('\n')), len(consts)))
    if not consts:
        return 0

    names = run(['py', 'print("")'])  # warm-up not needed; go straight to names_at
    del names
    out = subprocess.run([sys.executable, 'analysis/names_at.py'] + ['0x' + c for c in consts],
                         capture_output=True, text=True, encoding='utf-8', errors='replace')
    decoded = []
    for line in (out.stdout or '').split('\n'):
        s = line.strip()
        if s.startswith('0x') and ' str ' in s:
            decoded.append(s)
            # keep the decoded text verbatim; console rendering of non-ASCII is a display concern
            print('  ' + s[:150])

    # R1213: say up front whether the replica already has this. Two rounds in a row the decode landed on
    # work R1088-R1094 had already done, and I only found out afterwards by grepping a field name by hand -
    # the check belongs before the decode, and it is cheap enough to run automatically from here on.
    try:
        import os
        import glob
        names = []
        for s in decoded:
            m = re.search(r"'([^']{4,60})'$", s)
            if m:
                names.append(m.group(1))
        hits = {}
        for path in glob.glob('replica/src/**/*.cs', recursive=True) + glob.glob('replica/tests/**/*.cs', recursive=True):
            try:
                text = open(path, encoding='utf-8', errors='replace').read()
            except OSError:
                continue
            for n in names:
                if n in text:
                    hits.setdefault(n, os.path.relpath(path))
        if hits:
            print('\nALREADY IN THE REPLICA (%d of %d decoded strings):' % (len(hits), len(names)))
            for n, p in sorted(hits.items())[:20]:
                print('  %-52s %s' % (n[:52], p))
        else:
            print('\nnone of the decoded strings appear in replica/src or replica/tests')
    except Exception as e:  # never let the convenience check hide the decode itself
        print('\nreplica cross-check unavailable: %s' % e)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
