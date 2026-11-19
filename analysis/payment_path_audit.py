"""Audit every path-shaped literal in the payment layer against the image.

R1246 checked hosts one at a time and found that one of them, api.omise.co, has no hit at all while six do. That is
a claim about a single constant; this asks the same question of every path the payment code builds, so the answer is
a list rather than an anecdote.

A literal counts as attested when `ida.py str` finds it, which searches the database itself rather than the pool file
that R816 showed to be a sample. Absence is reported as "no hit", never as "the image does not use it": a path can be
assembled from fragments, and R1245 showed two builders differing only in a version value.
"""
import glob
import io
import json
import re
import subprocess
import sys

PATH_LITERAL = re.compile(r'"((?:/[a-z0-9]|[a-z0-9]+/)[^"\\]{3,})"', re.I)


def ida_str(pattern, limit=3):
    out = subprocess.run([sys.executable, 'analysis/ida.py', 'str', pattern, '--limit', str(limit)],
                         capture_output=True, text=True, encoding='utf-8', errors='replace')
    try:
        return json.JSONDecoder().raw_decode(out.stdout)[0]
    except Exception:
        return {'n': 0, 'matches': []}


def main():
    found = {}
    for path in glob.glob('replica/src/Cybersole.Stores/Payments/*.cs'):
        raw = io.open(path, encoding='utf-8', errors='replace').read()
        # R1247: comment lines produced a bogus literal ("jgc/v8/client is recorded and never called: no"), so the
        # audit reads code lines only. A path inside a comment is documentation, not something the code requests.
        text = '\n'.join(l for l in raw.split('\n') if not l.lstrip().startswith('//'))
        for m in PATH_LITERAL.finditer(text):
            lit = m.group(1)
            if len(lit) < 6 or lit.startswith('//'):
                continue
            found.setdefault(lit, os_basename(path))

    print('path-shaped literals in the payment layer: %d' % len(found))
    attested, unattested = [], []
    for lit in sorted(found):
        d = ida_str(lit)
        (attested if d.get('n') else unattested).append((lit, found[lit], d.get('n', 0)))

    print('  attested in the image : %d' % len(attested))
    print('  no hit                : %d' % len(unattested))

    out = 'analysis/payment_path_audit.txt'
    with io.open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('# Every path-shaped literal in replica/src/Cybersole.Stores/Payments/*.cs, probed with\n')
        f.write('# `ida.py str` (the database, not the pool sample). "no hit" means the literal was not found; it\n')
        f.write('# does NOT mean the image lacks the route, since a path can be assembled from fragments (R1245).\n')
        f.write('# Regenerate with: python analysis/payment_path_audit.py\n\n')
        f.write('# ATTESTED (%d)\n' % len(attested))
        for lit, src, n in attested:
            f.write('%-52s\t%s\t%d\n' % (lit, src, n))
        f.write('\n# NO HIT (%d)\n' % len(unattested))
        for lit, src, _n in unattested:
            f.write('%-52s\t%s\n' % (lit, src))

    print('\nfirst 25 with no hit:')
    for lit, src, _n in unattested[:25]:
        print('   %-46s %s' % (lit[:46], src))
    print('\nwrote', out)
    return 0


def os_basename(path):
    return path.replace('\\', '/').split('/')[-1]


if __name__ == '__main__':
    sys.exit(main())
